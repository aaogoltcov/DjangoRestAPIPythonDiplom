from django.contrib.auth.models import User
from rest_framework import serializers

from user_account.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'company', 'position', 'city', 'street', 'house',
                  'structure', 'building', 'apartment', 'user', 'phone', 'type')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'profile')
        read_only_fields = ('id',)
