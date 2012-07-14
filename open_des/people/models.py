from django.db import models

from accounting.models import account_type, AccountingDescriptor

from open_des.des.models import Subject 
  


@economic_subject
class Person(models.Model):
    # a unique (database independent) ID (an ASCII string) for ``GAS`` model instances
    uid = models.CharField()
    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)

    accounting =  AccountingDescriptor(PersonAccountingProxy)
    
    def setup_accounting(self):
        self.subject.init_accounting_system()
        system = self.accounting_system
        # create a generic asset-type account (a sort of "virtual wallet")
        system.add_account(parent_path='/', name='wallet', kind=account_type.asset)  
       
    def is_member(self, gas):
        """
        Return ``True`` if this person is member of GAS ``gas``, ``False`` otherwise. 
        
        If ``gas`` is not a ``GAS`` model instance, raise ``TypeError``.
        """
        from open_des.gas.models import GAS
         
        if not isinstance(self, GAS):
            raise TypeError(_(u"GAS membership can only be tested against a GAS model instance"))
        return gas in [member.gas for member in self.gas_memberships]        
    
    @property
    def full_name(self):
        return self.name + self.surname
    
    @property
    def gas_memberships(self):
        """
        The queryset of all incarnations of this person as a GAS member.
        """
        return self.gas_membership_set.all()