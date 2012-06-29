from django.db import models

from model_utils import Choices


class Subject(models.Model):
    """
    An actor operating within a given DES.
    
    It may be a GAS, a supplier or a person.
    """
    SUBJECT_TYPES = Choices(
                     'person',
                     'gas',
                     'supplier',
                     )
    # fields shared by each kind of subject go here
    # a sort of cache field; to be populated on subject creation
    subject_type = models.CharField(choices=SUBJECT_TYPES)

    def downcast(self):
        """
        Return the downcasted version of this subject.
        """
        pass
    
    
## DOM    
class Des(object):
    """
    The root object for the object hierarchy modeling a DES. 
    """
    @property
    def pacts(self):
        """
        The (query)set of active pacts in this DES.
        """ 
        pass
    
    @property
    def people(self):
        """
        The (query)set of people partecipating in this DES.
        """ 
        pass
    
    @property
    def gases(self):
        """
        The (query)set of GASes operating within this DES.
        """ 
        pass
    
    @property
    def suppliers(self):
        """
        The (query)set of suppliers operating within this DES.
        """ 
        pass
    