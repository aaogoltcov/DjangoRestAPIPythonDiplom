from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from product.models import Product, ProductInfo
from product.serializers import ProductsSerializer, ProductInfoSerializer


class ProductsView(ListAPIView):
    """
    Класс для просмотра категорий
    GET - для получения информации по категориям продуктов в Header нужно добавить, например так: {
            key: 'Authorization',
            value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58' }
    """
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer


class ProductInfoView(APIView):
    """
    Класс для поиска товаров
    GET - для получения информации по категориям продуктов в Header нужно добавить, например так: {
        key: 'Authorization',
        value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58' }, в params указать id продукта: {
        key: 'product_id',
        value: '1' }
    """

    def get(self, request, *args, **kwargs):
        query = Q(shop__state=True)
        product_id = request.query_params.get('product_id')
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        if product_id:
            query = query & Q(product_id=product_id)
        if shop_id:
            query = query & Q(shop_id=shop_id)
        if category_id:
            query = query & Q(product__category_id=category_id)
        # фильтруем и отбрасываем дуликаты
        queryset = ProductInfo.objects.filter(
            query).select_related(
            'product', 'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)
