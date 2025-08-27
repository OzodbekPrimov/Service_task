from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import WorkerProfile, ServiceType

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    service_type = serializers.ChoiceField(choices=ServiceType.choices, required=False)

    class Meta:
        model = User
        fields = ("username", "password", "role", "email", "first_name", "last_name", "service_type")

    def create(self, validated_data):
        service_type = validated_data.pop("service_type", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if user.role == "worker":
            if not service_type:
                raise serializers.ValidationError({"service_type": "Required for worker registration."})
            WorkerProfile.objects.create(user=user, service_type=service_type)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role")