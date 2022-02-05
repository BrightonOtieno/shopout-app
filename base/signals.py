from django.db.models.signals import pre_save
from django.contrib.auth.models import User

# gets fired b4 obj is saved


def updateUser(sender, instance, **kwargs):
    #print('Signal Triggered')
    user = instance
    if user.email != '':
        user.username = user.email


pre_save.connect(updateUser, sender=User)
