

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .views import ask_open_weather_forecast_and_openai

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Processar a mensagem do usuário e enviar de volta o conteúdo gerado
        # Use OpenAI ou qualquer outra lógica necessária aqui
        response_content = await sync_to_async(ask_open_weather_forecast_and_openai)(text_data, date_solicited=None, hora_solicitada=None)

        # Enviar a resposta de volta para o cliente via WebSocket
        await self.send(text_data=json.dumps({
            'message': response_content
        }))
