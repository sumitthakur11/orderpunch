


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

            data = requests.get('https://openapi.SAMCO.com/scrip-master/csv/NSE')

        if exchange=='NFO' :

            data = requests.get('https://openapi.SAMCO.com/scrip-master/csv/NFO')
       
        if exchange=='BSE'  :

            data = requests.get('https://openapi.SAMCO.com/scrip-master/csv/BSE')
        
        if exchange=='BFO' :

            data = requests.get('https://openapi.SAMCO.com/scrip-master/csv/BFO')
    





        
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









    

class SAMCOConnect(object):
    def __init__(self, api_key='', api_secret='', userid='',password=''):
        self.api = api_key
        self.secret = api_secret
        self.userid = userid
        self.password= password
        
      

 


    def login(self):
        requestBody={
                "userId" : self.userid,
                "password" : self.password
                }

        headers = {
        'Content-Type' : 'application/json',
        'Accept' : 'application/json'
        }

        r = requests.post('https://tradeapi.samco.in/login', 
        data=json.dumps(requestBody),
        headers = headers)

        r= r.json()
        checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='SAMCO').last()
        checktoken.AuthToken= r['sessionToken']
        checktoken.save()
        res= self.login2(checktoken)
        if res:
            self.login3()
        else:
            return None

        
        
    def login2(self,checktoken):

        # while True:   
                pasttime = time.time()

                if checktoken.AuthToken:
                    headers = {
                        'Accept': 'application/json',
                        'x-session-token': checktoken.AuthToken
                        }

                    response = requests.get('https://tradeapi.samco.in/webSecretCode'
                        ,headers = headers)
                    print (response.json()   )
                             


                    if response.status_code == 200  :
                        response_data = response.json()

                        if response_data.get("status").lower() == "success":

                            access_token = response_data["data"]["otp"]
                            checktoken.vendorcode = access_token
                        
                            checktoken.save()
                            return True    
                        else:
                            


                            logpathfron.error(f"Failed to generate access token: {response_data}")
                            return None
                    else:
                    

                        return None

              

    def login3(self):
        checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='SAMCO').last()
        
        requestBody={
                    "otp":checktoken.vendorcode
                                }

        headers = {
                'Content-Type' : 'application/json',
                'Accept' : 'application/json'
                }

        response = requests.post('https://tradeapi.samco.in/webSecretCodeValidation', 
        data=json.dumps(requestBody),
        headers = headers)
        print (response.json())

        if response.status_code == 200  :
                        response_data = response.json()

                        if response_data.get("status").lower() == "success":

                            access_token = response_data["sessionToken"]
                            checktoken.imei = access_token
                            checktoken.valid= True
                            checktoken.save()
                            return response_data    
                        else:
                            


                            logging.error(f"Failed to generate access token: {response_data}")
                            return None
        else:
                    

                        return None



    
        


    def loginsession(self):
            checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='SAMCO').last()
            
          

            return checktoken.imei
    





    

    
    
 

