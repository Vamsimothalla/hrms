# Generated by Django 3.2.6 on 2021-08-21 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrms', '0002_auto_20210802_1723'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='nuban',
            new_name='number',
        ),
        migrations.AlterField(
            model_name='employee',
            name='bank',
            field=models.CharField(default='Santander UK', max_length=25),
        ),
        migrations.AlterField(
            model_name='employee',
            name='emp_id',
            field=models.CharField(default='emp705', max_length=70),
        ),
        migrations.DeleteModel(
            name='Kin',
        ),
    ]
