from django.db import models

class SolidalPactManager(models.Manager):
    def get_by_natural_key(self, gas, supplier):
        return self.get(gas=gas, supplier=supplier)

