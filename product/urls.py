from django.conf.urls import url

from product.views import ProductsView, ProductInfoView

app_name = 'product'

urlpatterns = [
    url(r'^products', ProductsView.as_view(), name='products-view'),
    url(r'^product/get', ProductInfoView.as_view(), name='product-get-view'),
]
