from django.conf.urls import url

from shop.views import YamlFileUpload

app_name = 'shop'

urlpatterns = [
    url(r'^upload/', YamlFileUpload.as_view(), name='yaml-file-upload'),
]
