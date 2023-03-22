# Generated by Django 4.1.5 on 2023-03-22 13:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Event')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('event_date', models.DateTimeField(blank=True, null=True, verbose_name='Event Date')),
                ('token_dist_start', models.DateTimeField(blank=True, null=True, verbose_name='Token Distribution Start')),
                ('token_dist_end', models.DateTimeField(blank=True, null=True, verbose_name='Token Distribution End')),
                ('token_usage', models.IntegerField(default=0, verbose_name='Token Usage Limit')),
                ('distribution_place', models.CharField(blank=True, max_length=100, null=True, verbose_name='Distribution')),
                ('desc', models.TextField(blank=True, null=True, verbose_name='Description')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('token_serial', models.CharField(blank=True, max_length=20, null=True, verbose_name='Serial')),
                ('is_printed', models.BooleanField(default=False, verbose_name='Printed')),
                ('is_activated', models.BooleanField(default=False, verbose_name='Activated')),
                ('entry_flag', models.BooleanField(blank=True, default=False, null=True, verbose_name='Entry Status')),
                ('food_flag', models.BooleanField(blank=True, default=False, null=True, verbose_name='Food Status')),
                ('student_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Student Id')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tokens.event', verbose_name='Event')),
            ],
            options={
                'verbose_name_plural': 'Tokens',
            },
        ),
        migrations.CreateModel(
            name='StudentList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Student Id')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Name')),
                ('claimed', models.BooleanField(blank=True, default=False, null=True, verbose_name='Token Claimed')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tokens.event', verbose_name='Event')),
            ],
            options={
                'verbose_name_plural': 'Student List',
            },
        ),
    ]
