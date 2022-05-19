from eventual.conf import settings
from eventual.job import Job, Eventual


def pre_save(self, sender, instance, using, **kwargs):
    instance._eventual_fields = []
    for f in sender._meta.get_fields():
        if not hasattr(instance, f.name):
            continue
        v = getattr(instance, f.name)
        if isinstance(v, Eventual):
            if settings.EVENTUAL_ENABLED:
                delattr(instance, f.name)  # nuke the field
                v.name = f.name
                instance._eventual_fields += [v]
            elif settings.EVENTUAL_IGNORE_ON_DISABLED:
                # just unwrap and use the expression-as-is
                setattr(instance, v.expression)


def post_save(self, sender, instance, using, **kwargs):
    if not settings.EVENTUAL_ENABLED:
        return

    count = 0
    for e in instance._eventual_fields:
        new_value = list(
            sender.objects.filter(pk=instance.pk)
            .annotate(value=e.expression)
            .values_list("value")
        )
        setattr(instance, e.name, new_value[0][0])

    if len(instance._eventual_fields) > 0:
        self.job_engine.queue(
            self.job_serializer.serialize(
                Job(
                    model=sender,
                    pk=instance.pk,
                    eventuals=instance._eventual_fields,
                )
            )
        )

    delattr(instance, "_eventual_fields")
