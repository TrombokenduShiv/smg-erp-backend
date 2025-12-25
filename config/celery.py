import os
from celery import Celery

# 1. Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. Create the Celery app
app = Celery('smg_portal')

# 3. Load config from Django settings (Using a namespace 'CELERY')
# This means in settings.py, all celery keys must start with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Auto-discover tasks in all installed apps
# (It looks for a 'tasks.py' file inside apps/hr, apps/operations, etc.)
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')