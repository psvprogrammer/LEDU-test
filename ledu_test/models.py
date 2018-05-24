from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save_profile_update(sender, instance, created, *args, **kwargs):
    """Automatically creating profile for all newly created users.
    All registered users retrieve 15 possibilities to vote.
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    votes = models.IntegerField(default=15)


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    description = models.TextField(blank=True, default='')
    rate = models.FloatField(default=0.0)


class Vote(models.Model):
    user = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='votes')
    rate = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'project')
