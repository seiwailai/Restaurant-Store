from .models import (
    Customer, 
    OrderItem, 
    Order, 
    Product, 
    DeliveryInfo
)

def checkDeliveryExist(deliveryData, customer):
    try:
        is_exist = DeliveryInfo.objects.filter(firstName=deliveryData['firstName'], lastName=deliveryData['lastName'], email=deliveryData['email'], customer=customer, address1=deliveryData['address1'], address2=deliveryData['address2'] if deliveryData['address2'] else None, phone=deliveryData['phone'], city=deliveryData['city'], state=deliveryData['state'], country=deliveryData['country'], postalCode=deliveryData['postalCode'])
    except Exception:
        is_exist = False
    return is_exist

def defaultDeliveryData(customer):
    try:
        deliveryDefault = customer.deliveryinfo_set.get(default=True)
    except DeliveryInfo.DoesNotExist:
        deliveryDefault = None
    return deliveryDefault

def serializeDeliveryInfo(deliveryInfo):
    if deliveryInfo:
        deliveryInfo = {
            'firstName': deliveryInfo.firstName,
            'lastName': deliveryInfo.lastName,
            'phone': deliveryInfo.phone.as_international,
            'email': deliveryInfo.email,
            'address1': deliveryInfo.address1,
            'address2': deliveryInfo.address2,
            'city': deliveryInfo.city,
            'state': deliveryInfo.state,
            'country': deliveryInfo.country,
            'postalCode': deliveryInfo.postalCode
        }
    return deliveryInfo

def serializeObjectList(object_list):
    serialized_object_list = {
        product.id: {
            'name': product.name,
            'pax': product.pax,
            'price': product.price,
            'description': product.description,
            'category': list(category.group for category in product.category.all()),
            'imageURL': product.imageURL,
            }
        for product in object_list
    }
    return serialized_object_list

def serializePageObj(page):
    page = {
        'has_previous': page.has_previous(),
        'previous_page_number': page.previous_page_number() if page.has_previous() else None,
        'number': page.number,
        'has_next': page.has_next(),
        'next_page_number': page.next_page_number() if page.has_next() else None,
        'paginator': {
            'page_range': list(page.paginator.page_range),
            'num_pages': page.paginator.num_pages
        },
        'object_list': serializeObjectList(page.object_list)
    }
    return page

def serializeOrderItem(orderItem):
    item = {
        "product": {
            "id": orderItem.product.id,
            "name": orderItem.product.name,
            "price": orderItem.product.price,
            "pax": orderItem.product.pax,
            "imageURL": orderItem.product.imageURL,
            "category": list(category.group for category in orderItem.product.category.all())
        },
        "quantity": orderItem.quantity,
        "get_total": "{:.2f}".format(orderItem.get_total)
    }
    return item

def get_order_context(order):
    orderAmount = order.get_cart_total
    delivery = order.get_delivery_fees
    delivery = delivery if float(delivery) > 0 else 'Free'
    discount = order.get_discount_amount
    grandTotal = order.get_cart_grand_total
    return orderAmount, delivery, discount, grandTotal

def updateCart(order, data):
    dataAction = data['dataAction']
    productID = data['productID']
    product = Product.objects.get(id=productID)
    if dataAction == 'addToCart':
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        orderItem.quantity += 1
        orderItem.save()
    elif dataAction == 'removeItem':
        orderItem = order.orderitem_set.get(product=product)
        orderItem.quantity = 0
        orderItem.delete()
    elif dataAction == 'reduceQuantity':
        orderItem = order.orderitem_set.get(product=product)
        orderItem.quantity -= 1
        if orderItem.quantity == 0:
            orderItem.delete()
        else:
            orderItem.save()
    elif dataAction == 'increaseQuantity':
        orderItem = order.orderitem_set.get(product=product)
        orderItem.quantity += 1
        orderItem.save()
    elif dataAction == 'addQuantity':
        quantity = data['quantity']
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        orderItem.quantity += int(quantity)
        orderItem.save()
    order.save()
    item = serializeOrderItem(orderItem)
    orderAmount, delivery, discount, grandTotal = get_order_context(order)
    return {'item': item, 'orderAmount': orderAmount, 'delivery': delivery, 'discount': discount, 'grandTotal': grandTotal}

def cartData(order):
    orderitems = order.orderitem_set.all()
    orderAmount, delivery, discount, grandTotal = get_order_context(order)
    return {'items': orderitems, 'orderAmount': orderAmount, 'delivery': delivery, 'discount': discount, 'grandTotal': grandTotal}

def get_customer_and_order(request):
    customer, created = Customer.objects.get_or_create(user=request.user, email=request.user.email, firstName=request.user.first_name, lastName=request.user.last_name)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    return customer, order