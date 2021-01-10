from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    update_session_auth_hash
    )
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, 
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.db import models
from django.http import (
    JsonResponse, 
    HttpResponseRedirect, 
    QueryDict, 
    HttpResponse
)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .forms import (
    CreateUserForm, 
    LoginForm, 
    CreateDeliveryForm, 
    PasswordResetCustomForm, 
    SetPasswordCustomForm, 
    PasswordChangeCustomForm
)
import json
from .models import *
import os
import stripe
from .utils import (
    serializePageObj, 
    serializeDeliveryInfo, 
    updateCart, 
    cartData, 
    defaultDeliveryData, 
    checkDeliveryExist, 
    get_order_context, 
    get_customer_and_order
)
import uuid


# Main Views.
class Home(ListView):
    model = Product
    template_name = 'foodstore/home.html'
    paginate_by = 3
    ordering = 'price'

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        query = self.request.GET.get('q', None)
        if query is not None:
            queryset = Product.objects.search(query)
        else:
            if self.queryset is not None:
                queryset = self.queryset
                if isinstance(queryset, QuerySet):
                    queryset = queryset.all()
            elif self.model is not None:
                queryset = self.model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        if request.is_ajax():
            page = serializePageObj(context['page_obj'])
            return JsonResponse({'page_obj':page})
        else:
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Rump House'
        context['carousels'] = Carousel.objects.all()
        context['carousels_n'] = list(range(len(Carousel.objects.all())))
        context['categories'] = Category.objects.all()
        return context


class CategoryView(ListView):
    model = Product
    template_name = 'foodstore/home.html'
    paginate_by = 3
    ordering = 'price'

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        query = self.request.GET.get('q', None)
        if query is not None:
            queryset = Product.objects.search(query)
        else:
            if self.queryset is not None:
                queryset = self.queryset
                if isinstance(queryset, QuerySet):
                    queryset = queryset.all()
            elif self.model is not None:
                queryset = self.model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )

        category = self.kwargs.get('category')
        if category is not None and queryset is not None:
            categoryObj = Category.objects.get(group=category)
            queryset = queryset.filter(category=categoryObj)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        if request.is_ajax():
            page = serializePageObj(context['page_obj'])
            return JsonResponse({'page_obj':page})
        else:
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.kwargs.get('category') + ' Menu'
        context['carousels'] = Carousel.objects.all()
        context['carousels_n'] = list(range(len(Carousel.objects.all())))
        context['categories'] = Category.objects.all()
        context['kwargs'] = self.kwargs
        return context


class ProductDetail(DetailView):
    model = Product
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context


#Authentication-related Views
class Login(LoginView):
    template_name = 'foodstore/login.html'
    redirect_authenticated_user=True
    authentication_form = LoginForm
    extra_context = {
        'title': 'Log In'
    }

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        customer, created = Customer.objects.get_or_create(user=self.request.user, email=self.request.user.email, firstName=self.request.user.first_name, lastName=self.request.user.last_name)
        customer.save()
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order.save()
        return HttpResponseRedirect(self.get_success_url())


def signup(request):
    if request.user.is_authenticated:
        return redirect(reverse('store-home'))
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, f'Account was created for {user}')
                return redirect('store-login')
                
        return render(request, 'foodstore/signup.html', {'title': 'Sign Up', 'form': form})


class PasswordReset(PasswordResetView):
    template_name = 'foodstore/password_reset.html'
    email_template_name = 'foodstore/password_reset_email.html'
    subject_template_name = 'foodstore/password_reset_subject.txt'
    form_class = PasswordResetCustomForm
    extra_context = {
        'title': 'Password Reset Request'
    }
    success_url = '/password_reset_done/'


class PasswordResetDoneCustom(PasswordResetDoneView):
    template_name = 'foodstore/password_reset_done.html'
    extra_context = {
        'title': 'Password Reset Sent'
    }


class PasswordResetConfirmCustom(PasswordResetConfirmView):
    template_name = 'foodstore/password_reset_confirm.html'
    extra_context = {
        'title': 'Password Reset Confirmation'
    }
    form_class = SetPasswordCustomForm
    success_url = '/password_reset_completed/'


class PasswordResetCompleteCustom(PasswordResetCompleteView):
    template_name = 'foodstore/password_reset_complete.html'
    extra_context = {
        'title': 'Password Reset Completed'
    }


# Cart and CheckOut Views
class CartView(LoginRequiredMixin, ListView):
    template_name = 'foodstore/cart.html'
    model = Order
    
    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        customer, order = get_customer_and_order(self.request)
        order.clear_voucher()
        order.save()
        context['title'] = 'Cart'
        context['cartData'] = cartData(order)
        return context


