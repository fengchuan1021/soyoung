# Generated by Django 4.0.1 on 2022-01-05 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grab', '0012_reviewer_usertyle'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reviewer',
            old_name='UserTyle',
            new_name='UserType',
        ),
    ]
