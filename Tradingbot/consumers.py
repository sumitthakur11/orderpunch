import json
from channels.generic.websocket import AsyncWebsocketConsumer
import pathlib
import os
path = pathlib.Path(__file__).parent.parent
sympath= os.path.join(path,'angel.json')
sympath= os.path.normpath(sympath)
print(sympath)

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

                    if os.path.exists(sympath):
                        with open(sympath) as file:
                            data = json.load(file)

                    else:
                        data= []
                except Exception as e :
                    print(e)
                    data=[]


                

                await self.send(text_data=json.dumps({
                "message": data
            }))



