from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from product.models import Product, ProductInfo
from product.serializers import ProductsSerializer, ProductInfoSerializer


class ProductsView(viewsets.ViewSet):
    """
    Класс для просмотра категорий
    URL - http://127.0.0.1:8000/api/products/pk/get
    GET - для получения информации по категориям продуктов в Header нужно добавить, например так: {
            key: 'Authorization',
            value: 'Token 3ecaa0f013165056af898e0adc2e2bed8d1fa6db' }
    """
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'get':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def get(self, request, *args, **kwargs):
        """
        Метод для поиска товаров
        URL - http://127.0.0.1:8000/api/products/pk/get?product_id=1
        GET - для получения информации по категориям продуктов в Header нужно добавить, например так: {
            key: 'Authorization',
            value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58' }, в params указать id продукта: {
            key: 'product_id',
            value: '1' }
        """
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
