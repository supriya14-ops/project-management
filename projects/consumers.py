import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()

class ProjectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.project_group_name = f'project_{self.project_id}'
        
        # Check if user has access to this project
        has_access = await self.check_project_access()
        if not has_access:
            await self.close()
            return
        
        # Join project group
        await self.channel_layer.group_add(
            self.project_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave project group
        await self.channel_layer.group_discard(
            self.project_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        
        if message_type == 'task_update':
            # Broadcast task update to project group
            await self.channel_layer.group_send(
                self.project_group_name,
                {
                    'type': 'task_update',
                    'task_id': text_data_json['task_id'],
                    'status': text_data_json['status'],
                    'user': self.scope['user'].username,
                }
            )
    
    async def task_update(self, event):
        # Send task update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'task_update',
            'task_id': event['task_id'],
            'status': event['status'],
            'user': event['user'],
        }))
    
    @database_sync_to_async
    def check_project_access(self):
        try:
            project = Project.objects.get(id=self.project_id)
            user = self.scope['user']
            return (user == project.owner or 
                   user in project.members.all())
        except Project.DoesNotExist:
            return False
