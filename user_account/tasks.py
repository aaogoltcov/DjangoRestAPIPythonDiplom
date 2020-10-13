from celery import shared_task
from django.core.mail import EmailMultiAlternatives

from Orders import settings
from user_account.models import ConfirmEmailToken


@shared_task
def new_user_registered(user_id, **kwargs):
    """
    Отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()
