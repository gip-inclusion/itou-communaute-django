from django.db.models.signals import ModelSignal


post_create = ModelSignal(use_caching=True)
