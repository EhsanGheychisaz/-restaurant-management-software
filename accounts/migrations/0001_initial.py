# Generated by Django 4.0.2 on 2023-07-06 16:19

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_jalali.db.models
import django_resized.forms
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='bannerShip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
            ],
        ),
        migrations.CreateModel(
            name='complex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('state', models.IntegerField(choices=[(0, 'Isfahan')], default=0)),
                ('city', models.IntegerField(choices=[(0, 'Isfahan')], default=0)),
                ('neighborhood', models.TextField()),
                ('dark_mode', models.BooleanField(default=False, verbose_name='نمایش دارک منو')),
                ('customer_ordering', models.BooleanField(default=True, verbose_name='ثبت سفارش سمت مشتری')),
                ('address', models.TextField()),
                ('telephone', models.CharField(max_length=11)),
                ('logo', models.ImageField(null=True, upload_to=accounts.models.path_and_rename)),
                ('logo_tumbnail', django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format=None, keep_meta=True, null=True, quality=10, size=[515, 478], upload_to=accounts.models.path_and_rename)),
                ('color', models.CharField(default='009dad', max_length=16)),
                ('phoneNumber', models.CharField(max_length=14)),
                ('Slogan', models.CharField(max_length=64)),
                ('socialMedia', models.JSONField()),
                ('emergencyCall', models.CharField(max_length=14)),
                ('location', models.JSONField()),
                ('membership_type', models.CharField(choices=[('Premium', 'pre'), ('Free', 'free')], default='Free', max_length=12)),
                ('workTime', models.JSONField()),
                ('rate', models.JSONField(blank=True, default=accounts.models.get_default_complex_rate, null=True, verbose_name='امتیاز رستوران')),
                ('bio', models.TextField(blank=True, default='bio', null=True, verbose_name='بیوگرافی مجموعه')),
                ('website', models.URLField()),
                ('taxType', models.CharField(choices=[('item', 'item'), ('order', 'order')], default='item', max_length=12)),
                ('qrCode', models.ImageField(blank=True, null=True, upload_to=accounts.models.path_and_rename)),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ افتتاح حساب')),
                ('update_at', django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ آخرین تغییرات')),
            ],
        ),
        migrations.CreateModel(
            name='customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthDate', django_jalali.db.models.jDateField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('phoneNumber', models.CharField(max_length=14)),
                ('acceptedRules', models.BooleanField(default=False)),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('update_at', django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ آخرین آپدیت')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='customerClub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, null=True)),
                ('membership_type', models.CharField(choices=[('Premium', 'pre'), ('Ordinary', 'ordinary')], default='Ordinary', max_length=12)),
                ('complex', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.complex')),
            ],
        ),
        migrations.CreateModel(
            name='image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pic', models.ImageField(upload_to=accounts.models.path_and_rename, verbose_name='image')),
                ('pic_tumbnail', django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format=None, keep_meta=True, null=True, quality=100, size=[1000, 350], upload_to=accounts.models.path_and_rename)),
                ('title', models.CharField(default='تصویر', max_length=32, null=True)),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
            ],
        ),
        migrations.CreateModel(
            name='worker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phoneNumber', models.CharField(max_length=14)),
                ('roleName', models.CharField(blank=True, max_length=255, null=True, verbose_name='وظیفه')),
                ('permission', models.JSONField(blank=True, default=accounts.models.get_default_worker_permission, null=True, verbose_name='دسترسی ها')),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('update_at', django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ آخرین آپدیت')),
                ('complex', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.complex', verbose_name='محل کار')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='worker', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=False)),
                ('membership', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.customerclub')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.customer')),
            ],
        ),
        migrations.CreateModel(
            name='SystemLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('none', 'none'), ('Create', 'Create'), ('Update', 'Update'), ('Delete', 'Delete')], default='none', max_length=50)),
                ('level', models.CharField(choices=[('TRACE', '5'), ('DEBUG', '10'), ('INFO', '20'), ('SUCCESS', '25'), ('WARNING', '30'), ('ERROR', '40'), ('CRITICAL', '50')], default='TRACE', max_length=50)),
                ('message', models.TextField(blank=True, null=True)),
                ('model', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('complex', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='which_complex_log', to='accounts.complex')),
                ('worker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='which_worker_log', to='accounts.worker')),
            ],
        ),
        migrations.CreateModel(
            name='imageShip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('foodcomplex', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.complex')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.image')),
            ],
        ),
        migrations.AddField(
            model_name='complex',
            name='banner',
            field=models.ManyToManyField(blank=True, through='accounts.bannerShip', to='accounts.image', verbose_name='بنر ها'),
        ),
        migrations.AddField(
            model_name='complex',
            name='complexImage',
            field=models.ManyToManyField(blank=True, related_name='picture', through='accounts.imageShip', to='accounts.image'),
        ),
        migrations.AddField(
            model_name='complex',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bannership',
            name='banner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.image'),
        ),
        migrations.AddField(
            model_name='bannership',
            name='foodcomplex',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.complex'),
        ),
    ]