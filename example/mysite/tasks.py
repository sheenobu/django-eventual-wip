import dramatiq
import pickle
import eventual
import base64

from funcy.flow import retry


handler = dramatiq.actor(retry(tries=3)(eventual.JobHandler()))


class JobEngine:
    def queue(self, data: str):
        handler.send(data)
