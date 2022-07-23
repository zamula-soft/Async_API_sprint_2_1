import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender='movies.Filmwork')
def attention(sender, instance, created, **kwargs):
    if created and instance.creation_date == datetime.date.today():
        print(f"Сегодня премьера {instance.title}! 🥳")
