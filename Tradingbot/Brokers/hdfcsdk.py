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
# from selenium import webdriver
from random import randint
from Tradingbot import models as md
import pandas as pd 
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import io
import zipfile
from datetime import datetime, timedelta
# import ThreadPoolExecutor
log = logging.getLogger(__name__)
import os 

logging.basicConfig(level=logging.DEBUG)


def searchscrip (name,exchange='NFO',instrument=''):
        print(name,exchange,instrument)

        params = {
                    'info': 'download',
                    
                }

        headers = {
                    "authority": "hdfcsky.com",
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "referer": "https://hdfcsky.com/",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    # Include this if you're logged in:
                    # "cookie": "sessionid=xyz; other-cookie=abc"
                }

        data = requests.get('https://hdfcsky.com/api/v1/contract/Compact', params=params,headers=headers)

    
        # with open("contract.zip", "wb") as f:
        #     f.write(data.content)

        with zipfile.ZipFile("contract.zip", 'r') as zip_ref:
            zip_ref.extractall("extracted")
            print("Files extracted:", zip_ref.namelist())
                    

        db = pd.read_csv(os.path.join("extracted", 'CompactScrip.csv'))

      
        # print(db.head())
        # print(db.columns)
        
       
        if  name and instrument and exchange:
            db =db[db['exchange']==exchange]
            db =db[db['instrument_name']==instrument]

            print(db.head())
            print(set(db['company_name'].str.split().str[0]))
            db =db[db['company_name'].str.split().str[0]==name]
            # print(db.head())

        else:
            db =db[db['exchange']==exchange]
        db = db.fillna('')  # or any default value
        


        db=db.rename(columns={'trading_symbol':'TradingSymbol','exchange':'exchange','lot_size':'lotsize','exchange_token':'token','instrument_name':'instrument'})
        return db











    

class HDFCSkyConnect(object):
    def __init__(self, api_key='', api_secret='', client_id=''):
        self.api = api_key
        self.secret = api_secret
        self.userid = client_id
        self.client_id = client_id
      

    


    def login(self):
        


        self.url= f'https://developer.hdfcsky.com/oapi/v1/login?api_key={self.api}'



        checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='HDFC').last()
        checktoken.AuthToken = None
        checktoken.url = self.url
        checktoken.save()
        pasttime = time.time()
        while True:
            
            self.login2()
            
            current= time.time()
            diff= current-pasttime
            if int(diff)>=400:
                return None

    def login2(self):
                checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='HDFC').last()
                if checktoken.AuthToken:
                    headers = {
                                'Content-Type': 'application/json',
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                            }
                    params = {
                                    'api_key': self.api,
                                    'request_token': checktoken.AuthToken,
                                }
                    data = {
                        "apiSecret": self.secret
                        }

                        
                    
                    response = requests.post(f'https://developer.hdfcsky.com/oapi/v1/access-token?api_key={self.api}&request_token={checktoken.AuthToken}', headers=headers, json=data)
                 
                   
                    print(response)
                    if response.status_code == 200:
                        response_data = response.json()

                        access_token = response_data["access_token"]
                        checktoken.imei = access_token
                        checktoken.valid = True
                        checktoken.save()
                        return response_data
                    else:
                        logging.error(f"Failed to generate access token: {response_data}")
                        return None
                
               

            

                


    def loginsession(self):
            checktoken = md.Broker.objects.filter(user=1, accountnumber=self.userid, brokername='HDFC').last()
            headers = {
                "Authorization": f"{checktoken.imei}",
                "Content-Type": "application/json",
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',

                # "x-api-key": self.api
            }

            # if checktoken.imei: 

            #     session = KiteConnect(api_key=self.api)
            #     data = self.kite.generate_session(checktoken.AuthToken, api_secret=self.secret)

            #     session=self.kite.set_access_token(checktoken.AuthToken)
            #     print(dir(session))
            #     # checktoken.imei= data["access_token"]
            #     checktoken.valid=True
            #     checktoken.save()
            #     return session
            # else:
            #     checktoken.valid=True
            #     checktoken.save()

            return headers 
    





    

    
    
 

