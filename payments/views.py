import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import PaymentRequestSerializer, PaymentSerializer
from .models import PaymentStatus, Payment
from orders.models import OrderStatus
from notifications.utils import notify_client_order_event
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class FakePayView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Initiate fake payment",
        operation_description="Creates a fake payment for the given order. Optionally force outcome: success, failed, or canceled.",
        request_body=PaymentRequestSerializer,
        responses={201: openapi.Response("Created", PaymentSerializer)},
        tags=["Payments"],
    )
    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data["order"]
        outcome = serializer.validated_data.get("outcome") or random.choice([
            PaymentStatus.SUCCESS, PaymentStatus.FAILED, PaymentStatus.CANCELED
        ])

        payment = Payment.objects.create(
            order=order,
            amount=order.price,
            status=outcome,
        )

        if outcome == PaymentStatus.SUCCESS:
            order.status = OrderStatus.PAID
            event = "payment_success"
        elif outcome == PaymentStatus.CANCELED:
            order.status = OrderStatus.CANCELED
            event = "payment_canceled"
        else:
            event = "payment_failed"  # pending hold
        order.save(update_fields=["status", "updated_at"])

        notify_client_order_event(order.client_id, order, event=event)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)