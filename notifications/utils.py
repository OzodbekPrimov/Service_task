from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

def worker_group_name(service_type: str) -> str:
    return f"service_{service_type}"

def client_group_name(user_id: int) -> str:
    return f"user_{user_id}"


def notify_workers_new_order(order):
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        worker_group_name(order.service_type),
        {
            "type": "broadcast",
            "payload": {
                "kind": "new_order",
                "order_id": order.id,
                "service_type": order.service_type,
                "price": order.price,
                "status": order.status,
            },
        },
    )


def notify_client_order_event(client_id: int, order, event: str):
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        client_group_name(client_id),
        {
            "type": "broadcast",
            "payload": {
                "kind": event,
                "order_id": order.id,
                "status": order.status,
                "price": order.price,
            },
        },
    )