from django.db import models

class PersonManager(models.Manager):
    def get_by_natural_key(self, uid):
        return self.get(uid=uid)
