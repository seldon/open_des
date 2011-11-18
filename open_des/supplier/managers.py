from django.db import models

class SupplierManager(models.Manager):
    def get_by_natural_key(self, uid):
        return self.get(uid=uid)
