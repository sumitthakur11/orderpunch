import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bot.settings')
django.setup()

from channels.generic.websocket import AsyncWebsocketConsumer
import pathlib
from . import models as md
path = pathlib.Path(__file__).parent.parent
sympath= os.path.join(path,'angel.json')
sympath= os.path.normpath(sympath)
print(sympath)
from asgiref.sync import sync_to_async


@sync_to_async
def get_watchlist_data():
    return list(md.watchlist.objects.filter(subscribe=True).values('tradingsymbol','ltp','volume','symboltoken','lotsize','broker','exchange','instrument'))



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        print("Received:", text_data)
        message= None
        text_data= json.loads(text_data)
        print(text_data)
        if text_data['message']=='LTPFEEDS':
            message= "connected"

            while True:
                try:
                    data = await get_watchlist_data()

                    print(data)

                    # if os.path.exists(sympath):
                    #     with open(sympath) as file:
                    #         data = json.load(file)

                    # else:
                    #     data= []
                except Exception as e :
                    print(e)
                    data=[]


                

                await self.send(text_data=json.dumps({
                "message": data
            }))



