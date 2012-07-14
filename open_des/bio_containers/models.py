from django.db import models
from django.utils.translation import ugettext_lazy as _

from open_des.utils.fields import CurrencyField
from open_des.people.models import Person 


class BioContainerType(models.Model):
    """
    An abstract base class modeling a kind of "bio-container" (bio-box or bio-bag).
    """
    # a short, identifying name for this bio-container
    name = models.CharField()
    # an optional, longer description 
    description = models.TextField(blank=True)
    # unit price for this bio container
    unit_price = CurrencyField() 
    
    class Meta:
        abstract = True
      
        
class BioBoxType(BioContainerType):
    """
    This model represents a specific type of "bio-box" (IT: "bio-cassetta").
    """
    # weight of a given instance of this bio-box (UM: Kg)
    weight = models.DecimalField()
    
    @property
    def price(self):
        """
        The actual price for this bio-box (it's the same for every bio-box of this type).
        """
        return self.unit_price * self.weight

class BioBagType(BioContainerType):
    """
    This model represents a specific type of "bio-bag" (IT: "bio-sporta").
    """
    # the name of the product contained by this bio-bag   
    product_name = models.CharField()
        

class Subscription(models.Model):
    """
    An abstract base class modeling subscriptions made by people 
    to a given kind of bio-container.
    """
    # a unique ID for this subscription
    uid = models.PositiveSmallIntegerField(unique=True, writable=False)
    # who subscribed to the bio-container
    subscriber = models.ForeignKey(Person)
    # when the subscription started 
    start_date = models.DateField()
    # when the subscription ended (if so)
    end_date = models.DateField(blank=True, Null=True)
    # whether this subscription is currently active 
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        # auto-generate an UID on instance creation
        created = kwargs['created']
        if created and not self.uid:
            self.uid = self.generate_uid()
        # TODO: add model-level validation
        # * ``start_date`` must precede ``end_date`` (if the latter is set)
        # * ``is_active`` must be set consistently to ``end_date`` 
        super(self, Subscription).save(*args, **kwargs)
    
    def generate_uid(self):
        """
        Generate a UID for this subscription.
        """
        raise NotImplementedError


class BioBoxSubscription(Subscription):
    """
    A subscription to the bio-box made by a given person for 
    a given period of time.
    """
    # type of this subscription
    _type = models.ForeignKey(BioBoxType)   


class BioBagSubscription(Subscription):
    """
    A subscription to the bio-bag made by a given person for 
    a given period of time.
    """
    # type of this subscription
    _type = models.ForeignKey(BioBagType)   

    
class ContainerIssue(models.Model):
    """
    An abstract base class modeling an "issue" of a bio-container's campaign. 
    """
    # a sequential number identifying this issue within a bio-box campaign
    seq_n = models.PositiveSmallIntegerField(unique=True, writable=False)
    # a reference date for this issue
    issue_date = models.DateField(blank=True, Null=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        # auto-generate a sequential number on instance creation
        created = kwargs['created']
        if created and not self.seq_n:
            self.seq_n = self._generate_seq_n() 
        super(self, ContainerIssue).save(*args, **kwargs)
        # automatically generate a "bio-container" record for each active subscription
        self._generate_containers()
        
    def _generate_seq_n(self):
        """
        Generate a sequential number for this bio-container's issue.
        """
        raise NotImplementedError

    def _generate_containers(self):
        """
        Generate a "bio-container" record (of the right type) for each active subscription 
        to that kind of bio-container.  
        """
        raise NotImplementedError       


class BioBoxIssue(ContainerIssue):
    """
    An "issue" of a bio-box's campaign.
    """
    # the type of bio-box for this issue
    _type = models.ForeignKey(BioBoxType)

    def subscriptions(self):
        """
        Return a queryset of active subscriptions (with respect to this issue).
        """
        raise NotImplementedError

class BioBagIssue(ContainerIssue):
    """
    An "issue" of a bio-bag's campaign.
    """
    # the type of bio-bag for this issue
    _type = models.ForeignKey(BioBagType)

    def subscriptions(self):
        """
        Return a queryset of active subscriptions (with respect to this issue).
        """
        raise NotImplementedError


class BioContainer(models.Model):
    """
    An abstract base class modeling a "bio-container" instance (bio-box or bio-bag)
    being delivered to a given subscriber of a bio-container campaign.
    """
    # when this container has been withdrawn by its subscriber
    withdrawal_date = models.DateField(blank=True, Null=True)
    # the price for this container
    price = CurrencyField()
    # if this container has been payed by its subscriber
    is_payed = models.BooleanField(default=False)
    
    class Meta:
        abstract = True


class BioBox(BioContainer):
    """
    A bio-box being delivered to a given subscriber of a bio-box campaign.
    """
    # the subscription corresponding to this box
    subscription = models.ForeignKey(BioBoxSubscription)
    
    @property
    def price(self):
        """
        The actual price for this bio-box (it's the same for all instances).
        """
        return self.subscription._type.price
    

class BioBag(BioContainer):
    """
    A bio-bag being delivered to a given subscriber of a bio-bag campaign.
    """
    # the subscription corresponding to this bag
    subscription = models.ForeignKey(BioBagSubscription)
    # weight of this bio-bag (UM: Kg)
    weight = models.DecimalField()
    
    @property
    def price(self):
        """
        The actual price for this bio-bag (may vary between instances!).
        """
        unit_price = self.subscription._type.unit_price 
        return unit_price * self.weight