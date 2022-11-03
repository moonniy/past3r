import os
from datetime import timedelta
from django.utils import timezone

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'past3r.settings')
app = Celery('past3r')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, check_expiration.s(), name='validate_expiration')


@app.task
def check_expiration(*args, **kwargs):
    from app.models import Paste
    for paste in Paste.objects.filter(active=True).exclude(expiration='never'):
        if paste.expiration == '10_MINUTES' and paste.created + timedelta(minutes=10) <= timezone.now():
            print(f'ID {paste.id} - {paste.cid}')
            print('10 minutes')
            paste.active = False

        if paste.expiration == '1_HOUR' and paste.created + timedelta(hours=1) <= timezone.now():
            print(f'ID {paste.id} - {paste.cid}')
            print('1 HOUR')
            paste.active = False

        if paste.expiration == '1_DAY' and  paste.created + timedelta(hours=24) <= timezone.now():
            print(f'ID {paste.id} - {paste.cid}')
            print('1 Day')
            paste.active = False

        if paste.expiration == '1_WEEk' and paste.created + timedelta(days=7) <= timezone.now():
            print(f'ID {paste.id} - {paste.cid}')
            print('1 Week')
            paste.active = False

        if paste.expiration == '2_WEEk' and paste.created + timedelta(days=14) <= timezone.now():
            print(f'ID {paste.id} - {paste.cid}')
            print('2 Week')
            paste.active = False

        if paste.expiration == '1_MONTH' and paste.created + timedelta(days=30) <= timezone.now():
            print(f'ID {paste.id} - {paste.cid}')
            print('1 Month')
            paste.active = False

        if paste.expiration == '6_MONTH' and paste.created + timedelta(days=30 * 6) <= timezone.now():
            print(f'ID {paste.id} - {paste.cid}')
            print('6 Month')
            paste.active = False

        if paste.expiration == '1_YEAR' and paste.created + timedelta(days=365) <= timezone.now():
            print(f'ID {paste.id} - {paste.cid}')
            print('1 Year')
            paste.active = False

        paste.save()