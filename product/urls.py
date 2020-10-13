# from django.conf.urls import url
#
# from product.views import ProductsView, ProductInfoView
#
# app_name = 'product'
#
# urlpatterns = [
#     url(r'^products', ProductsView.as_view(), name='products-view'),
#     url(r'^product/get', ProductInfoView.as_view(), name='product-get-view'),
# ]


from rest_framework.routers import DefaultRouter

from product.views import ProductsView

router = DefaultRouter()
router.register(r'products', ProductsView, basename='products')
urlpatterns = router.urls
