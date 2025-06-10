


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

            data = requests.get('https://openapi.stoxkart.com/scrip-master/csv/NSE')

        if exchange=='NFO' :

            data = requests.get('https://openapi.stoxkart.com/scrip-master/csv/NFO')
       
        if exchange=='BSE'  :

            data = requests.get('https://openapi.stoxkart.com/scrip-master/csv/BSE')
        
        if exchange=='BFO' :

            data = requests.get('https://openapi.stoxkart.com/scrip-master/csv/BFO')
    





        
        print(data)
        db= None
        csv_data = io.StringIO(data.text)
        db= pd.read_csv(csv_data,delimiter = ",",keep_default_na=False)
        print(db.head())
        print(db.columns)
      
        
       
            


        if instrument=='EQ':
            instrument='EQUITIES'
        if  name and instrument and exchange:
            db =db[db['exchange']==exchange]
            db =db[db['instrument_type']==instrument]
            db =db[db['symbol']==name]
        else:
            db =db[db['exchange']==exchange]
        


        db=db.rename(columns={'symbol_description':'TradingSymbol','exchange':'exchange','lot_size':'lotsize','token':'token','instrument_type':'instrument'})
        return db









    

class StoxkartConnect(object):
    def __init__(self, api_key='', api_secret='', userid='',password=''):
        self.api = api_key
        self.secret = api_secret
        self.userid = userid
        self.password= password
        
      

 


    def login(self):
        login_url = f"https://superrtrade.stoxkart.com/login?api_key={self.api}"
        checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='STOXKART').last()
        checktoken.vendorcode = None
        checktoken.url = login_url
        checktoken.save()
        pasttime = time.time()

        while True:
            self.login2()
            current= time.time()
            diff= current-pasttime
            if int(diff)>=400:
                return None
        
    def login2(self):

        # while True:   

                checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='STOXKART').last()
                if checktoken.vendorcode:
                    url = "https://preprod-openapi.stoxkart.com/auth/token"
                    headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    
                    }

                    token= self.api+checktoken.vendorcode
                    hashed_data = hashlib.sha256(token.encode()).hexdigest()
        
                    key1 = bytes(self.api + checktoken.vendorcode, 'UTF-8')
                    key2 = bytes(self.secret, 'UTF-8')        

              
                    signature = hmac.new(key1, key2, hashlib.sha256).hexdigest()
                    print(signature)

                    data = {
                        "api_key": self.api,
                        "signature": signature,
                        "req_token": checktoken.vendorcode,
                        }


                    response = requests.post(url, json=data, headers=headers)
                    print(response.json())
                    
                    if response.status_code == 200  :
                        response_data = response.json()

                        if response_data.get("status") == "success":

                            access_token = response_data["data"]["access_token"]
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

                

    def login3(self):
        print(self.api)
        data = {
                "platform": "api",

                "data": {
                    "client_id": self.userid ,
                    "password": self.password,
                
                }
                }
        print(data)
        print(self.password)
        

        
        checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='STOXKART').last()
        
        url = f"https://preprod-openapi.stoxkart.com/auth/login?api-key={self.api}"
        headers = {
                    "Content-Type": "application/json",
                    "Accept-Type": "application/json",
                    # "X-Api-Key":self.api,
                    "X-Platform":'api',
                    # "X-Access-Token":checktoken.imei


                    }
        response = requests.post(url, json=data, headers=headers)
        print(response.json())
        if response.status_code==200 :
            response=response.json()
            if response['status'].lower()=='success':
                checktoken.vendorcode= response['data']['token']
                checktoken.save()
                self.validate_2fa(response['data']['token'],checktoken)
    

    def validate_2fa(self, token,checktoken):
        otp = pyotp.TOTP('ZP462I7OEGPXFQRN').now()
        print(otp)
        params = {
            "platform": "api",
            "data": {
            "client_id":  self.userid,
            "password": self.password,
            "api-key":self.api,
            "req_token": token,
            "action": "api-key-validation",
            "totp": otp
            
            }
        }     
        print(params)
        url = f"https://preprod-openapi.stoxkart.com/auth/twofa/verify?api-key={self.api}"
        headers = {
                    "Content-Type": "application/json",
                    "Accept-Type": "application/json",
                    "X-Access-Token":checktoken.imei,
                                "client_id":  self.userid,
                                "password": self.password,
                                "api-key":self.api,
                                "req_token": token,
                                'x-api-key':self.api,
                                'x-api-secret':self.secret,




                    "X-Platform":'api',
                    }
        data = requests.post(url, json=params, headers=headers)
        print(data.json())

        if data.status_code==200 :
            print(data)

            data = data.json()
            if data['status'].lower()=='success':
                print(data)
                requestToken = data["data"]["request_token"]
                checktoken.imei=requestToken
                checktoken.save()
        
        


    def loginsession(self):
            checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='STOXKART').last()
            headers = {
                "X-Access-Token": f"Bearer {checktoken.imei}",
                "Content-Type": "application/json",
                "Accept-Type":"application/json",
                "X-Platform":"api",
                "X-Api-Key":self.api,
                "request_token" : checktoken.vendorcode,
                "x-session" : "{}:{}".format(checktoken.apikey, checktoken.imei),





            }

          

            return headers 
    





    

    
    
 

