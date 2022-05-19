from django.conf import settings as base_settings

from eventual.utils import import_string


class Defaults:
    EVENTUAL_ENABLED = True
    EVENTUAL_IGNORE_ON_DISABLED = False
    EVENTUAL_JOB_ENGINE = "eventual.job.NoOpJobEngine"
    EVENTUAL_JOB_SERIALIZER = "eventual.job.PickleJobSerializer"


class Settings(object):
    def __getattr__(self, name):
        res = getattr(base_settings, name, getattr(Defaults, name))
        if name in ["EVENTUAL_JOB_ENGINE", "EVENTUAL_JOB_SERIALIZER"]:
            res = import_string(res) if isinstance(res, str) else res

        # Save to dict to speed up next access, __getattr__ won't be called
        self.__dict__[name] = res
        return res


settings = Settings()
