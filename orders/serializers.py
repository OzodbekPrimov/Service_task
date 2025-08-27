from rest_framework import serializers
from .models import Order
from .utils import compute_price

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "service_type", "description", "price")
        read_only_fields = ("id", "price")

    def create(self, validated_data):
        user = self.context["request"].user
        # compute price based on service_type and description
        service_type = validated_data.get("service_type")
        description = validated_data.get("description", "")
        price = compute_price(service_type, description)
        return Order.objects.create(client=user, price=price, **validated_data)

class OrderListSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source="client.username", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "client", "client_username", "service_type", "description", "price", "status", "created_at")
        read_only_fields = fields