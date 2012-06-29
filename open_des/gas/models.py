from django.db import models

from accounting.models import account_type, AccountingDescriptor, Account

from open_des.person.models import Person
from open_des.des.models import Subject
from open_des.gas.managers import GasReferrerManager



class Gas(Subject):
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
    
    def natural_key(self):
        return self.uid
            
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
    
    @property
    def members(self):
        """
        The queryset of current members for this GAS (as ``Person`` instances).
        """
        return GaSMember.current.filter(gas=self)
    
    @property
    def referrers(self):
        """
        The queryset of current referrers for this GAS (as ``Persons`` instances).
        """
        return GasReferrer.current.filter(gas=self)
    
    

class GaSMember(models.Model):
    """
    A relationship table modeling membership of a person into a given GAS.
    
    A person may be member of a given GAS for a period of time, then leave the group 
    and re-join the group an arbitrary number of times.  In order to reconstruct a member's
    history, the same ``member_id`` must be the assigned every time.
    """
    member_id = models.PositiveSmallIntegerField()
    person = models.ForeignKey(Person, related_name='gas_membership_set')
    gas = models.ForeignKey(Gas)
    # when the membership started
    start_date = models.DateField()
    # when the membership ended (if so)
    end_date = models.DateField(blank=True, null=True)
    
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
    
    
class GasReferrer(models.Model):
    """
    A relationship table mapping the fact that a person is a referrer for a given GAS.
    
    This role is assigned within a time-frame; so, we are able to answer questions such as:
        
        "Who was the referrer for GAS XYZ at a given date in the past ?"
          
    """
    person = models.ForeignKey(Person, related_name='gas_referrer_role_set')
    gas = models.ForeignKey(Gas)
    # when the membership started
    start_date = models.DateField()
    # when the membership ended (if so)
    end_date = models.DateField(blank=True, null=True)
    
    objects = models.Manager()
    # filter out inactive roles
    # TODO: maybe this may be implemented via a ``QueryManager``
    current = GasReferrerManager()

## COMMENT: each role may be modeled after this