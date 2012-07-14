from django.db import models

from accounting.models import account_type

from open_des.gas.models import GAS
from open_des.supplier.models import Supplier 


## GAS-Supplier interface
class SolidalPact(models.Model):
    gas = models.ForeignKey(GAS, related_name='pact_set')
    supplier = models.ForeignKey(Supplier, related_name='pact_set')
    
    def setup_accounting(self):
        ## create accounts for logging GAS <-> Supplier transactions
        # GAS-side
        gas_system = self.gas.subject.accounting_system
        gas_system.add_account(parent_path='/expenses/suppliers', name=self.supplier.uid, kind=account_type.expense)
        # Supplier-side
        supplier_system = self.supplier.subject.accounting_system
        supplier_system.add_account(parent_path='/incomes/gas', name=self.gas.uid, kind=account_type.income)