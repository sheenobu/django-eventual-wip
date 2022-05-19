# django-eventual-poc

this is a proof-of-concept deferred value calculations by serializing
query expressions and throwing them in a job queue.

I wanted to know how you would instrument the django ORM and whether
you could build 'smart' query expressions.

Example:

```
def got_vote(choice: Choice):
    choice.votes = F("votes") + 1
    choice.save()
    choice.refresh_from_db(fields=["votes"])
```

Can use 'eventual' just by wrapping our Expressions:

```

from eventual import Eventual

def got_vote(choice: Choice):
    choice.votes = Eventual(F("votes") + 1)
    choice.save()
```

What happens:

 * `Eventual(F("votes") + 1)` is serialized into a queue.
 * `F("votes") + 1` is calculated and stored into the votes field,
    but not written to the db.
      it can then be returned by your views as-if it was incremented.
 * The database write happens in your backend workers.

## Usage

Include `eventual` into `INSTALLED_APPS`.

Set config details:

```
EVENTUAL_ENABLED = True
EVENTUAL_JOB_ENGINE = 'myproject.tasks.JobEngine'
```

### Usage - Dramatiq:

Implement handler:

```
import dramatiq
import eventual

handler = dramatiq.actor(eventual.JobHandler())

class JobEngine:
    def queue(self, data: str):
        handler.send(data)
```



