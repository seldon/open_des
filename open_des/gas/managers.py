from django.db import models

class GasManager(models.Manager):
    def get_by_natural_key(self, uid):
        return self.get(uid=uid)

class GasMemberManager(models.Manager):
    def get_by_natural_key(self, person, gas):
        return self.get(person=person, gas=gas)