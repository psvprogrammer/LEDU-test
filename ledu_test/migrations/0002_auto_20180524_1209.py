# Generated by Django 2.0.5 on 2018-05-24 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ledu_test', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='rate',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vote',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='ledu_test.Project'),
        ),
    ]
