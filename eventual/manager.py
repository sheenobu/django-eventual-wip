import sys

from funcy import (
    select_keys,
    cached_property,
    once,
    once_per,
    monkey,
    wraps,
    walk,
    chain,
)
from django.db.models.manager import BaseManager
from django.db.models.signals import pre_save, post_save


from eventual import Eventual, signals
from eventual.job import JobEngine, Job
from eventual.utils import monkey_mix
from eventual.conf import settings


def connect_first(signal, receiver, sender):
    old_receivers = signal.receivers
    signal.receivers = []
    signal.connect(receiver, sender=sender, weak=False)
    signal.receivers += old_receivers


class ManagerMixin(object):
    @once_per("cls")
    def _install_eventual(self, cls):
        # Set up signals
        connect_first(pre_save, self._pre_save, sender=cls)
        connect_first(post_save, self._post_save, sender=cls)

        # Install auto-created models as their module attributes to make them picklable
        module = sys.modules[cls.__module__]
        if not hasattr(module, cls.__name__):
            setattr(module, cls.__name__, cls)

        self.job_engine = settings.EVENTUAL_JOB_ENGINE()
        self.job_serializer = settings.EVENTUAL_JOB_SERIALIZER()

    # This is probably still needed if models are created dynamically
    def contribute_to_class(self, cls, name):
        self._no_monkey.contribute_to_class(self, cls, name)
        # Django migrations create lots of fake models, just skip them
        # NOTE: we make it here rather then inside _install_cacheops()
        #       because we don't want @once_per() to hold refs to all of them.
        if cls.__module__ != "__fake__":
            self._install_eventual(cls)

    def _pre_save(self, **kwargs):
        signals.pre_save(self, **kwargs)

    def _post_save(self, **kwargs):
        signals.post_save(self, **kwargs)


@once
def install_eventual():
    """
    Installs eventual by numerous monkey patches
    """
    monkey_mix(BaseManager, ManagerMixin)

    from django.apps import apps

    # Install profile and signal handlers for any earlier created models
    for model in apps.get_models(include_auto_created=True):
        if not isinstance(model._default_manager, BaseManager):
            raise ImproperlyConfigured(
                "Can't install eventual for %s.%s model:"
                " non-django model class or manager is used."
                % (model._meta.app_label, model._meta.model_name)
            )
        model._default_manager._install_eventual(model)
