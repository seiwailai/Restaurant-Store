from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Voucher(models.Model):
    code = models.CharField(max_length=20, null=True)
    valid_from = models.DateTimeField(blank=False)
    valid_to = models.DateTimeField(blank=False)
    min_purchase = models.FloatField(blank=False)
    discount_unit_choices = (
        ('Amount Off', 'Amount Off'),
        ('Percent Off', 'Percent Off'),
    )
    discount_unit = models.CharField(max_length=15, choices=discount_unit_choices, blank=False, default='Amount Off')
    discount = models.IntegerField(blank=False)
    active = models.BooleanField(blank=False)

    def __str__(self):
        return self.code


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=200, null=True)
    lastName = models.CharField(max_length=200, null=True)
    email = models.EmailField()
    used_vouchers = models.ManyToManyField(Voucher, blank=True)

    def __str__(self):
        return self.firstName + ' ' + self.lastName


class Category(models.Model):
    group = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['group']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.group


class ProductManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(name__icontains=query) | 
                         Q(description__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs
    

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    pax = models.IntegerField()
    description = models.TextField(max_length=500)
    category = models.ManyToManyField(Category, blank=True)
    image = models.ImageField(default='product_placeholder.png', null=True, blank=True, upload_to='product_images')
    objects = ProductManager()

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_ordered = models.DateTimeField(null=True, blank=True)
    complete = models.BooleanField(default=False, null=True)
    transaction_id = models.UUIDField(null=True, blank=True)
    discount_code = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        return f'{sum([item.get_total for item in orderitems]):.2f}'
    
    def get_cart_quantity(self):
        orderitems = self.orderitem_set.all()
        return sum([item.quantity for item in orderitems])
    
    @property
    def get_discount_amount(self):
        if self.discount_code:
            if self.discount_code.discount_unit == 'Amount Off':
                discount = self.discount_code.discount
            elif self.discount_code.discount_unit == 'Percent Off':
                discount = self.discount_code.discount/100 * float(self.get_cart_total)
            return f'{discount:.2f}'
        return f'{0:.2f}'
    
    @property
    def get_delivery_fees(self):
        if float(self.get_cart_total):
            if (float(self.get_cart_total)-float(self.get_discount_amount)) < 30:
                return f'{8:.2f}'
        return f'{0:.2f}'
    
    @property
    def get_cart_grand_total(self):
        return f'{float(self.get_cart_total) + float(self.get_delivery_fees) - float(self.get_discount_amount):.2f}'
    
    def apply_voucher(self, voucher):
        self.discount_code = voucher
    
    def clear_voucher(self):
        self.discount_code = None
    

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.product.name + ' on ' + str(self.date_added)

    @property
    def get_total(self):
        return self.product.price * self.quantity


class Carousel(models.Model):
    name = models.CharField(max_length=100)
    caption = models.TextField(max_length=150)
    date_posted = models.DateTimeField(default=timezone.now)
    image = models.ImageField(null=True, blank=True, upload_to="carousel_slides")

    def __str__(self):
        return self.name
             
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    

class DeliveryInfo(models.Model):
    firstName = models.CharField(max_length=200, null=True)
    lastName = models.CharField(max_length=200, null=True)
    phone = PhoneNumberField()
    email = models.EmailField()
    address1 = models.CharField(max_length=200, blank=False)
    address2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, blank=False)
    state = models.CharField(max_length=100, blank=False)
    country = models.CharField(max_length=100, blank=False)
    postalCode = models.IntegerField(blank=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    default = models.BooleanField(default=True)

    def __str__(self):
        return self.firstName + ' ' + self.lastName + ' ' + str(self.id)