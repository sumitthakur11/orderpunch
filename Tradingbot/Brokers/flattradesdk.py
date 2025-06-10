

import asyncio
import base64
import hashlib
import hmac
import json
import logging
from random import random
import time
from urllib.parse import urljoin
import uuid
import requests
import websockets
import websocket
import threading
from concurrent.futures import ThreadPoolExecutor
import pyotp
import pandas as pd
from Tradingbot import models as md
import sys
import yaml
import zipfile
import io
from Tradingbot import env
from datetime import datetime, timedelta
import os 
from pathlib import Path
import pathlib


path = pathlib.Path(__file__).resolve().parent.parent.parent
# import ThreadPoolExecutor
log = logging.getLogger(__name__)


logging.basicConfig(level=logging.DEBUG)


#   


logger2path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpathfron= os.path.normpath(logger2path)
logpathfron=env.setup_logger(logpathfron)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def searchscrip (name,exchange='NFO',instrument=''):
        print(name,exchange,instrument)

        if exchange=='NSE':

            data = requests.get('https://flattrade.s3.ap-south-1.amazonaws.com/scripmaster/NSE_Equity.csv')

        if exchange=='NFO' and (instrument=='FUTSTK' or instrument=='OPTSTK'):

            data = requests.get('https://flattrade.s3.ap-south-1.amazonaws.com/scripmaster/Nfo_Equity_Derivatives.csv')
        if exchange=='NFO' and  (instrument=='FUTIDX' or instrument=='OPTIDX'):

            data = requests.get('https://flattrade.s3.ap-south-1.amazonaws.com/scripmaster/Nfo_Index_Derivatives.csv')
        if exchange=='BSE'  :

            data = requests.get('https://flattrade.s3.ap-south-1.amazonaws.com/scripmaster/BSE_Equity.csv')
        
        if exchange=='BFO' and  (instrument=='FUTIDX' or instrument=='OPTIDX'):

            data = requests.get('https://flattrade.s3.ap-south-1.amazonaws.com/scripmaster/Bfo_Index_Derivatives.csv')
        if exchange=='BFO' and  (instrument=='FUTSTK' or instrument=='OPTSTK'):

            data = requests.get('https://flattrade.s3.ap-south-1.amazonaws.com/scripmaster/Bfo_Equity_Derivatives.csv')
        





        
        print(data)
        db= None
        csv_data = io.StringIO(data.text)
        db= pd.read_csv(csv_data,delimiter = ",",keep_default_na=False)
        print(db.head())
        print(db.columns)
      
        
       
            


        # if instrument=='EQ':
        #     instrument=''
        if  name and instrument and exchange:
            db =db[db['Exchange']==exchange]
            db =db[db['Instrument']==instrument]
            db =db[db['Symbol']==name]
        else:
            db =db[db['Exchange']==exchange]
        


        db=db.rename(columns={'Tradingsymbol':'TradingSymbol','Exchange':'exchange','Lotsize':'lotsize','Token':'token','Instrument':'instrument'})
        return db








path = pathlib.Path(__file__).resolve().parent.parent.parent
# import ThreadPoolExecutor
log = logging.getLogger(__name__)


logging.basicConfig(level=logging.DEBUG)


#   


logger2path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpathfron= os.path.normpath(logger2path)
logpathfron=env.setup_logger(logpathfron)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


    

class FlattradeConnect(object):
    def __init__(self, api_key='', api_secret='', userid='',password=''):
        self.api = api_key
        self.secret = api_secret
        self.userid = userid
        self.password= password
        
        
      

 


    def login(self):
        login_url = f"https://auth.flattrade.in/?app_key={self.api}"
        checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='FLATTRADE').last()
        checktoken.AuthToken = None
        checktoken.url = login_url
        checktoken.save()
        pasttime = time.time()

        # while True:
        #     self.login2()

        #     current= time.time()
        #     diff= current-pasttime
        #     if int(diff)>=400:
        #                 return None
        
    def login2(self):

        # while True:   
                

                checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='FLATTRADE').last()
                if checktoken.AuthToken:
                    url = "https://authapi.flattrade.in/trade/apitoken"
                    headers = {
                    "Content-Type": "application/json",
                    
                    }

                  
                    enkey= f"{self.api}{checktoken.AuthToken}{self.secret}"
                    key1 = hashlib.sha256(enkey.encode()).hexdigest()
                    print(self.api,self.secret,checktoken.AuthToken[-5:])
              
                    signature =  hashlib.sha256(key1.encode()).hexdigest()

                    data = {
                        "api_key": self.api,
                        "request_code": checktoken.AuthToken,
                        "api_secret": signature,
                        }


                    response = requests.post(url, json=data,headers=headers)
                    print(response.text)
                    print(response.json())
                    
                    if response.status_code == 200  :
                        response_data = response.json()

                        if response_data.get("status") == "Ok":

                            access_token = response_data["token"]
                            checktoken.imei = access_token
                            checktoken.valid = True
                            checktoken.save()
                            return response_data    
                        else:
                            response_data = response.text
                            checktoken.valid = False
                            checktoken.save()


                            logging.error(f"Failed to generate access token: {response_data}")
                            return None
                    else:
                        checktoken.valid = False
                        checktoken.save()

                        return None

               

    


    def loginsession(self):
            checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='Flattrade').last()
            headers = {
                "X-Access-Token": f"Bearer {checktoken.imei}",
                "Content-Type": "application/json",
                "Accept-Type":"application/json",
                "X-Platform":"api",
                "X-Api-Key":self.api



            }

          

            return headers 
    





    

    
    
 

