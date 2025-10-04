"""
Celery beat schedule configuration.
"""

from celery.schedules import crontab

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'update-crypto-data-every-5-minutes': {
        'task': 'apps.crypto.tasks.update_crypto_data',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-data-daily': {
        'task': 'apps.crypto.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
