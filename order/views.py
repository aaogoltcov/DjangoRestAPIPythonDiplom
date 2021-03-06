from django.db import IntegrityError
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import Order, OrderItem
from order.serializers import OrderSerializer
from .tasks import new_order


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """

    def get(self, request, *args, **kwargs):
        """
        GET - получение информации из корзины
        :param request: в Header нужно добавить, например так:
                        {
                        key: 'Authorization',
                        value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58'
                        }
        :return: информация по товарам в корзине
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, status='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        POST - редактирование корзины
        :param request: в Header нужно добавить, например так:
                        {
                        key: 'Authorization',
                        value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58'
                        }, а в body raw в формате json:
                        {
                        "items": [
                                    {
                                        "id": 1,
                                        "quantity": 5
                                    },
                                    {
                                        "id": 2,
                                        "quantity": 5
                                    }
                                ]
                        }
        :return: статус и количество обновленных дефектов
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        product_items = request.data.get('items')
        if product_items:
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
            objects_created = 0
            for item in product_items:
                OrderItem.objects.filter(order_id=basket.id, product_info_id=item['id']).update(
                    quantity=item['quantity'])
                item.update({'order_id': basket.id, 'product_info_id': item['id']})
                objects_created += 1
            return JsonResponse({'Status': True,
                                 'Обновлено объектов': objects_created,
                                 'data': list(OrderItem.objects.filter(order_id=basket.id).values())})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def delete(self, request, *args, **kwargs):
        """
        DELETE - удаление товаров из корзины
        :param request: в Header нужно добавить, например так:
                        {
                        key: 'Authorization',
                        value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58'
                        }, а в body raw в формате json:
                        {
                            "items": [ 1, 2 ]
                        }
        :return: статус об удалении товаров из корзины
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_list = request.data.get('items')
        if len(items_list) > 0:
            # items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if type(order_item_id) == int:
                    query = query | Q(order_id=basket.id, product_info_id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def put(self, request, *args, **kwargs):
        """
        PUT - добавление товаров в корзину
        :param request: в Header нужно добавить, например так:
                        {
                        key: 'Authorization',
                        value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58'
                        }, а в body raw в формате json:
                        {
                        "items": [
                                    {
                                        "id": 1,
                                        "quantity": 1
                                    },
                                    {
                                        "id": 2,
                                        "quantity": 10
                                    }
                                ]
                        }
        :return: статус о добавлении товаров в корзину
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        product_items = request.data.get('items')
        if product_items:
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
            objects_updated = 0
            for item in product_items:
                if type(item['id']) == int and type(item['quantity']) == int:
                    orderItem, _ = OrderItem.objects.get_or_create(order_id=basket.id, product_info_id=item['id'])
                    objects_updated += OrderItem.objects.filter(order_id=basket.id, product_info_id=item['id']).update(
                        quantity=item['quantity']
                    )
            return JsonResponse({'Status': True, 'Добавлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class OrderView(APIView):
    """
    Класс для получения и размешения заказов пользователями
    """
    def get(self, request, *args, **kwargs):
        """
        GET - получение информации по заказам
        :param request: в Header нужно добавить Token, например так:
                        {
                        key: 'Authorization',
                        value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58'
                        }
        :return: Информация по заказу
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Order.objects.filter(
            user_id=request.user.id).exclude(status='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('profile').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):
        """
        POST - размещение заказа
        :param request: в Header нужно добавить Token, например так:
                        {
                        key: 'Authorization',
                        value: 'Token 80d57ddd904f358b00375f500d74d181fdbc9a58'
                        }, а в body raw в формате json:
                        {
                            "order_id": 2,
                            "profile_id": 3
                        }
        :kwargs: order_id, profile_id
        :return: Статус обработки
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'order_id', 'profile_id'}.issubset(request.data):
            if request.data['order_id']:
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['order_id']).update(
                        profile_id=request.data['profile_id'],
                        status='new')
                except IntegrityError as error:
                    return JsonResponse({'Status': False, 'Errors': f'Неправильно указаны аргументы: {error}'})
                else:
                    if is_updated:
                        # new_order.send(sender=self.__class__, user_id=request.user.id)
                        new_order.delay(user_id=request.user.id)
                        return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