class HTTP(FlattradeConnect):
    
   
    def checkfunds(self):
        # print(self.key,self.secret,self.passphrase)
        try:

            """Get a list of accounts.

            Required args:
                None
            """
            """"api endpoint to fetch balance and account detail
            *kwargs: symbol (not mandatory)
            
            """
            url ='https://piconnect.flattrade.in/PiConnectTP/Limits'
            session,key =self.loginsession()
            print(session)
            data= dict()
            data['jKey']= key
            data['jData']={'uid':self.user,"actid":self.user}

            balance= requests.post(url,json=data,headers= session)

            if balance.status_code==200:

                balance= balance.json()
                print(balance)
                if balance['stat']=='Ok' :
                    return balance['data']['cash']
                else:
                    return None, balance
            else:
                return None, balance

       
        except Exception as e :
            print(e)
            return None, e
    
    
    
    
    def cancel_order(self,variety,order_id):
            url =f'https://piconnect.flattrade.in/PiConnectTP/CancelOrder'
            data = {}
            session ,key=self.loginsession()
            data['jKey']= key
            data['jData']={'uid':self.user,"norenordno":order_id}

            print(session)
            balance= requests.delete(url,json=data,headers= session)
            balance= balance.json()
            if balance['stat']=='Ok':
                return balance
            else :
                return balance
    
    
    def allholding(self):
        try:

            url ='https://piconnect.flattrade.in/PiConnectTP/Holdings'
            session ,key=self.loginsession()
            data['jKey']= key
            data['jData']={'uid':self.user,'actid':self.user,'prd':'H'}


            print(session)
            balance= requests.get(url,headers= session)
            balance= balance.json()
            if balance['stat']=='Ok':
                
                listfin = []
                finddata ={}
                for i in balance:
                    finddata['tradingsymbol'] = i['exch_tsym']['tsym']
                    finddata['quantity'] = i['holdqty']
                    finddata['averageprice'] = i['upldprc']
                    # finddata['profitandloss']=i['pnl']
                    # finddata['totalprofitandloss']=i.get('total_pl')
                    # finddata['totalpnlpercentage']=i.get('pnl_percentage')
                    
                    listfin.append(finddata)
                    finddata={}
                return listfin,None
            else :
                return None, balance.get('notfound')


        except Exception as e:
            print(e)
            return None,e

    def getposition(self):
        try:
            
            url ='https://piconnect.flattrade.in/PiConnectTP/PositionBook'
            listfin= []
            findata= {}          
            
            session =self.loginsession()
            data = {}
            data['jKey']= key

            data['jData']={'uid':self.user,'actid':self.user}


            balance = requests.get(url,json=data, headers=session)
            balance = balance.json()
            
            if balance['stat'] == 'Ok':
                for i in balance:
                    findata['tradingsymbol'] = i['tsym']
                    findata['quantity'] = i['netqty']
                    findata['averageprice'] = i['totsellavgprc']
                    findata['ltp'] = i['lp']
                    findata['unrealised'] = i['urmtom']
                    findata['realised'] = i['rpnl']

                    listfin.append(findata)
                    findata={}
                    print(listfin,'checklist')
            
                return listfin ,None
            else:
                        return None,'Not found'


        except Exception as e:
            print(e)
            return None,e
   
    
    

    def orderbook(self,orderid):
        """
        Info :Get order status by order id  
        args: orderid 
        """
        try:
            
            url ='https://piconnect.flattrade.in/PiConnectTP/OrderBook'
            listfin= []
            findata= {}          

            data = {}
            session,key=self.loginsession()
            data['jKey']= key

            data['jData']={'uid':self.user}

            balance = requests.get(url, headers=session)
            balance = balance.json()
            
            if balance['stat'] == 'Ok':
              
            
                return balance ,None
            else:
                return None,'Not found'


        except Exception as e:
            print(e)
            return None,e
    
    
    






    def placeorder(self,orderparam,orderobject,variety):
        try:
            url = f'https://piconnect.flattrade.in/PiConnectTP/PlaceOrder'
            session ,key=self.loginsession()
            data['jKey']= key

            exchange = orderparam['exchange']
            # tradingsymbol = orderparam['tradingsymbol']
            transaction_type = orderparam['transaction_type'] 
            quantity = orderparam['quantity']
            product = orderparam['product_type']
            order_type = orderparam['order_type']
            validity = orderparam.get('validity', None)
            
            data['jData'] = {
            'uid':self.user,
            'actid':self.user,
            'exchange': exchange,
            # 'tradingsymbol': tradingsymbol,
            'transaction_type': transaction_type,
            'quantity': str(quantity),  
            'product': product,
            'order_type': order_type,
            
            'validity': validity,
        }
            
            response = requests.post(url, headers=session, data=data)
            result = response.json()
            if result['status'] == 'success':
                orderparam['orderid'] = result['data']['order_id']  # Corrected from 'id'
                orderobject(orderparam)  # Call the callback function
                return result['data'], None
            else:
                return False, result.get('message', 'Order placement failed')

        except Exception as e:
            print(e)
            return False, str(e)

    def modifyorder(self, variety, order_id, parent_order_id=None, quantity=None,
                price=None, order_type=None, 
                trigger_price=None, validity=None, disclosed_quantity=None):
        try:
            url = f'https://piconnect.flattrade.in/PiConnectTP/ModifyOrder'
            session = self.loginsession() 
            data = {}
            if parent_order_id is not None:
                data['parent_order_id'] = parent_order_id
            if quantity is not None:
                data['quantity'] = str(quantity)  
            if price is not None:
                data['price'] = str(price)
            if order_type is not None:
                data['order_type'] = order_type
            if trigger_price is not None:
                data['trigger_price'] = str(trigger_price)
            if validity is not None:
                data['validity'] = validity
            if disclosed_quantity is not None:
                data['disclosed_quantity'] = str(disclosed_quantity)

            response = requests.put(url, headers=session, data=data)
            result = response.json()

            if result['status'] == 'success':
                return result['data'], None
            else:
                return False, result.get('message', 'Order modification failed')

        except Exception as e:
            print(e)
            return False, str(e)
            


    
 