class HTTP(SAMCOConnect):
    
   
    def searchscrip(self,symbol,exchange,instrument):
        checktoken = md.Broker.objects.filter(user=1, brokername='SAMCO').last()

        # self.AuthToken=self.loginsession()


        headers = {
        'Accept': 'application/json',
        'x-session-token': checktoken.imei
        }

        r = requests.get('https://tradeapi.samco.in/eqDervSearch/search', params={
        'searchSymbolName': symbol,
        'exchange':exchange
        }, headers = headers)

        print (r.json())
        response= r.json()
        csv_data= response['searchResults']
        db= pd.DataFrame(csv_data)
        db=db.rename(columns={'tradingSymbol':'TradingSymbol','exchange':'exchange','quantityInLots':'lotsize'})
        if 'instrument' in db.columns:

            db= db[db['instrument']==instrument] 


        return db
    def checkfunds(self):
        # print(self.key,self.secret,self.passphrase)
        self.AuthToken=self.loginsession()

        try:

            headers = {
            'Accept': 'application/json',
            'x-session-token': self.AuthToken
            }

            balance = requests.get('https://tradeapi.samco.in/limit/getLimits'
            ,headers = headers)
            print (balance.json())
            balance=balance.json()
            if balance['status'].lower()=='success' :
                # return balance['data']['cash']['net'],None
                return balance['equityLimit']['netAvailableMargin'],None
            else:
                return None, balance

       
        except Exception as e :
            print(e)
            return None,e
    
    
    
    
    def cancel_order(self,variety,order_id):
            self.AuthToken=self.loginsession()

            headers = {
                'Accept': 'application/json',
                'x-session-token': self.AuthToken
                }

            balance = requests.delete('https://tradeapi.samco.in/order/cancelOrder', params={
                'orderNumber': order_id
                }, headers = headers)

            print( balance.json())
          
            if balance['status'].lower()=='success':
                return balance
            else :
                return balance
    
    
    def allholding(self):
        self.AuthToken=self.loginsession()

        try:

            headers = {
            'Accept': 'application/json',
            'x-session-token': self.AuthToken
            }

            balance = requests.get('https://tradeapi.samco.in/holding/getHoldings'
            , headers = headers)
            print( balance.json())
            balance= balance.json()
            if balance['status'].lower()=='success':
                
                listfin = []
                finddata ={}
                for i in balance['holdingDetails']:
                    finddata['tradingsymbol'] = i['tradingSymbol']
                    finddata['quantity'] = i['holdingsQuantity']
                    finddata['averageprice'] = i['averagePrice']
                    finddata['ltp'] = i['lastTradedPrice']
                    # finddata['profitandloss']=i['pnl']
                    finddata['totalprofitandloss']=balance['holdingSummary']['totalGainAndLossAmount']
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
        self.AuthToken=self.loginsession()

        try:
            
            headers = {
                'Accept': 'application/json',
                'x-session-token': self.AuthToken
                }

            balance = requests.get('https://tradeapi.samco.in/position/getPositions', params={
                'positionType': 'DAY'
                }, headers = headers)

            print( balance.json())
            balance= balance.json()
            findata= {}
            listfin= []
            if balance['status'].lower() == 'success':
                for i in balance['positionDetails']:
                    findata['exchange'] = i['exchange']
                    findata['tradingsymbol'] = i['tradingSymbol']
                    findata['buyavgprice'] = i['averagePrice']
                    findata['sellavgprice'] = i['debit_price']
                    findata['netqty'] = i['netQuantity']
                    findata['ltp'] = i['lastTradedPrice']
                    findata['realised']=i['realizedGainAndLoss']
                    findata['unrealised']=i['unrealizedGainAndLoss']
                    listfin.append(findata)
                    findata={}
                    print(listfin,'checklist')
            
                return listfin ,None
            else:
                        return None,'Not found'


        except Exception as e:
            print(e)
            return None,e
   
    
    

    def orderBook(self):
        self.AuthToken=self.loginsession()

        """
        Info :Get order status by order id  
        args: orderid 
        """
        try:
            
            headers = {
                'Accept': 'application/json',
                'x-session-token': self.AuthToken
                }

            balance = requests.get('https://tradeapi.samco.in/order/orderBook', headers = headers)
            print( balance.json())
            balance= balance.json()

            if balance['status'].lower() == 'success':
              
                
                return balance['orderBookDetails']
            else:
                return None


        except Exception as e:
            print(e)
            return None,e
    
    
    






    def placeorder(self,orderparam,orderobject):
        self.AuthToken=self.loginsession()

        try:
           
            exchange = orderparam['exchange']
            # tradingsymbol = orderparam['tradingsymbol']
            transaction_type = orderparam['transactiontype'] 
            quantity = orderparam['quantity']
            product = orderparam['product_type']
            order_type = orderparam['ordertype']
            validity = orderparam.get('validity', None)

            if order_type=='LIMIT':
                order_type='L'
            elif order_type=='MARKET':
                order_type='MKT'

            if product=='DELIVERY':
                product='CNC'
            elif product=='CARRYFORWARD':
                product='NRML'
            elif product=='INTRADAY':
                product='MIS'



            

            requestBody={ 
                        "symbolName":orderparam['tradingsymbol'],
                        "exchange":exchange,
                        "transactionType":transaction_type,
                        "orderType":order_type,
                        "quantity": str(quantity),
                        "disclosedQuantity":orderparam['discloseqty'],
                        "orderValidity":"DAY",
                        "productType":product,
                        "afterMarketOrderFlag":"NO",
                        "price":orderparam['ltp']
                        }
          
            headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'x-session-token': self.AuthToken
                    }

            result= requests.post('https://tradeapi.samco.in/order/placeOrder'
            , data=json.dumps(requestBody)
            , headers = headers)

            print (result.json())
            
            result= result.json()
            if result['status'].lower() == 'success':
                orderparam['orderid'] = result['orderNumber']  # Corrected from 'id'
                orderparam['lotsize']= 1 if not orderparam['lotsize'] else orderparam['lotsize']
                orderobject(orderparam)  # Call the callback function
                return result['orderNumber'], None
            else:
                return False, result.get('message', 'Order placement failed')

        except Exception as e:
            print(e)
            return False, str(e)

    def modifyorder(self,data,orderobject):
        self.AuthToken=self.loginsession()

        try:
            requestBody={
                    "orderType": data['ordertype'],
                    "quantity": data['quantity'],
                    "disclosedQuantity":  data['discloseqty'],
                    "orderValidity": "DAY",
                    "price": data['ltp'],
                    "triggerPrice": data['ltp']+1,
                    "marketProtection": "5"
                    }
            result = requests.put('https://tradeapi.samco.in/order/modifyOrder/{orderNumber}'
                        , data=json.dumps(requestBody)
                        , headers = headers)

            if result['status'].lower() == 'success':
                return result['data'], None
            else:
                return False, result.get('message', 'Order modification failed')

        except Exception as e:
            print(e)
            return False, str(e)
            


    
 



class WebSocketConnect(SAMCOConnect):
    def __init__(self, api_key='', request_token=''):
        super().__init__(api_key)
        self.api_key = api_key
        self.request_token = request_token
        self.ws_url = f"ws://inmob.SAMCO.com:7763/?api_key={api_key}&request_token={request_token}"
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
        logging.info("Successfully connected to SAMCO WebSocket")
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