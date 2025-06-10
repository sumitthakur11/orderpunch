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

from datetime import datetime, timedelta
# import ThreadPoolExecutor
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

import io








    

class kitesetup(object):
    def __init__(self, user,apikey='', secret=''):
    
        self.api= apikey
        self.secret=secret

       
        self.userid= user
      

 


    def login(self):
        self.kite = KiteConnect(api_key=self.api)

        self.url= self.kite.login_url()

        checktoken= md.Broker.objects.filter(user=1,accountnumber=self.userid,brokername='ZERODHA').last()
        checktoken.AuthToken= None
        checktoken.url= self.url
        checktoken.save()
        pasttime = time.time()
        while True:
                checktoken= md.Broker.objects.filter(user=1,accountnumber=self.userid,brokername='ZERODHA').last()

                if checktoken.AuthToken:


                    data = self.kite.generate_session(checktoken.AuthToken, api_secret=self.secret)
                    session=self.kite.set_access_token(data["access_token"])
                    print(data)
                    checktoken.imei= data["access_token"]
                    checktoken.valid=True
                    checktoken.save()
                    return data
                else:
                    current= time.time()
                    diff= current-pasttime
                    if int(diff)>=400:
                        return None

            
    def searchscrip (self,name,exchange='NFO',instrument=''):
        print(name,exchange,instrument)
        
        checktoken= md.Broker.objects.filter(user=1,brokername='ZERODHA').last()

        headers={

                "X-Kite-Version": "3" ,
                "Authorization": "token "+checktoken.apikey+":"+checktoken.imei,
               
            }
        
        data = requests.get('https://api.kite.trade/instruments',headers=headers)
        print(data)
        db= None
        csv_data = io.StringIO(data.text)
        db= pd.read_csv(csv_data,delimiter = ",",keep_default_na=False)
        print(db.head())
        print(db.columns)
        print(set(db['segment']))
      
       
            
        if instrument in ['FUTIDX',"FUTSTK"]:
            instrument='NFO-FUT'
        if instrument in ['OPTIDX',"OPTSTK"]:
            instrument='NFO-OPT'
        if instrument in ['EQ']:
            instrument=exchange
        if instrument in ['FUTIDX',"FUTSTK"] and exchange=='BFO':
            instrument='BFO-FUT'
        if instrument in ['OPTIDX',"OPTSTK"] and exchange=='BFO':
            instrument='BFO-OPT'



            


        if  name and instrument and exchange:
            db =db[db['exchange']==exchange]
            db =db[db['segment']==instrument]

            db =db[db['name'].str.upper()==name]
        else:
            db =db[db['exchange']==exchange]
        


        db=db.rename(columns={'tradingsymbol':'TradingSymbol','lot_size':'lotsize','exchange_token':'token','instrument_type':'instrument'})
        return db

    def loginsession(self):
            checktoken= md.Broker.objects.filter(user=1,accountnumber=self.userid,brokername='ZERODHA').last()
            print(self.api)
            headers={

                "X-Kite-Version": "3" ,
                "Authorization": "token "+self.api+":"+checktoken.imei,
               
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
    





    

    
    
 

class HTTP(kitesetup):
    
   
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

            url ='https://api.kite.trade/user/margins'
            session =self.loginsession()
            print(session)
            balance= requests.get(url,headers= session)
            balance= balance.json()
            print(balance)
            if balance['status']=='success' :
                return balance['data']['equity']['net'],None
            else:
                return None, balance

       
        except Exception as e :
            print(e)
            return e
    
    
    
    
    def cancel_order(self, orderid):
            url = f"https://api.kite.trade/orders/regular/{orderid}" 
            data = {}
    
            session =self.loginsession()
            print(session)
            balance= requests.delete(url,headers= session)
            balance= balance.json()
            if balance['status']=='success':
                return balance
            else: return balance


    
    
    def allholding(self):
        try:

            url ='https://api.kite.trade/portfolio/holdings'
            session =self.loginsession()
            print(session)
            balance= requests.get(url,headers= session)
            balance= balance.json()
            if balance['status']=='success':
                
                listfin = []
                finddata ={}
                for i in balance['data']:
                    finddata['tradingsymbol'] = i['tradingsymbol']
                    finddata['quantity'] = i['quantity']
                    finddata['averageprice'] = i['average_price']
                    finddata['ltp'] = i['last_price']
                    finddata['profitandloss']=i['pnl']
                    finddata['totalprofitandloss']=i.get('total_pl')
                    finddata['totalpnlpercentage']=i.get('pnl_percentage')
                    
                    listfin.append(finddata)
                    finddata={}
                return listfin,None
            else :
                return None, 'Not found'


        except Exception as e:
            print(e)
            return None,e

    def getposition(self):
        try:
            
            url ='https://api.kite.trade/portfolio/positions'
            listfin= []
            findata= {}          
            
            session =self.loginsession()

            balance = requests.get(url, headers=session)
            balance = balance.json()
            
            if balance['status'] == 'success':
                for i in balance['data']['net']:
                    findata['tradingsymbol'] = i['tradingsymbol']
                    findata['quantity'] = i['quantity']
                    findata['averageprice'] = i['average_price']
                    findata['ltp'] = i['last_price']
                    findata['profitandloss']=i['pnl']
                    findata['totalprofitandloss']==i.get('total_pl')
                    findata['totalpnlpercentage']=i.get('pnl_percentage')
                    listfin.append(findata)
                    findata={}
                
            
                return listfin ,None
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
            
            url ='https://api.kite.trade/orders'
            listfin= []
            findata= {}          
            
            session =self.loginsession()

            balance = requests.get(url, headers=session)
            balance = balance.json()
            
            if balance['status'] == 'success':
               
            
                return balance['data']
            else:
                return None


        except Exception as e:
            print(e)
            return None,e
    
    
    






    def placeorder(self,orderparam,orderobject):
        try:
            url = 'https://api.kite.trade/orders/regular'
            session =self.loginsession()
            print(orderparam)
            exchange = orderparam['exchange']
            tradingsymbol = orderparam['tradingsymbol']
            transaction_type = orderparam['transactiontype'] 
            quantity = orderparam['quantity']
            product = orderparam['product_type']
            order_type = orderparam['ordertype']
            validity = orderparam.get('validity', None)
            if product=='INTRADAY':
                product='MIS'
            if product=='DELIVERY':
                product='CNC'

            if product=='CARRYFORWARD':
                product='NRML '


            data = {
            'exchange': exchange,
            'tradingsymbol': tradingsymbol,
            'transaction_type': transaction_type,
            'quantity': str(quantity),  
            'product': product,
            'order_type': order_type,
            'price':orderparam['ltp'],
            'validity': validity,
        }
            
            response = requests.post(url, headers=session, data=data)
            result = response.json()
            print(result)
            if result['status'] == 'success':
                orderparam['orderid'] = result['data']['order_id']  # Corrected from 'id'
                
                orderobject(orderparam)  # Call the callback function
                return result['data'], None
            else:
                return False, result.get('message', 'Order placement failed')

        except Exception as e:
            print(e)
            return False, str(e)

    def modifyorder(self,orderparam,orderobject):
        try:
            

            variety=  'regular'
            
            order_id=orderobject.orderid
            parent_order_id=None
            quantity=orderparam['quantity']
            price=orderparam['ltp']
            order_type=orderparam['ordertype']
            trigger_price=None
            validity='DAY'
            disclosed_quantity=orderparam['discloseqty']


            url = f'https://api.kite.trade/orders/regular/{order_id}'
            session = self.loginsession() 
            data = {}
            
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
            print(result)

            if result['status'] == 'success':
                return result['data'], None
            else:
                return False, result.get('message', 'Order modification failed')

        except Exception as e:
            print(e)
            return False, str(e)
     
     


    
 


class WebSocketConnect(kitesetup):
    def __init__(self,key='', secret=''):
     

        super().__init__(key)
        self.key = key
        self.token= "147pR9GqlNrh6nRa3QVE7PwlqV97f3o7"
        kws = KiteTicker(key, self.token)

        # RELIANCE BSE
        


        # Callback for tick reception.
        def on_ticks(ws, ticks):
            if len(ticks) > 0:
                
                # Ltp(ticks)
                print(ticks)
                logging.info("Current mode: {}".format(ticks[0]["mode"]))


        # Callback for successful connection.
        def on_connect(ws, response):
            logging.info("Successfully connected. Response: {}".format(response))
            ws.subscribe(tokens)
            ws.set_mode(ws.MODE_FULL, tokens)
            logging.info("Subscribe to tokens in Full mode: {}".format(tokens))


        # Callback when current connection is closed.
        def on_close(ws, code, reason):
            logging.info("Connection closed: {code} - {reason}".format(code=code, reason=reason))
        
        


        # Callback when connection closed with error.
        def on_error(ws, code, reason):
            logging.info("Connection error: {code} - {reason}".format(code=code, reason=reason))


        # Callback when reconnect is on progress
        def on_reconnect(ws, attempts_count):
            logging.info("Reconnecting: {}".format(attempts_count))


        # Callback when all reconnect failed (exhausted max retries)
        def on_noreconnect(ws):
            logging.info("Reconnect failed.")


        # Assign the callbacks.
        kws.on_ticks = on_ticks
        kws.on_close = on_close
        kws.on_error = on_error
        kws.on_connect = on_connect
        kws.on_reconnect = on_reconnect
        kws.on_noreconnect = on_noreconnect

        # Infinite loop on the main thread.
        # You have to use the pre-defined callbacks to manage subscriptions.
        kws.connect(threaded=True)

        # Block main thread
        logging.info("This is main thread. Will change webosocket mode every 5 seconds.")

        count = 0
        while True:
            count += 1
            if count % 2 == 0:
                if kws.is_connected():
                    logging.info("### Set mode to LTP for all tokens")
                    kws.set_mode(kws.MODE_LTP, tokens)
            else:
                if kws.is_connected():
                    logging.info("### Set mode to quote for all tokens")
                    kws.set_mode(kws.MODE_QUOTE, tokens)

            time.sleep(5)
