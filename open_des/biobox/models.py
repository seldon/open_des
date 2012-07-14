from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from open_des.utils.fields import CurrencyField
from open_des.people.models import Person 


class Subscription(models.Model):
    """
    A subscription to the bio-box (IT: "bio-cassetta") made by a given person for 
    a given period of time.
    """
    SUBSCRIPTION_TYPES = Choices(
                                ('SMALL', 'small', _('small')),
                                ('MEDIUM', 'medium', _('medium')),
                                ('LARGE', 'large', _('large')),
                                )
    # a unique ID for this subscription
    uid = models.PositiveSmallIntegerField(unique=True, writable=False)
    # who subscribed the bio-box
    subscriber = models.ForeignKey(Person)
    # type of this subscriptio
    _type = models.CharField(max_lenght=8, choices=SUBSCRIPTION_TYPES)
    # when the subscription started 
    start_date = models.DateField()
    # when the subscription started (if so)
    end_date = models.DateField(blank=True, Null=True)
    # whether this subscription is currently active 
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # auto-generate an UID on instance creation
        created = kwargs['created']
        if created and not self.uid:
            self.uid = self.generate_uid()
        ## model-level validation
        # * ``start_date`` must precede ``end_date`` (if the latter is set)
        # * ``is_active`` must be set consistently to ``end_date`` 
        super(self, Subscription).save(*args, **kwargs)
    
    def generate_uid(self):
        """
        Generate a UID for this subscription.
        """
        raise NotImplementedError
    
    
class Issue(models.Model):
    """
    A "issue" of the bio-box campaign. 
    """
    # a sequential number identifying this issue within a bio-box campaign
    seq_n = models.PositiveSmallIntegerField(unique=True, writable=False)
    # when this issue was delivered
    deliver_date = models.DateField(blank=True, Null=True)
    
    def save(self, *args, **kwargs):
        # auto-generate a sequential number on instance creation
        created = kwargs['created']
        if created and not self.seq_n:
            self.seq_n = self.generate_seq_n()
        super(self, Issue).save(*args, **kwargs)
        
    def generate_seq_n(self):
        """
        Generate a sequential number for this bio-box's issue.
        """
        raise NotImplementedError


class Box(models.Model):
    """
    A bio-box being delivered to a given subscriber of this bio-box campaign.
    """
    # the subscription corresponding to this box
    subscription = models.ForeignKey(Subscription)
    # when this box has been withdrawn by its subscriber
    withdrawal_date = models.DateField(blank=True, Null=True)
    # the price for this box
    price = CurrencyField()
    # if this box has been payed by its subscriber
    is_payed = models.BooleanField(default=False)