class CheckoutView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'foodstore/checkout.html'


    def handlingDeliveryForm(self, data, customer):
        dataAction = data['dataAction']
        if dataAction == 'getDefaultDeliveryInfo':
            response = JsonResponse({'deliveryDefault': serializeDeliveryInfo(defaultDeliveryData(customer))})
        elif dataAction == 'submitDeliveryForm':
            deliveryData = data['deliveryData']
            isExist = checkDeliveryExist(deliveryData, customer)
            if isExist:
                deliveryInfo = isExist
                response = JsonResponse({'url': reverse('store-makePayment')})
                response.status_code = 200
            else:
                queryDict = QueryDict('', mutable=True)
                queryDict.update(deliveryData)
                form = CreateDeliveryForm(queryDict)
                if form.is_valid():
                    deliveryInfo = form.save()
                    deliveryDefault = defaultDeliveryData(customer)
                    if deliveryDefault:
                        deliveryDefault.default = False
                        deliveryDefault.save()
                    deliveryInfo.customer = customer
                    deliveryInfo.default = True
                    deliveryInfo.save()
                    response = JsonResponse({'url': reverse('store-makePayment')})
                    response.status_code = 200
                else:
                    response = JsonResponse({'error': form.errors})
                    response.status_code = 400
        return response
    
    def handlingVoucher(self, data, customer):
        dataAction = data['dataAction']
        if dataAction == 'applyVoucher':
            now = timezone.now()
            voucherCode = data['voucherCode']
            try:
                voucher = Voucher.objects.get(
                    code__iexact=voucherCode,
                    valid_from__lte=now,
                    valid_to__gt=now,
                    active=True
                )
                if voucher not in customer.used_vouchers.all():
                    order, created = Order.objects.get_or_create(customer=customer, complete=False)
                    if float(order.get_cart_total) >= voucher.min_purchase:
                        order.apply_voucher(voucher)
                        order.save()
                        orderAmount, delivery, discount, grandTotal = get_order_context(order)
                        response = JsonResponse({'orderAmount': orderAmount, 'delivery': delivery, 'discount': discount, 'grandTotal': grandTotal, 'discountCode': voucher.code})
                    else:
                        response = JsonResponse({'error': f'The voucher with code of {voucher.code} requires minimum purchase of RM{voucher.min_purchase}'})
                        response.status_code = 403  
                else:
                    response = JsonResponse({'error': f'The voucher with code of {voucher.code} is used by this customer in previous purchases'})
                    response.status_code = 403    
            except Voucher.DoesNotExist as error:
                response = JsonResponse({'error': 'Voucher entered is either expired or not existed'})
                response.status_code = 403
            return response
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            customer, created = Customer.objects.get_or_create(user=request.user)
            data = json.loads(request.body)
            dataClass = data['dataClass']
            if dataClass == 'deliveryForm':
                return self.handlingDeliveryForm(data, customer)
            elif dataClass == 'voucher':
                return self.handlingVoucher(data, customer)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        customer, order = get_customer_and_order(self.request)
        order.clear_voucher()
        order.save()
        context['cartData'] = cartData(order)
        context['title'] = 'Check Out'
        context['form'] = CreateDeliveryForm()
        context['deliveryDefault'] = defaultDeliveryData(customer)
        return context


def itemUpdate(request):
    if request.is_ajax():
        if request.user.is_authenticated:
            data = json.loads(request.body)
            customer, created = Customer.objects.get_or_create(user=request.user, email=request.user.email, firstName=request.user.first_name, lastName=request.user.last_name)
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            context = updateCart(order, data)
            return JsonResponse(context)


# Stripe Payment Views
stripe.api_key = settings.STRIPE_SK