class HTTP(StoxkartConnect):
    
   
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
            url ='https://preprod-openapi.stoxkart.com/funds'
            session =self.loginsession()
            print(session)
            balance= requests.get(url,headers= session)
            balance= balance.json()
            print(balance)
            if balance['status']=='success' :
                # return balance['data']['cash']['net'],None
                return balance['data']['available_limit']
            else:
                return None, balance

       
        except Exception as e :
            print(e)
            return e
    
    
    
    
    def cancel_order(self,variety,order_id):
            url =f'https://preprod-openapi.stoxkart.com/{variety}/{order_id}'
            data = {}
            data ['']
            session =self.loginsession()
            print(session)
            balance= requests.delete(url,headers= session)
            balance= balance.json()
            if balance['status']=='success':
                return balance
            else :
                return balance
    
    
    def allholding(self):
        try:

            url ='https://preprod-openapi.stoxkart.com/portfolio/holdings'
            session =self.loginsession()
            print(session)
            balance= requests.get(url,headers= session)
            balance= balance.json()
            if balance['status']=='success':
                
                listfin = []
                finddata ={}
                for i in balance['data']:
                    finddata['tradingsymbol'] = i['symbol']
                    finddata['quantity'] = i['quantity']
                    finddata['averageprice'] = i['average_price']
                    finddata['ltp'] = i['last_trade_price']
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
            
            url ='https://preprod-openapi.stoxkart.com/portfolio/positions'
            listfin= []
            findata= {}          
            
            session =self.loginsession()

            balance = requests.get(url, headers=session)
            balance = balance.json()
            
            if balance['status'] == 'success':
                for i in balance['data']:
                    # findata['tradingsymbol'] = i['tradingsymbol']
                    findata['quantity'] = i['net_quantity']
                    findata['averageprice'] = i['net_average_price']
                    findata['ltp'] = i['last_trade_price']
                    findata['profitandloss']=i['pnl']
                    # findata['totalprofitandloss']==i.get('total_pl')
                    # findata['totalpnlpercentage']=i.get('pnl_percentage')
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
            
            url ='https://preprod-openapi.stoxkart.com/reports/order-book'
            listfin= []
            findata= {}          
            
            session =self.loginsession()

            balance = requests.get(url, headers=session)
            balance = balance.json()
            
            if balance['status'] == 'success':
                for i in balance['data']:
                    findata['tradingsymbol'] = i['symbol']
                    findata['quantity'] = i['quantity']
                    findata['averageprice'] = i['trade_average_price']
                    # findata['ltp'] = i['last_price']
                    # findata['profitandloss']=i['pnl']
                    # findata['totalprofitandloss']==i.get('total_pl')
                    # findata['totalpnlpercentage']=i.get('pnl_percentage')
                    listfin.append(findata)
                    findata={}
                    print(listfin,'checklist')
            
                return listfin ,None
            else:
                return None,'Not found'


        except Exception as e:
            print(e)
            return None,e
    
    
    






    def placeorder(self,orderparam,orderobject,variety):
        try:
            url = f'https://preprod-openapi.stoxkart.com/orders/{variety}'
            session =self.loginsession()

            exchange = orderparam['exchange']
            # tradingsymbol = orderparam['tradingsymbol']
            transaction_type = orderparam['transaction_type'] 
            quantity = orderparam['quantity']
            product = orderparam['product_type']
            order_type = orderparam['order_type']
            validity = orderparam.get('validity', None)
            
            data = {
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
            url = f'https://preprod-openapi.stoxkart.com/orders/{variety}/{order_id}'
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
            


    
 



class WebSocketConnect(StoxkartConnect):
    def __init__(self, api_key='', request_token=''):
        super().__init__(api_key)
        self.api_key = api_key
        self.request_token = request_token
        self.ws_url = f"ws://inmob.stoxkart.com:7763/?api_key={api_key}&request_token={request_token}"
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
        logging.info("Successfully connected to Stoxkart WebSocket")
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