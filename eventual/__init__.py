import django

if django.VERSION < (3, 2):
    default_app_config = "eventual.apps.EventualConfig"

from eventual.job import Eventual, Job, JobEngine, JobHandler
