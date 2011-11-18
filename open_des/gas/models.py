from django.db import models

from accounting.models import account_type, AccountingDescriptor, economic_subject, Account

from open_des.person.models import Person

@economic_subject
class Gas(models.Model):
    # a unique (database independent) ID (an ASCII string) for ``GAS`` model instances
    uid = models.CharField()
    name = models.CharField(max_length=128, unique=True)
    membership_fee = CurrencyField(null=True, blank=True)
    
    accounting =  AccountingDescriptor(GasAccountingProxy)

    def setup_accounting(self):
        self.subject.init_accounting_system()
        system = self.accounting_system
        ## setup a base account hierarchy
        # GAS's cash       
        system.add_account(parent_path='/', name='cash', kind=account_type.asset) 
        # root for GAS members' accounts 
        system.add_account(parent_path='/', name='members', kind=account_type.asset, is_placeholder=True)
        # a placeholder for organizing transactions representing payments to suppliers
        system.add_account(parent_path='/expenses', name='suppliers', kind=account_type.expense, is_placeholder=True)
        # recharges made by GAS members to their own account
        system.add_account(parent_path='/incomes', name='recharges', kind=account_type.income)
        # membership fees
        system.add_account(parent_path='/incomes', name='fees', kind=account_type.income)
        
    @property
    def pacts(self):
        """
        The queryset of all solidal pacts active for this GAS.
        """
        return self.pact_set.all()
    
    @property
    def suppliers(self):
        """
        The set of all suppliers which have signed a (currently active) solidal pact with this GAS.
        """
        suppliers = set([pact.supplier for pact in self.pacts])
        return suppliers 

    def natural_key(self):
        return self.uid
    

class GaSMember(models.Model):
    person = models.ForeignKey(Person, related_name='gas_membership_set')
    gas = models.ForeignKey(Gas)
    
    def setup_accounting(self):
        person_system = self.person.subject.accounting_system
        gas_system = self.gas.subject.accounting_system
        
        ## account creation
        ## Person-side
        # placeholder for payments made by this person to GASs (s)he belongs to
        try:
            person_system['/expenses/gas'] 
        except Account.DoesNotExist:
            person_system.add_account(parent_path='/expenses', name='gas', kind=account_type.expense, is_placeholder=True)
        # base account for expenses related to this GAS membership
        person_system.add_account(parent_path='/expenses/', name=self.gas.uid, kind=account_type.expense, is_placeholder=True)
        # recharges
        person_system.add_account(parent_path='/expenses/' + self.gas.uid, name='recharges', kind=account_type.expense)
        # membership fees
        person_system.add_account(parent_path='/expenses/' + self.gas.uid, name='fees', kind=account_type.expense)
        ## GAS-side   
        gas_system.add_account(parent_path='/members', name=self.member.uid, kind=account_type.asset)
    
    def natural_key(self):
        return [self.person, self.gas]
        
    @property
    def issued_orders(self):
        """
        The queryset of orders this member has issued against his/her GAS. 
        """
        return self.issued_order_set.all()