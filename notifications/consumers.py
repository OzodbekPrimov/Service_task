from channels.generic.websocket import AsyncJsonWebsocketConsumer
from users.models import Roles
from .utils import worker_group_name, client_group_name

class NotificationsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.groups_to_join = []
        if user.role == Roles.WORKER and hasattr(user, "worker_profile"):
            st = user.worker_profile.service_type
            self.groups_to_join.append(worker_group_name(st))
        self.groups_to_join.append(client_group_name(user.id))

        for g in self.groups_to_join:
            await self.channel_layer.group_add(g, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        for g in getattr(self, "groups_to_join", []):
            await self.channel_layer.group_discard(g, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "ping":
            await self.send_json({"type": "pong"})

    async def broadcast(self, event):
        await self.send_json(event.get("payload", {}))