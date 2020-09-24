import jsonfield as jsonfield
from django.db import models

from user_account.models import User


class Shop(models.Model):
    """
    Модель магазина, который осуществялет прием заказов
    """
    name = models.CharField(max_length=50, verbose_name='Название магазина', unique=True)
    url = models.URLField(verbose_name='Ссылка на магазин', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Пользователь (представитель магазина)',
                                blank=True, null=True, on_delete=models.CASCADE)
    state = models.BooleanField(verbose_name='Статус приемки заказов', default=True)
    init_file_content = jsonfield.JSONField(verbose_name='Исходные данные при импорте', null=True, blank=True)
    # filename = models.FileField(verbose_name='Исходный файл при импорте', upload_to='uploads/', null=True, blank=True)
    filename = models.FilePathField(verbose_name='Исходный файл при импорте', path='uploads/', null=True, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Категории магазинов
    """
    name = models.CharField(max_length=40, verbose_name='Название', unique=True)
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        return self.name