class WebSocketConnect(FlattradeConnect):
    def __init__(self, api_key='', request_token=''):
        super().__init__(api_key)
        self.api_key = api_key
        self.request_token = request_token
        self.ws_url = f"ws://inmob.Flattrade.com:7763/?api_key={api_key}&request_token={request_token}"
        self.tokens = [11536]
        self.ws = None
        self.setup_logging()
        self.connect()
        kws = KiteTicker(api_key, self.token)

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if 'MsgCode' in data:
                if data['MsgCode'] == 61: 
                    logging.info(f"LTP Data: {data}")
                else:
                    logging.info(f"Received message with MsgCode {data['MsgCode']}: {data}")
            else:
                logging.info(f"Received message: {data}")
        except json.JSONDecodeError:
            logging.error("Failed to parse message as JSON")

    def on_open(self, ws):
        logging.info("Successfully connected to Flattrade WebSocket")
        # Subscribe to tokens
        for token in self.tokens:
            subscribe_request = {
                "MsgCode": 72,  
                "exchange": "NSE", 
                "token": str(token)
            }
            ws.send(json.dumps(subscribe_request))
            logging.info(f"Subscribed to token: {token}")

    def on_close(self, ws, code, reason):
        logging.info(f"Connection closed: {code} - {reason}")

    def on_error(self, ws, error):
        logging.error(f"Connection error: {error}")
    def on_reconnect(ws, attempts_count):
            logging.info("Reconnecting: {}".format(attempts_count))

    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error
        )
        self.ws.run_forever()

    def change_mode(self):
        
        pass

    if __name__ == "__main__":

        api_key = ""  
        request_token = ""  
        ws_client = WebSocketConnect(api_key, request_token)
        
        count = 0
        while True:
            count += 1
            if count % 2 == 0:
                logging.info("### Set mode to LTP for all tokens")
                ws_client.change_mode()
            else:
                logging.info("### Set mode to quote for all tokens")
                ws_client.change_mode()
            time.sleep(5)