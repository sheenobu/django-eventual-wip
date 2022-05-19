import base64
import pickle
from eventual.conf import settings


class Eventual:
    def __init__(self, expression):
        self.name = ""
        self.expression = expression


class Job:
    """
    A Job is a job that represents the update
    of a field 'eventually'.
    """

    def __init__(self, model, pk, eventuals):
        self.model = model
        self.pk = pk
        self.eventuals = eventuals


class JobEngine:
    """
    The job engine represents the function
    for queueing jobs.
    """

    def queue(self, data: str):
        raise NotImplemented


class JobSerializer:
    def serialize(self, job: Job) -> str:
        raise NotImplemented

    def unserialize(self, data: str) -> Job:
        raise NotImplemented


class PickleJobSerializer(JobSerializer):
    def serialize(self, job: Job) -> str:
        return base64.b64encode(pickle.dumps(job)).decode()

    def unserialize(self, data: str) -> Job:
        return pickle.loads(base64.b64decode(data))


class NoOpJobEngine(JobEngine):
    def queue(self, data: str):
        pass


class JobHandler:
    def __init__(self):
        self.job_serializer = settings.EVENTUAL_JOB_SERIALIZER()
        self.__name__ = "JobHandler"

    def __call__(self, data: str):
        job = self.job_serializer.unserialize(data)
        print(f"handling job {job.model} {job.pk}")
        instance = job.model.objects.get(pk=job.pk)
        attrs = {}
        for eventual in job.eventuals:
            attrs[eventual.name] = eventual.expression
        job.model.objects.filter(pk=job.pk).update(**attrs)
