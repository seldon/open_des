from django.db import models

from accounting.models import Invoice

from open_des.pact.models import SolidalPact
from open_des.supplier.models import SupplierStock

# GAS -> Supplier   
class GASSupplierStock(models.Model):
    pact = models.ForeignKey(SolidalPact)
    stock = models.ForeignKey(SupplierStock)  
    

class GASSupplierOrder(models.Model):
    # workflow management
    (OPEN, CLOSED, ON_COMPLETION, FINALIZED, SENT, DELIVERED, WITHDRAWN, ARCHIVED, CANCELED) = range(0,9)
    SUPPLIER_ORDER_STATUS_CHOICES = (
        (OPEN, _('OPEN')),
        (CLOSED, _('CLOSED')),
        (ON_COMPLETION, _('ON_COMPLETION')),
        (FINALIZED, _('FINALIZED')),
        (SENT, _('SENT')),
        (DELIVERED, _('DELIVERED')),
        (WITHDRAWN, _('WITHDRAWN')),
        (ARCHIVED, _('ARCHIVED')),
        (CANCELED, _('CANCELED')),        
    )
    pact = models.ForeignKey(SolidalPact, related_name='order_set')
    # workflow management
    status = models.CharField(max_length=20, choices=SUPPLIER_ORDER_STATUS_CHOICES)
    invoice = models.ForeignKey(Invoice, null=True, blank=True)
    
    @property
    def orderable_products(self):
        """
        The queryset of ``GASSupplierOrderProduct``s associated with this order. 
        """
        return self.order_product_set.all()
    
    @property
    def purchasers(self):
        """
        The set of GAS members participating to this supplier order.
        """
        # FIXME: for consistency, the return value should be a ``QuerySet``
        purchasers = set([order.purchaser for order in self.member_orders])
        return purchasers

    @property
    def member_orders(self):
        """
        The queryset of GAS members' orders issued against this supplier order.
        """
        member_orders = GASMemberOrder.objects.filter(ordered_product__order=self)
        return member_orders
    
    @property
    def total_amount(self):
        """
        The total expense for this order, as resulting from the invoice. 
        """
        amount = 0 
        for order_product in self.orderable_products:
            price = order_product.delivered_price
            quantity = order_product.delivered_amount
            amount += price * quantity
        return amount    
    

class GASSupplierOrderProduct(models.Model):
    order = models.ForeignKey(GASSupplierOrder, related_name='order_product_set')
    gas_stock = models.ForeignKey(GASSupplierStock)
    # the price of the Product at the time the GASSupplierOrder was created
    initial_price = CurrencyField()
    # the price of the Product at the time the GASSupplierOrder was sent to the Supplier
    order_price = CurrencyField()
    # the actual price of the Product (as resulting from the invoice)
    delivered_price = CurrencyField(null=True, blank=True)
    # how many items were actually delivered by the Supplier 
    delivered_amount = models.PositiveIntegerField(null=True, blank=True)
    
# GAS member -> GAS
class GASMemberOrder(models.Model):
    # workflow management
    (UNCONFIRMED, CONFIRMED, FINALIZED, SENT, READY, WITHDRAWN, NOT_WITHDRAWN, CANCELED) = range(0,8)
    MEMBER_ORDER_STATUS_CHOICES = (
        (UNCONFIRMED, _('UNCONFIRMED')),
        (CONFIRMED, _('CONFIRMED')),
        (FINALIZED, _('FINALIZED')),
        (SENT, _('SENT')),
        (READY, _('READY')),
        (WITHDRAWN, _('WITHDRAWN')),
        (NOT_WITHDRAWN, _('NOT_WITHDRAWN')),
        (CANCELED, _('CANCELED')),
    )        
    purchaser = models.ForeignKey(GasMember, related_name='issued_order_set')
    ordered_product = models.ForeignKey(GASSupplierOrderProduct)
    # price of the Product at order time
    ordered_price = CurrencyField()
    # how many Product units were ordered by the GAS member
    ordered_amount = models.PositiveIntegerField()
    # how many Product units were withdrawn by the GAS member 
    withdrawn_amount = models.PositiveIntegerField()
    # workflow management
    status = models.CharField(max_length=20, choices=MEMBER_ORDER_STATUS_CHOICES)
    
    @property
    def supplier_order(self):
        """
        Which supplier order this member order was issued against.
        """
        return self.ordered_product.order
