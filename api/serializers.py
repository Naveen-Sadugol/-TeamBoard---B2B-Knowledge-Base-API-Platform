from django.contrib.auth.models import User
from rest_framework import serializers

from .models import KBEntry


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    company_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class QuerySerializer(serializers.Serializer):
    search = serializers.CharField(allow_blank=False)

    def validate_search(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Search field cannot be blank.")
        return cleaned


class KBEntrySerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = KBEntry
        fields = ["id", "question", "answer", "category"]
