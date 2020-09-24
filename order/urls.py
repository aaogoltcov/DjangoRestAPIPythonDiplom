from django.conf.urls import url

from order.views import BasketView, OrderView

app_name = 'order'

urlpatterns = [
    url(r'^basket', BasketView.as_view(), name='basket'),
    url(r'^order', OrderView.as_view(), name='order'),
]