def create_checkout_session(request):
    customer, order = get_customer_and_order(request)
    data = cartData(order)
    voucher = order.discount_code
    print(voucher)
    if voucher:
        try:
            stripe.Coupon.retrieve(voucher.code)
        except stripe.error.InvalidRequestError:      
            stripe.Coupon.create(
                currency = 'myr',
                amount_off = int(float(order.get_discount_amount)*100),
                id = voucher.code,
                name = voucher.code,
                duration = 'once',
            )
    line_items = []
    for item in data['items']:
        line_items.append({
            'price_data': {
                        'currency': 'myr',
                        'unit_amount': int(item.product.price * 100),
                        'product_data': {
                            'name': item.product.name,
                        },
                    },
                    'quantity': item.quantity
        })
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card', 'fpx'],
            line_items=line_items,
            mode='payment',
            discounts = [{'coupon': voucher.code}] if voucher else [],
            success_url=request.build_absolute_uri(reverse('store-success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('store-cancel')) + '?session_id={CHECKOUT_SESSION_ID}',
        )
        return JsonResponse({'session_id' : session.id, 'STRIPE_PK': settings.STRIPE_PK})
    except Exception as e:
        print(e)
        response = JsonResponse({'error': str(e)})
        response.status_code = 403
        return response

def success(request):
    context = {
        'title': 'Payment Success'
    }
    customer, order = get_customer_and_order(request)
    order.complete = True
    order.transaction_id = uuid.uuid4()
    order.date_ordered = timezone.now()
    order.save()
    return render(request, 'foodstore/success.html', context)

def cancel(request):
    context = {
        'title': 'Checkout Canceled',
    }
    return render(request, 'foodstore/cancel.html', context)

@csrf_exempt
def my_webhook_view(request):
    endpoint_secret = "whsec_m5O2MgDU3FSjkazPpOBuUmVyp5hyU4F0"
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object # contains a stripe.PaymentIntent
        print('PaymentIntent was successful!')
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object # contains a stripe.PaymentMethod
        print('PaymentMethod was attached to a Customer!')
    # ... handle other event types
    elif event.type == 'payment_intent.created':
        print('PaymentIntent was created!')
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)
        

# Client Profile Views
class ProfileView(LoginRequiredMixin, ListView):
    template_name = 'foodstore/profile_orders.html'
    model = Order

    def post(self, *args, **kwargs):
        choice = self.kwargs.get('choice')
        data = json.loads(self.request.body)
        passwordChangeData = data['passwordChangeData']
        if choice == 'Change Password':
            form = PasswordChangeCustomForm(self.request.user, passwordChangeData)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(self.request, user)
                response = JsonResponse({'url': reverse('store-profile', kwargs={'choice': 'Change Password Success'})})
            else:
                response = JsonResponse({'error': form.errors})  
                response.status_code = 403
            return response      
    
    def get_password_change_success_context(self, context):
        self.template_name = 'foodstore/password_change_success.html'
        context['title'] = 'Password Changed Success'

    def get_orders_object_context(self, context, customer):
        orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_ordered')
        context['orders'] = orders
        context['subtitle'] = 'Orders'
        context['title'] = 'Order History'
    
    def get_address_object_context(self, context, customer):
        self.template_name = 'foodstore/profile_addresses.html'
        context['addresses'] = customer.deliveryinfo_set.all()
        context['subtitle'] = 'Addresses'
        context['title'] = 'Manage Address'
    
    def get_password_change_form_context(self, context):
        self.template_name = 'foodstore/password_change.html'
        context['form'] = PasswordChangeCustomForm(user=self.request.user)
        context['subtitle'] = 'Change Password'
        context['title'] = 'Change Password'
    
    def get_context_data(self, **kwargs):
        choice = self.kwargs.get('choice')
        context = super(ProfileView, self).get_context_data(**kwargs)
        customer, order = get_customer_and_order(self.request)
        context['kwargs'] = self.kwargs
        context['GET_subURL'] = ['Orders', 'Addresses', 'Change Password']
        if choice == 'Orders':
            self.get_orders_object_context(context, customer)
        elif choice == 'Addresses':
            self.get_address_object_context(context, customer)
        elif choice == 'Change Password':
            self.get_password_change_form_context(context)
        elif choice == 'Change Password Success':
            self.get_password_change_success_context(context)
        return context


class ProfileAddressDetail(DetailView):
    template_name = 'foodstore/profile_address_edit.html'
    model = DeliveryInfo

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        deliveryData = data['deliveryData']
        deliveryObj = DeliveryInfo.objects.get(pk=self.kwargs.get('pk'))
        form = CreateDeliveryForm(deliveryData, instance=deliveryObj)
        if form.is_valid():
            customer, order = get_customer_and_order(request)
            if form.fields['default']:
                existingDefault = customer.deliveryinfo_set.get(default=True)
                existingDefault.default = False
                existingDefault.save()
            deliveryInfo = form.save()
            deliveryInfo.customer = customer
            deliveryInfo.save()
            response = JsonResponse({'url': reverse('store-profile', kwargs={'choice': 'Addresses'})})
        else:
            response = JsonResponse({'error': form.errors})
            response.status_code = 403
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.kwargs.update({'choice': 'Addresses'})
        context['kwargs'] = self.kwargs
        deliveryObj = context['object']
        context['title'] = 'Edit Address'
        context['GET_subURL'] = ['Orders', 'Addresses', 'Change Password']
        context['form'] = CreateDeliveryForm(instance=deliveryObj)
        return context

