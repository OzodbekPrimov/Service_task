from rest_framework import serializers
from .models import Payment, PaymentStatus
from orders.models import Order, OrderStatus

class PaymentRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    outcome = serializers.ChoiceField(choices=["success", "failed", "canceled"], required=False)

    def validate(self, attrs):
        order_id = attrs["order_id"]
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Order not found"})
        attrs["order"] = order
        if order.status != OrderStatus.PENDING:
            raise serializers.ValidationError({"order_id": "Order is not pending"})
        return attrs

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "order", "amount", "status", "created_at")