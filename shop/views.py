import json

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework_yaml.renderers import YAMLRenderer
from yaml import load as load_yaml, Loader

from product.models import ProductInfo, Product, Parameter, ProductParameter
from shop.models import Shop, Category


class YamlFileUpload(APIView):

    parser_classes = (MultiPartParser,)
    renderer_classes = (YAMLRenderer,)

    def post(self, request, format=None):
        """
        Загрузка данных в модель Shop (первоначальная информация о магазине, товарах и категориях)
        В Postman в body нужно выбрать form-data и задать key 'filename' (тип file) с указание файла в поле value
        """

        filename = request.data['filename']
        if filename:
            try:
                FileExtensionValidator(allowed_extensions=['yaml', ]).__call__(filename)
                data = load_yaml(filename.read(), Loader=Loader)
                # # insert to Shop model
                shop_name = data['shop']
                new_filename = f'uploads/{shop_name}.json'
                with open(new_filename, 'w') as file:
                    json.dump(data, file)
                    shop, _ = Shop.objects.get_or_create(
                        name=shop_name,
                        init_file_content=data,
                        filename=new_filename,
                    )
                # insert to Categories model
                for category in data['categories']:
                    category, _ = Category.objects.get_or_create(
                        id=category['id'],
                        name=category['name'],
                    )
                    category.shops.add(shop.id)
                    category.save()
                # insert to Categories model
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id,
                                                              # name=item['name'],
                                                              )
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value,
                                                        # name=item['name'],
                                                        )
                return JsonResponse({'Status': True})
            except (ValidationError, IntegrityError) as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
