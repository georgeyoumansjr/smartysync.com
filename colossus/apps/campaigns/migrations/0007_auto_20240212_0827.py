# Generated by Django 2.2 on 2024-02-12 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0006_auto_20231111_0737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='mailing_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaigns', to='lists.MailingList', verbose_name='mailing list'),
        ),
    ]
