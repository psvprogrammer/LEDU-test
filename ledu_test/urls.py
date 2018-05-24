"""ledu_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from datetime import datetime

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.urls import path

from ledu_test import views
from ledu_test.forms import CustomAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', login,
        {
            'template_name': 'ledu_test/login.html',
            'authentication_form': CustomAuthenticationForm,
            'extra_context':
                {
                    'title': 'Login, please',
                    'year': datetime.now().year,
                }
        }, name='login'),
    path('logout/', logout,
        {
            'next_page': '/login'
        }, name='logout'),

    path('sign-up/', views.SignUp.as_view(), name='sign_up'),
    path('account_activation_sent/', TemplateView.as_view(
            template_name='ledu_test/account_activation_sent.html'),
         name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
         views.activate, name='activate'),
    # path(r'activate/(<uidb64>[0-9A-Za-z_\-]+)/(<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
    #      views.activate, name='activate'),
    path('', TemplateView.as_view(template_name='ledu_test/home.html'),
         name='home'),

    path('projects/', cache_page(60 * 15)(views.ProjectList.as_view()), name='project-list'),
    path('project/add/', views.ProjectCreate.as_view(), name='project-add'),
    path('ajax/vote/', views.AddVote.as_view(), name='add-vote')
]
