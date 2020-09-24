DB

sudo -u postgres psql postgres
create user rest_api with password 'rest_api';
alter role rest_api set client_encoding to 'utf8';
alter role rest_api set timezone to 'UTC';
create database rest_api owner rest_api;

PROJECT

python manage.py createsuperuser
login: admin
email: admin@admin.ru
password: admin
python manage.py makemigrations
python manage.py migrate

Критерии достижения:

1. Полностью работающие API Endpoint.
Описание по работе с Endpoint представлен в каждой View отдельно.
Также по ссылке находится коллекция уже преднастроенных http запросов в PostMan (чтобы не создавать с нуля). 

Корректно отрабатывает следующий сценарий:
1. Пользователь может авторизоваться;
Сделано с помощью LoginAccount(APIView).

2. Есть возможность отправки данных для регистрации и получения email с подтверждением регистрации;
Сделано с помощью RegisterAccount(APIView).

3. Пользователь может добавлять в корзину товары от разных магазинов;
Сделано с помощью BasketView(APIView).

4. Пользователь может подтверждать заказ с вводом адреса доставки;
Сделано с помощью OrderView(APIView), адрес доставки береться из Profile.

5. Пользователь получает email с подтверждением после ввода адреса доставки;
Сделано с помощью OrderView(APIView), адрес доставки береться из Profile, 
дальше уходит письмо на электронный адрес почты, которые был указан при регистрации.

6. Пользователь может переходить на страницу "Заказы" и открывать созданный заказ.
Сделано с помощью OrderView(APIView).

Продвинутая часть (по желанию, если базовая часть полностью готова):

1. Реализация forms и views админки склада
Все модели представлены в админке.

2. Вынос медленных методов в задачи Celery
new_order_signal сделан на уровне создания заказа и new_user_registered_signal при регистрации. 
import сделан с помощью YamlFileUpload(APIView).