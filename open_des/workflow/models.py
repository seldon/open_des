from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from open_des.person.models import Person

from datetime import datetime

class WorkflowStateChange(models.Model):
    """
    A record describing a state transition for a workflow-enabled model.
    
    In particular, for each state transition the following pieces of info is recorded:
    
    * the model instance whose state changed (``instance``)
    * the source state for the transition (``source_state``)
    * the final state for the transition (``target_state``)
    * when the transition occurred (``date``)
    * the person who triggered the transition (``issuer``)
    
    Note that, in the workflow model adopted by OpenDES, a state is simply a (positive) integer,
    mapping to a model-level symbolic costant.
    
    For example:
    class Foo(models.Model):
        (BAR, BAZ) = range(0,2)
        
        FOO_STATES_CHOICES = (
        (BAR, _('Bar')),
        (BAZ, _('Baz')),
        )
        
        ...
        status = models.IntegerField(choices=INVOICE_STATES_CHOICES)
        
    This model implements the following validation checks at when saving an instance:
    
    * source state must differ from target state
    * source and target states must be valid status choices for ``instance``    
    * issuer must be an active user when the record is taken
    
    If any of these conditions isn't verified, raise ``ValidationError``
    """    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    instance = generic.GenericForeignKey(ct_field='content_type', fk_field='object_id')
    source_state = models.PositiveSmallIntegerField()
    target_state = models.PositiveSmallIntegerField()
    date = models.DateTimeField(default=datetime.now)
    issuer = models.ForeignKey(Person)
    
    # model-level custom validation goes here
    def clean(self):
    # TODO: run this hook on ``post_save`` signale
    # TODO: source state must differ from target state
    # TODO: source and target states must be valid status choices for ``instance``    
    # TODO: issuer must be an active user when the record is taken  
        pass
    
    class WorkflowDescriptor(object):
        """
        Should work similar to ``AccountingProxy``
        should take as input the name of the model field contataining status info. 
        """
        
    

