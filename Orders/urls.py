from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('order.urls', 'order'), namespace='order')),
    path('api/', include(('product.urls', 'product'), namespace='product')),
    path('api/', include(('shop.urls', 'shop'), namespace='shop')),
    path('api/', include(('user_account.urls', 'user_account'), namespace='user_account')),
]
