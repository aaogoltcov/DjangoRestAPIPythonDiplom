from rest_framework import serializers

from shop.models import Shop


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"
