# Generated by Django 4.2.7 on 2025-07-15 07:59

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventmgmt', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'ordering': ['-booking_date']},
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['date', 'time']},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-review_date']},
        ),
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['price']},
        ),
        migrations.AddField(
            model_name='booking',
            name='booking_reference',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 7, 15, 7, 54, 57, 617163, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='event',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 7, 15, 7, 56, 43, 957181, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='event_images/'),
        ),
        migrations.AddField(
            model_name='event',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Confirmed', 'Confirmed'), ('Pending', 'Pending'), ('Cancelled', 'Cancelled'), ('Refunded', 'Refunded')], default='Confirmed', max_length=20),
        ),
        migrations.AlterField(
            model_name='booking',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='eventmgmt.ticket'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('technology', 'Technology'), ('music', 'Music'), ('business', 'Business'), ('art', 'Art'), ('food', 'Food'), ('sports', 'Sports'), ('education', 'Education'), ('health', 'Health')], max_length=50),
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed'), ('Draft', 'Draft')], default='Active', max_length=20),
        ),
        migrations.AlterField(
            model_name='review',
            name='booking',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review', to='eventmgmt.booking'),
        ),
        migrations.AlterField(
            model_name='review',
            name='comment',
            field=models.TextField(blank=True, default='No comment'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')]),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='eventmgmt.event'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='ticket_type',
            field=models.CharField(choices=[('General', 'General Admission'), ('VIP', 'VIP'), ('Premium', 'Premium'), ('Student', 'Student'), ('Early Bird', 'Early Bird'), ('Group', 'Group')], max_length=50),
        ),
    ]
