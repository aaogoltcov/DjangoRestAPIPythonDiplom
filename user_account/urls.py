from django.conf.urls import url

from user_account.views import LoginAccount, RegisterAccount

app_name = 'user'

urlpatterns = [
    url(r'^user/login', LoginAccount.as_view(), name='user-login'),
    url(r'^user/signup', RegisterAccount.as_view(), name='user-signup'),
]
