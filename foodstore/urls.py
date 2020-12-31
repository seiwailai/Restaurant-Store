from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.Home.as_view(), name='store-home'),
    path('category/<str:category>/', views.CategoryView.as_view(), name='store-category'),
    path('product/<int:pk>/', views.ProductDetail.as_view(), name='store-product-detail'),
    path('login/', views.Login.as_view() , name='store-login'),
    path('logout/', LogoutView.as_view(), name='store-logout'),
    path('signup/', views.signup, name='store-signup'),
    path('cart/', views.CartView.as_view(), name='store-cart'),
    path('cart/item_updated/', views.itemUpdate, name='store-item-update'),
    path('cart/check_out/', views.CheckoutView.as_view(), name='store-checkout'),
    path('create-checkout-session/', views.create_checkout_session, name='store-makePayment'),
    path('success/', views.success, name='store-success'),
    path('cancel/', views.cancel, name='store-cancel'),
    path('webhook/', views.my_webhook_view, name='store-webhook'),
    path('password_reset/', views.PasswordReset.as_view(), name='store-passwordReset'),
    path('password_reset_done/', views.PasswordResetDoneCustom.as_view(), name='store-passwordResetDone'),
    path('password_reset_confirm/<str:uidb64>/<str:token>', views.PasswordResetConfirmCustom.as_view(), name='store-passwordResetConfirm'),
    path('password_reset_completed/', views.PasswordResetCompleteCustom.as_view(), name='store-passwordResetComplete'),
    path('profile/<str:choice>/', views.ProfileView.as_view(), name='store-profile'),
    path('profile/Addresses/<int:pk>/', views.ProfileAddressDetail.as_view(), name='store-profile-address'),
]