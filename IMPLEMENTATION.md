# implementation details

## queue+serialization

jobs are serialized and unserialized via `settings.EVENTUAL_JOB_SERIALIZER`
and written to queue via `settings.EVENTUAL_JOB_QUEUE`.

The queues built in the main repo:

 * None!

The serializers built into the main repo:

 * `eventual.job.PickleJobSerializer`

NOTE: its unclear whether you can do JSON serialization to Query expressions.

For now, you can't JSON serialize Job objects because they encode
the model metadata. We should be storing them as strings and
then loading the model dynamically via `django.apps`.

## sources

Much of the ORM instrumentation work was copied directly from
https://github.com/Suor/django-cacheops .

Tested on django 3.2.x .

parts derived directly from cacheops:
  * eventual/conf.py
  * eventual/manager.py
  * eventual/utils.py

custom parts:

  * eventual/signals.py
    pre-and-post save signals that handle Eventual expressions.
