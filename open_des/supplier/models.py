from django.db import models

from accounting.models import account_type, AccountingDescriptor  

from open_des.des.models import Subject

            
class Supplier(Subject):
    # a unique (database independent) ID (an ASCII string) for ``Supplier`` model instances
    uid = models.CharField()
    name = models.CharField(max_length=128, unique=True)
    
    accounting =  AccountingDescriptor(SupplierAccountingProxy)
    
    def setup_accounting(self):
        self.subject.init_accounting_system()
        system = self.accounting_system
        ## setup a base account hierarchy   
        # a generic asset-type account (a sort of "virtual wallet")        
        system.add_account(parent_path='/', name='wallet', kind=account_type.asset)  
        # a placeholder for organizing transactions representing GAS payments
        system.add_account(parent_path='/incomes', name='gas', kind=account_type.income, is_placeholder=True)


class Product(models.Model):
    name = models.CharField(max_length=128)
     

class SupplierStock(models.Model):
    supplier = models.ForeignKey(Supplier, related_name='stock_set')
    product = models.ForeignKey(Product, related_name='stock_set')
    price = CurrencyField()