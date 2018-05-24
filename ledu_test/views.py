from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db import DatabaseError
from django.db.models import prefetch_related_objects, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string, get_template
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse

from django_ajax.mixin import AJAXMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import (
    FormView,
    CreateView,
    UpdateView,
    DeleteView
)

from ledu_test.forms import SignUpForm
from ledu_test.models import (
    Profile,
    Project,
    User,
    Vote,
)


MAX_USER_VOTES = 15


class SignUp(FormView):
    template_name = 'ledu_test/sign_up.html'
    form_class = SignUpForm
    success_url = '/account_activation_sent/'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        activation_link = self.send_activation_email(user)
        self.request.session['link'] = activation_link
        return super().form_valid(form)

    def send_activation_email(self, user):
        site = get_current_site(self.request)
        use_https = True if self.request.is_secure() else False

        context = {
            'domain': site.domain,
            'site_name': site.name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }

        subject = 'Account activation link for ledu test'
        template = get_template('ledu_test/account_activation_email.html')
        html_context = template.render(context)
        from_email = 'admin@ledu-test.com'
        msg = EmailMessage(subject, html_context, from_email, [user.email, ])
        msg.content_subtype = 'html'
        try:
            msg.send()
            # user.email_user(subject, message)
        except Exception as why:
            print(str(why))
            print('activation message: \n{}'.format(html_context))
        return '{}://{}/activate/{}/{}/'.format(
            context['protocol'], context['domain'],
            context['uid'], context['token'])


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as why:
        user, error = None, str(why)

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'account_activation_invalid.html', {'error': error})


class ProjectCreate(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['title', 'description']
    template_name = 'ledu_test/project/project_form.html'
    success_url = '/projects/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UserIdentity:
    def identify_user(self, request):
        if request.user.is_authenticated:
            return request.user.username
        else:
            return request.META.get('REMOTE_ADDR', 'anonymous')


class ProjectList(ListView, UserIdentity):
    model = Project
    context_object_name = 'project_list'
    template_name = 'ledu_test/project/project_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        user = self.identify_user(self.request)
        projects = list(context.get('project_list'))
        project_list = []
        for project in projects:
            votes_count = project.votes.all().count()
            user_rate = project.votes.filter(user=user).first()
            if user_rate:
                user_rate = user_rate.rate

            # if votes_count:
            #     rate = sum(
            #         vote['rate'] for vote in project.votes.all().values('rate')
            #     ) / project.votes.all().count()
            # else:
            #     rate = '-'
            project_list.append({
                'id': project.id,
                'user': project.user,
                'title': project.title,
                'description': project.description,
                'rate': str(project.rate),
                'user_rate': user_rate,
            })
        context['project_list'] = project_list
        context['vote_range'] = range(1, 6)
        return context

    def get_queryset(self):
        sort = self.request.GET.get('sort')
        if sort and sort == 'asc':
            return Project.objects.all().prefetch_related('votes').order_by('rate')
        return Project.objects.all().prefetch_related('votes').order_by('-rate')


class AddVote(AJAXMixin, TemplateView, UserIdentity):

    def __init__(self):
        super().__init__()
        self.response = {}

    def post(self, request):
        user = self.identify_user(request)
        project = get_object_or_404(Project, id=request.POST.get('project_id'))
        try:
            rate = int(request.POST.get('rate'))
        except TypeError:
            self._fail_popover(msg='Wrong type error!')
            return self.response
        project_vote = Vote.objects.filter(user=user, project=project)
        user_votes = Vote.objects.filter(user=user).all().count()

        if project_vote.count() == 0:
            # add new vote
            if user_votes < MAX_USER_VOTES:
                project_vote = Vote(user=user, project=project, rate=rate)
                self._update_project(project, project_vote)
            else:
                self._fail_popover(msg="You have no quota to vote anymore!")
                return self.response
        else:
            # update existing rate
            project_vote = project_vote.first()
            if project_vote.rate != rate:
                project_vote.rate = rate
                self._update_project(project, project_vote)
            else:
                self._success_popover()

        return self.response

    def _update_project(self, project, project_vote):
        try:
            project_vote.save()
        except DatabaseError as why:
            self._fail_popover(msg=str(why))
            return
        else:
            rate = sum(
                vote['rate'] for vote in project.votes.all().values('rate')
            ) / project.votes.all().count()
            project.rate = rate
            project.save()
            self._success_popover()
            self.response.update({
                'inner-fragments': {
                    '#project_{}_rate'.format(project.id): str(rate),
                },
            })

    def _fail_popover(self, title='Error', msg='Internal server error'):
        popover = {
            'title': title,
            'content': msg,
            'template': render(self.request,
                               'ledu_test/popovers/popover_error.html'),
        }
        self.response.update({
            'success': False,
            'popover': popover,
        })

    def _success_popover(self, title='Success', msg='Your vote saved!'):
        popover = {
            'title': title,
            'content': msg,
            'template': render(self.request,
                               'ledu_test/popovers/popover_success.html'),
        }
        self.response.update({
            'success': True,
            'popover': popover,
        })

        # post = get_object_or_404(Vote, id=request.POST.get('post_id'))
        # comment = Comment(
        #     author=request.user, post=post,
        #     content=request.POST.get('content'))
        # comment.save()
        # return {
        #     'append-fragments': {
        #         '#comments': render(
        #             request, 'probegin_test/comment/comment.html',
        #             {'comment': comment}).content.decode().replace('\n', ''),
        #     },
        # }
