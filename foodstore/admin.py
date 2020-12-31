from django.contrib import admin
from .models import *

class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = ('used_vouchers',)

# Register your models here.
admin.site.register(Carousel)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DeliveryInfo)
admin.site.register(Voucher)