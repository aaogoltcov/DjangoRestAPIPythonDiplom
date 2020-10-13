from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('order.urls', 'order'), namespace='order')),
    path('api/', include(('product.urls', 'product'), namespace='product')),
    path('api/', include(('shop.urls', 'shop'), namespace='shop')),
    path('api/', include(('user_account.urls', 'user_account'), namespace='user_account')),
    path('openapi', get_schema_view(
        title="Orders",
        description="API for Orders",
        version="1.0.0",
    ), name='openapi-schema'),
]
