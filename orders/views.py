from rest_framework import viewsets, mixins, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import QuerySet
from .models import Order, OrderStatus
from .serializers import OrderCreateSerializer, OrderListSerializer
from users.models import Roles
from notifications.utils import notify_workers_new_order, notify_client_order_event
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class OrderViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderListSerializer

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        qs = super().get_queryset()
        if user.role == Roles.ADMIN:
            return qs
        if user.role == Roles.CLIENT:
            return qs.filter(client=user)
        if user.role == Roles.WORKER and hasattr(user, "worker_profile"):
            st = user.worker_profile.service_type
            return qs.filter(service_type=st)
        return qs.none()

    def perform_create(self, serializer):
        order = serializer.save()
        notify_workers_new_order(order)

    @swagger_auto_schema(
        operation_summary="Create a new order",
        operation_description="Create an order as a client. Workers/Admins typically don't create orders.",
        request_body=OrderCreateSerializer,
        responses={201: openapi.Response("Created", OrderListSerializer)},
        tags=["Orders"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List orders",
        operation_description="List orders visible to the current user. Admins see all, clients see their own, workers see orders matching their service type.",
        responses={200: openapi.Response("OK", OrderListSerializer(many=True))},
        tags=["Orders"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve order",
        operation_description="Retrieve a single order if visible to the current user.",
        responses={200: openapi.Response("OK", OrderListSerializer)},
        tags=["Orders"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @decorators.action(detail=True, methods=["post"], url_path="cancel")
    @swagger_auto_schema(
        operation_summary="Cancel order",
        operation_description="Cancel a pending order. Only Admins and the owning Client can cancel.",
        responses={200: openapi.Response("OK", OrderListSerializer), 400: "Only pending orders can be canceled.", 403: "Not allowed."},
        tags=["Orders"],
    )
    def cancel(self, request, pk=None):
        order = self.get_object()
        user = request.user
        if order.status != OrderStatus.PENDING:
            return Response({"detail": "Only pending orders can be canceled."}, status=400)
        if user.role not in [Roles.ADMIN, Roles.CLIENT] or (user.role == Roles.CLIENT and order.client != user):
            return Response({"detail": "Not allowed."}, status=403)
        order.status = OrderStatus.CANCELED
        order.save(update_fields=["status", "updated_at"])
        notify_client_order_event(order.client_id, order, event="order_canceled")
        return Response(OrderListSerializer(order).data)