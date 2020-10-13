from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.utils import json


class TestProducts(APITestCase):
    def setUp(self):
        self.user = self.setup_user()
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.test_product_id = int()
        self.test_external_id = int()

        # database data upload
        self.client.post('http://127.0.0.1:8000/api/upload/',
                         {'filename': open('Orders/test_orders/test_shop_data.yaml')})

    @staticmethod
    def setup_user():
        User = get_user_model()
        return User.objects.create_user(
            'test',
            email='testuser@test.com',
            password='test'
        )

    def get_test_product(self):
        response = self.client.get('http://localhost/api/products/pk/get/',
                                   HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        data = json.loads(response.content)
        self.test_product_id = data[0]['id']
        self.test_external_id = data[0]['external_id']

    def test_products_list_response(self):
        response = self.client.get('http://localhost/api/products/pk/get/',
                                   HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))

    def test_get_products_list(self):
        response = self.client.get('http://localhost/api/products/pk/get/',
                                   HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        data_length = len(json.loads(response.content))
        self.assertEqual(data_length, 4,
                         'Expected Data Length 4, received {0} instead.'
                         .format(data_length))

    def test_get_product_id(self):
        self.get_test_product()
        response = self.client.get('http://localhost/api/products/pk/get/',
                                   {'product_id': self.test_product_id},
                                   HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        product_external_id = json.loads(response.content)[0]['external_id']
        self.assertEqual(product_external_id, self.test_external_id,
                         'Expected Product External ID {0}, received {1} instead.'
                         .format(self.test_external_id, product_external_id))

    def test_basket_response(self):
        response = self.client.get('http://127.0.0.1:8000/api/basket',
                                   HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))

    def test_check_empty_basket(self):
        response = self.client.get('http://127.0.0.1:8000/api/basket',
                                   HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        data_length = len(json.loads(response.content))
        self.assertEqual(data_length, 0,
                         'Expected Response Data Length 0, received {0} instead.'
                         .format(data_length))

    def test_basket_put_and_get_product(self):
        # put
        self.get_test_product()
        response_put = self.client.put('http://127.0.0.1:8000/api/basket',
                                       json.dumps({"items": [
                                           {
                                               "id": self.test_product_id,
                                               "quantity": 1
                                           }
                                       ]}),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        response_status = json.loads(response_put.content)['Status']
        self.assertEqual(response_status, True,
                         'Expected Status True, received {0} instead.'
                         .format(response_status))

        # get
        response_get = self.client.get('http://127.0.0.1:8000/api/basket',
                                       HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        data = json.loads(response_get.content)
        data_length = len(data)
        data_product_id = data[0]['ordered_items'][0]['product_info']['id']
        self.assertEqual(data_length, 1,
                         'Expected Response Data Length 1, received {0} instead.'
                         .format(data_length))
        self.assertEqual(data_product_id, self.test_product_id,
                         'Expected Response Data Length {0}, received {1} instead.'
                         .format(self.test_product_id, data_product_id))
