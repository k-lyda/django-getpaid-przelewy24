# Generated by Django 3.1.2 on 2020-10-09 03:55

import uuid

import django.db.models.deletion
import django_fsm
import getpaid.types
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('paywall', '0002_auto_20200419_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount_required', models.DecimalField(decimal_places=2, help_text='Amount required to fulfill the payment; in selected currency, normal notation', max_digits=20, verbose_name='amount required')),
                ('currency', models.CharField(max_length=3, verbose_name='currency')),
                ('status', django_fsm.FSMField(choices=[('new', 'new'), ('prepared', 'in progress'), ('pre-auth', 'pre-authed'), ('charge_started', 'charge process started'), ('partially_paid', 'partially paid'), ('paid', 'paid'), ('failed', 'failed'), ('refund_started', 'refund started'), ('refunded', 'refunded')], db_index=True, default=getpaid.types.PaymentStatus['NEW'], max_length=50, protected=True, verbose_name='status')),
                ('backend', models.CharField(db_index=True, max_length=100, verbose_name='backend')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created on')),
                ('last_payment_on', models.DateTimeField(blank=True, db_index=True, default=None, null=True, verbose_name='paid on')),
                ('amount_locked', models.DecimalField(decimal_places=2, default=0, help_text='Amount locked with this payment, ready to charge.', max_digits=20, verbose_name='amount paid')),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, help_text='Amount actually paid.', max_digits=20, verbose_name='amount paid')),
                ('refunded_on', models.DateTimeField(blank=True, db_index=True, default=None, null=True, verbose_name='refunded on')),
                ('amount_refunded', models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='amount refunded')),
                ('external_id', models.CharField(blank=True, db_index=True, default='', max_length=64, verbose_name='external id')),
                ('description', models.CharField(blank=True, default='', max_length=128, verbose_name='description')),
                ('fraud_status', django_fsm.FSMField(choices=[('unknown', 'unknown'), ('accepted', 'accepted'), ('rejected', 'rejected'), ('check', 'needs manual verification')], db_index=True, default=getpaid.types.FraudStatus['UNKNOWN'], max_length=20, protected=True, verbose_name='fraud status')),
                ('fraud_message', models.TextField(blank=True, verbose_name='fraud message')),
                ('url_return', models.CharField(db_index=True, max_length=256, verbose_name='url_return')),
                ('time_limit', models.IntegerField(default=0, verbose_name='time limit')),
                ('channel', models.IntegerField(verbose_name='payment channel')),
                ('wait_for_result', models.BooleanField(default=True, verbose_name='wait for result')),
                ('token', models.CharField(max_length=50, null=True, verbose_name='token')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='orders.order', verbose_name='order')),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'ordering': ['-created_on'],
                'abstract': False,
            },
            bases=(django_fsm.ConcurrentTransitionMixin, models.Model),
        ),
    ]