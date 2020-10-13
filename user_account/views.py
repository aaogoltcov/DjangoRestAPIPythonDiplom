from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from user_account.serializers import UserSerializer
# from user_account.signals import new_user_registered
from .tasks import new_user_registered


class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """

    def post(self, request, *args, **kwargs):
        """
        POST - авторизация пользователей
        :param request: Для авторизации необходимо в form-data указать, например: [
                         { key: 'email' , value: 'aaogoltcov@mail.ru' },
                         { key: 'password' , value: 'aaogoltcov' },
                        ]
        :return: статус авторизации и токен
        """
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request=request, username=request.data['email'], password=request.data['password'])
            print(user, request.data['email'], request.data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({'Status': True, 'Token': token.key})
                    # return JsonResponse({'Status': True})
            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class RegisterAccount(APIView):
    """
    Класс регистрации покупателей
    """

    def post(self, request, *args, **kwargs):
        """
        POST - регистрация покупателей
        :param request: Для регистрации необходимо в form-data указать, например: [
                         { key: 'email' , value: 'aaogoltcov@mail.ru' },
                         { key: 'username' , value: 'aaogoltcov' },
                         { key: 'password' , value: 'aaogoltcov' },
                         { key: 'first_name' , value: 'aaogoltcov' },
                         { key: 'last_name' , value: 'aaogoltcov' },
                         { key: 'middle_name' , value: 'aaogoltcov' },
                         { key: 'company' , value: 'aaogoltcov' },
                         { key: 'position' , value: 'aaogoltcov' },
                        ]
        :return: статус регистрации
        """
        print('+', request.data)
        # проверяем обязательные аргументы
        if {'first_name', 'last_name', 'middle_name', 'email', 'username', 'password', 'company', 'position'} \
                .issubset(request.data):
            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    # new_user_registered.send(sender=self.__class__, user_id=user.id)
                    new_user_registered.delay(user_id=user.id)
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