class HTTP(HDFCSkyConnect):
    
   
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
            url =f'https://developer.hdfcsky.com/oapi/v1/funds/view?api_key={self.api}&client_id={self.client_id}&type=all'
            session =self.loginsession()
            
            balance= requests.get(url,headers= session)
            if balance.status_code==200:

                balance= balance.json()
                if balance['status']=='success' :
                    # return balance['data']['cash']['net'],None
                    return balance['data']['values'][0][1],None
                else:
                    return None, balance
            else:
                return None, balance

       
        except Exception as e :
            print(e)
            return e
    
    
    
    
    def cancel_order(self,order_id, execution_type):
            url =f'https://developer.hdfcsky.com/oapi/v1/orders/{order_id}?api_key={self.api}&client_id={self.client_id}&execution_type={execution_type}'
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

            url =f'https://developer.hdfcsky.com/oapi/v1/holdings?api_key={self.api}&client_id={self.client_id}'
            session =self.loginsession()
            print(session)
            balance= requests.get(url,headers= session)
            if balance.status_code==200:
                
                balance= balance.json()
                print(balance)
                if balance['status']=='success':
                    
                    listfin = []
                    finddata ={}
                    for i in balance['data']:
                        finddata['tradingsymbol'] = i['trading_symbol']
                        finddata['quantity'] = i['quantity']
                        finddata['averageprice'] = i['buy_avg']
                        finddata['ltp'] = i['ltp']
                        # finddata['profitandloss']=i['pnl']
                        # finddata['totalprofitandloss']=i.get('total_pl')
                        # finddata['totalpnlpercentage']=i.get('pnl_percentage')
                        
                        listfin.append(finddata)
                        finddata={}
                    return listfin,None
                else:
                     return None, balance.get('notfound')
            else :
                return None, balance.get('notfound')


        except Exception as e:
            print(e)
            return None,e

    def getposition(self):
        try:
            
            url =f'https://developer.hdfcsky.com/oapi/v1/positions?api_key={self.api}&client_id={self.client_id}&type={self.type}'
            listfin= []
            findata= {}          
            
            session =self.loginsession()

            balance = requests.get(url, headers=session)
            if balance.status_code==200:

                balance = balance.json()
                
                if balance['status'] == 'success':
                    for i in balance['data']:
                        findata['tradingsymbol'] = i['trading_symbol']
                        findata['quantity'] = i['net_quantity']
                        findata['averageprice'] = i['average_price']
                        findata['ltp'] = i['ltp']
                        # findata['profitandloss']=i['pnl']
                        # findata['totalprofitandloss']==i.get('total_pl')
                        # findata['totalpnlpercentage']=i.get('pnl_percentage')
                        listfin.append(findata)
                        findata={}
                        print(listfin,'checklist')
                
                    return listfin ,None
                else:
                        return None,'Not found'


            else:
                        return None,'Not found'


        except Exception as e:
            print(e)
            return None,e
   
    
    

    def orderBook(self):
        """
        Info :Get order status by order id  
        args: orderid 
        """
        try:
            
            url =f'https://developer.hdfcsky.com/oapi/v1/orders?type=completed&client_id={self.client_id}&api_key={self.api}'
            listfin= []
            findata= {}          
            
            session =self.loginsession()

            balance = requests.get(url, headers=session)
            if balance.status_code==200:

                balance = balance.json()
                print(balance)
        
            
                return balance['data']['orders']
            else:
                return None


        except Exception as e:
            print(e)
            return None,e
    
    
    






    def placeorder(self,orderparam,orderobject):
        try:
            url = f'https://developer.hdfcsky.com/oapi/v1/orders?api_key={self.api}'
            session =self.loginsession()

            exchange = orderparam['exchange']
            # tradingsymbol = orderparam['order_side']
            transaction_type = orderparam['transactiontype'] 
            quantity = orderparam['quantity']
            product = orderparam['product_type']
            order_type = orderparam['ordertype']
            validity = orderparam.get('validity', None)
            if product=='INTRADAY':
                product= 'MIS'
            if product=='DELIVERY':
                product='CNC'

            if product=='CARRYFORWARD':
                product='NRML'

            


            data = {
                'exchange': exchange,
                'instrument_token': orderparam['symboltoken'],   
                'client_id':self.client_id,
                'order_type': order_type,
                'amo':False,
                "price":float( orderparam['ltp']),
                'quantity': int(quantity),  
                'disclosed_quantity':int(orderparam['discloseqty']),
                "validity":"DAY",
                'product': product,
                "order_side": transaction_type,
                "device": "WEB",
                "user_order_id":int(time.time())*1000,
                'trigger_price':0,
                'execution_type':'REGULAR',
                'source':'API'






        }
            
            print(data)
            response = requests.post(url, headers=session, json=data)
            result = response.json()
            print(result)
            if result['status'] == 'success':
                orderparam['orderid'] = result['data']['oms_order_id']
                orderobject(orderparam)  # Call the callback function
                return result['data'], None
            else:
                return False, result.get('message', 'Order placement failed')

        except Exception as e:
            print(e)
            return False, str(e)

def modifyorder(self, parent_order_id=None, quantity=None,
                price=None, order_type=None, 
                trigger_price=None, validity=None, disclosed_quantity=None):
    try:
        url = f'https://developer.hdfcsky.com/oapi/v1/orders?api_key={self.api}'
        session = self.loginsession() 
        data = {}
        if parent_order_id is not None:
            data['oms_order_id'] = parent_order_id
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
     


    
 



class WebSocketConnect(HDFCSkyConnect):
    def __init__(self, api_key='', request_token=''):
        super().__init__(api_key)
        self.api_key = api_key
        self.request_token = request_token
        self.ws_url = f"ws://sky-ws.hdfcsky.com/wsapi/v1/session"
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
            if 'data' in data and 'type' in data:
                if data['type'] == 'quote': 
                    logging.info(f"Quate data: {data[data]}")
                elif data['type'] == 'ltp':
                    logging.info(f"LTP Data: {data['data']}")
                else:
                    logging.info(f"Received message with MsgCode {data['type']}: {data}")
            else:
                logging.info(f"Received message: {data}")
        except json.JSONDecodeError:
            logging.error("Failed to parse message as JSON")

    def on_open(self, ws):
        logging.info("Successfully connected to Stoxkart WebSocket")
        # Subscribe to tokens
        headers = self.loginsession()
        for token in self.tokens:
            subscribe_request = {
                "method": "subscribe",
                "instruments": [{"exchange": "NSE", "token": str(token)} for token in self.tokens],
                "types": ["quote", "ltp"]
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
        headers = self.loginsession()
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            header =headers,
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