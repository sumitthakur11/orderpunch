# import pyotp
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
import threading
from concurrent.futures import ThreadPoolExecutor
# from selenium import webdriver    
from random import randint
import pandas as pd 
# from logzero import logger
from Tradingbot import models as md

import datetime
import math
import pickle
import pytz
import webbrowser
logging.basicConfig(level=logging.DEBUG)
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

import io 
import os 
import zipfile
import gzip
from urllib.parse import urlparse, parse_qs
import upstox_client
# dir(upstox_client)

def searchscrip (name,exchange='NFO',instrument='',TOKEN=''):
        print(name,exchange,instrument)

        
        data = requests.get('https://assets.upstox.com/market-quote/instruments/exchange/complete.csv.gz')
        db= None    
       
        if data.status_code == 200:

            logpath= os.path.join(BASE_DIR,"extracted_files")
            logpath= os.path.normpath(logpath)
            
            with gzip.open(io.BytesIO(data.content),'rt') as zip_ref:
                    db = pd.read_csv(zip_ref,delimiter = ",",keep_default_na=False)
            print(db.head())
            print(db.columns)
            

        if exchange=='NFO':
            exchange= "NSE"
        elif exchange=='BFO':
            exchange= "BSE"




       
            


        if instrument=='EQ':
            instrument='EQUITY'
            exchange= exchange.upper()+'_EQ'
        if instrument in ['OPTIDX','OPTSTK','FUTSTK','FUTIDX']  :
            exchange= exchange.upper()+'_FO'
        # if name in ['NIFTY','FINNIFTY','BANNIFTY','MIDCAP','SENSEX']:
            
        #     exchange= exchange.upper()+'_INDEX'

        if TOKEN:
            print(TOKEN)
            print(type(TOKEN))

            db=db[db['tradingsymbol']==name]

            print(db['exchange_token'])
            db=db[db['exchange_token']==int(TOKEN)]
            print(db)
        
        if  name and instrument and exchange:
            db =db[db['exchange']==exchange]
            db =db[db['instrument_type']==instrument]
            db['name'] =db['name'].str.split().str[0]   

            db =db[db['name'].str.upper()==name]
        # else:
        #     db =db[db['exchange']==exchange]
        
       


        db=db.rename(columns={'tradingsymbol':'TradingSymbol','lot_size':'lotsize','exchange_token':'token','instrument_type':'instrument'})
        return db








class Upstoxapi(object) :
    #sheikhimran_rocky@yahoo.com
    def __init__(self, user,api_key =''):
        self.api= api_key 
        self.username=user
        # self.pwd = pwd
        self.orderid = None
        self.authToken= None
        self.refreshToken= None
        self.feedToken = None
        self.baseurl = 'https://api.upstox.com/'
        self.userid= user
        # self.token = token   #"46PG2HG3ST4NDTRD4FUUNVDC6Q"
        self.decimals = 10**6
        self.occurred= 0
        # self.getclient()
        # self.accesstoken ='eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIxNjMyMTAiLCJqdGkiOiI2N2E0YTJiNDZiNmQ0NDM4NGYzOTAxN2UiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaWF0IjoxNzM4ODQyODA0LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3NDEzODQ4MDB9.HvJG5sjpJauTxKf7CDNxjwF2EV3A40OOGXom_5AhI4M'
    def headersupdate(self,accesstoken):

        self.header= {"Authorization":"Bearer "+accesstoken,
                      "Accept":'application/json',
                    "Content-Type": "application/json"

                      }
        return self.header

    def sendrequest(self,method,endpoint,payload,head):
            
        if method=='GET':
            result= requests.get(self.baseurl+endpoint,params=payload,headers=head)
            print(result.url)
        
            return result

        if method== "POST":
            print(self.baseurl+endpoint)

            result= requests.post(self.baseurl+endpoint,data=payload,headers=head)
            print(result)   
            return result
        
        if method=='PUT':
            result= requests.put(self.baseurl+endpoint,data=payload,headers=head)

            return  result




    def gettoken(self,code,secret_key):
        url = "https://api.upstox.com/v2/login/authorization/token"

        Payload={}
        Payload['code']=code
        Payload['client_id']= self.api
        Payload['redirect_uri']= "https://tradeforsure.in/upstoxtoken"
        Payload['response_type']= "code"
        Payload['client_secret']=secret_key
        Payload['grant_type']='authorization_code'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=Payload)
        print(response.text)

        return response.json()

    def login(self):

        Payload= dict()
        Payload['client_id']= self.api
        redirect_uri= "https://tradeforsure.in/upstoxtoken"
        response_type= "code"
        header= {}
        print(Payload)
        payload = "?client_id={}&redirect_uri={}&response_type={}".format(self.api,redirect_uri,response_type)

        checktoken= md.Broker.objects.filter(user=1,accountnumber=self.username,brokername='UPSTOX').last()
        if not checktoken.AuthToken:
            url = self.baseurl+"v2/login/authorization/dialog"+payload
            checktoken.url= url
            checktoken.AuthToken= None
            checktoken.save()
            

            return True,None


    def getclient(self):
        
            checktoken= md.Broker.objects.filter(user=1,accountnumber=self.username,brokername='UPSTOX').last()
            token= checktoken.AuthToken
            breakcount = 300
            if token :
                access=self.gettoken(token,checktoken.secretkey)
                access_token = access["access_token"]
                checktoken.imei=access_token
                checktoken.valid=True
                checktoken.save()

    def authrisedlogin(self):
        checktoken= md.Broker.objects.filter(user=1,accountnumber=self.username,brokername='UPSTOX').last()

        url = 'https://api.upstox.com/v3/login/auth/token/request/678d46e1-91ac-4b8d-925d-89c8e3015c2b'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        data = {
            'client_secret': f'{checktoken.secretkey}'
        }

        response = requests.post(url, headers=headers, data=data)

        print(response.status_code)
        print(response.json())
        return  response.json()

class HTTP(Upstoxapi):
    def __init__(self,user,api_key =''):
        super().__init__(user,api_key)
        self.user=user


    
    def checkfunds (self):
        try:
            url = 'https://api.upstox.com/v2/user/get-funds-and-margin?segment=SEC'

            access_token= md.Broker.objects.filter(accountnumber=self.username,brokername='UPSTOX').last()
            headers= self.headersupdate(access_token.imei)
            print(headers)
            data = dict()

       
            ret= requests.get(url,headers=headers)
            if ret.status_code==200:
                cash =ret.json()
                print(cash)
                
                return cash['data']['equity']['available_margin'] ,None
            
            else: return None,ret.json()

        except Exception as e:
            print(e)
            return None,e


    def cancel_order(self, orderno):

        try:
            url = f'https://api-hft.upstox.com/v2/order/cancel?order_id={orderno}'
            access_token= md.Broker.objects.filter(accountnumber=self.username,brokername='UPSTOX').last()

            headers= self.headersupdate(access_token.imei)
            print(headers)

       
            ret= requests.get(url,headers=headers)
            if ret.status_code==200:
                cash =ret.json()
                print(cash)
                
                
                return cash['data'] ,None
            
          

        except Exception as e:
            print(e)
            return None,e

    def orderBook(self):

        try:
            url = "https://api.upstox.com/v2/order/retrieve-all"
            access_token= md.Broker.objects.filter(accountnumber=self.username,brokername='UPSTOX').last()

            headers= self.headersupdate(access_token.imei)
            print(headers)

       
            ret= requests.get(url,headers=headers)
            if ret.status_code==200:
                cash =ret.json()
                print(cash)
                
                
                return cash['data'] 
            
          

        except Exception as e:
            print(e)
            return None

    def getposition (self):
        try:
            url = "https://api.upstox.com/v2/portfolio/short-term-positions"

            access_token= md.Broker.objects.filter(accountnumber=self.username,brokername='UPSTOX').last()
            print(self.username)
            headers= self.headersupdate(access_token.imei)
            print(headers)
            data = dict()

            listfin=[]
            findata=dict()
            ret= requests.get(url,headers=headers)
            if ret.status_code==200:
                cash =ret.json()
                print(cash)
  
                for i in cash['data'] :

                    findata['exchange'] = i['exchange']
                    findata['tradingsymbol'] = i['trading_symbol']
                    findata['symboltoken'] = i['instrument_token']
                    findata['buyavgprice'] = i['buy_price']
                    findata['sellavgprice'] =  i['sell_price']
                    findata['netqty'] = i['quantity']
                    findata['unrealised'] = i['unrealised']
                    findata['realised'] = i['realised']
                    listfin.append(findata)
                    findata={}

                        
                
                return listfin,None
            else:
                return None ,ret.json()

        except Exception as e:
            print(e)
            return None,e

    def allholding (self):
        try:
            url = 'https://api.upstox.com/v2/portfolio/long-term-holdings'

            access_token= md.Broker.objects.filter(accountnumber=self.username,brokername='UPSTOX').last()
            print(self.username)
            headers= self.headersupdate(access_token.imei)
            print(headers)
            data = dict()

            listfin=[]
            findata=dict()
            ret= requests.get(url,headers=headers)
            if ret.status_code==200:
                cash =ret.json()
                print(cash)
  
                for i in cash['data'] :

                    findata['tradingsymbol'] = i['tradingsymbol']
                    findata['symboltoken'] = i['instrument_token']
                    findata['quantity'] = i['quantity']
                    findata['averageprice'] = i['average_price']
                    listfin.append(findata)
                    findata={}

                        
                
                return listfin,None
            else:
                return None ,ret.json()


          

        except Exception as e:
            print(e)
            return None,e



    
    def placeorder(self, orderparam,orderobject):

        try:
            url = "https://api-hft.upstox.com/v2/order/place"

            access_token= md.Broker.objects.filter(accountnumber=self.username,brokername='UPSTOX').last()
            print(orderparam)
            headers= self.headersupdate(access_token.imei)
            
            security_id=orderparam['symboltoken']
            exchange_segment=orderparam['exchange']
            transaction_type=orderparam['transactiontype']
            product_type=orderparam['product_type']
            quantity=int(orderparam['quantity'])
            order_type=orderparam['ordertype']
            price=float(orderparam['ltp'])
            disclosed_quantity=int(orderparam['discloseqty'])
            stoploss=0
            print(security_id)
            TOKENS = searchscrip(orderparam['tradingsymbol'],TOKEN=security_id)
            TOKENS= TOKENS['instrument_key'].iloc[-1]
            
            if product_type=='INTRADAY':
                product_type='I'

            if product_type=='DELIVERY':
                product_type='D'
            

            if product_type=='CARRYFORWARD':
                product_type='D'

            
            data = {
                    'quantity': quantity,
                    'product': 'D',
                    'validity': 'DAY',
                    'price': price,
                    'tag': 'string',
                    'instrument_token':TOKENS,
                    'order_type': order_type,
                    'transaction_type': transaction_type,
                    'disclosed_quantity': disclosed_quantity,
                    'trigger_price': 0,
                    'is_amo': False,
                }
       
            ret= requests.post(url,headers=headers,json=data)
            print(ret.json())
            if ret.status_code==200:

                ret=ret.json()
                if ret['status']=='success':
           
                    orderparam['orderid']=ret['data']['order_id']
                    orderparam['orderstatus']='OPEN'
                    orderparam['lotsize']=int(orderparam['lotsize']) 
                    orderobject(orderparam)
                
                
                    return orderparam ,None
                else:
                    return None ,ret.json()

            
          

        except Exception as e:
            print(e)
            return None,e


        
    
class WebSocketConnect(Upstoxapi):
    def __init__(self,user,api_key =''):
        super().__init__(user, api_key)

        


    def newevent(self):
        obj = md.watchlist.objects.filter(newevent=True,broker='UPSTOX').last()
        if obj:
            return obj,obj.newevent
        else:
            return obj, False

    def unsubscribetoken(self):
            try:

                obj = md.watchlist.objects.filter(subscribe=False,broker='UPSTOX')
                tokenlist=[]
                for  i in obj:
                    TOKENS = searchscrip(i.tradingsymbol,TOKEN=i.symboltoken)
                    TOKENS= TOKENS['instrument_key'].iloc[-1]
                    tokenlist.append(TOKENS)              
                return tokenlist
            except Exception as e :
                print(e)
    def subscribetoken(self):
          

            try:
                
                obj = md.watchlist.objects.filter(subscribe=True,broker='UPSTOX')
                tokenlist=[]
                for  i in obj:
                    TOKENS = searchscrip(i.tradingsymbol,TOKEN=i.symboltoken)
                    TOKENS= TOKENS['instrument_key'].iloc[-1]
                    i.orderpunchsymbol=TOKENS
                    i.save()

                    tokenlist.append(TOKENS)
                return tokenlist
            except Exception as e :
                print(e)

    def on_message(self,message):
        objnew,newevent= self.newevent()
        if newevent:
            tokelistunsb= self.unsubscribetoken()
            tokelistsubs= self.subscribetoken()
            if len(tokelistunsb)>0:
                    self.streamer.subscribe(tokelistsubs,"full")
                
            if len(tokelistsubs)>0:
                    self.streamer.unsubscribe(tokelistunsb)

            objnew.newevent= False
            objnew.save()
        data = message
        # print(data)
        if 'feeds' in data.keys():
            # print(data['feeds'].keys())
            symbol=data['feeds'].keys()
            symbol= list(symbol)
            for i in symbol:

                obj = md.watchlist.objects.filter(broker='UPSTOX',orderpunchsymbol=i).last()
                if obj:
                    if obj.orderpunchsymbol in data['feeds'].keys():
                        print( data['feeds'][obj.orderpunchsymbol]['fullFeed']['marketFF'].keys())
                        datasym= data['feeds'][obj.orderpunchsymbol]['fullFeed']['marketFF']['marketOHLC']['ohlc'][0]
                        obj.ltp= int(datasym['close'])
                        obj.volume= int(datasym['vol'])  if 'vol' in datasym.keys() else 0
                        obj.save()

        
                
        print(message)

    
    def start_thread(self):
        subscribetoken=self.subscribetoken()
        print(subscribetoken)
        access_token= md.Broker.objects.filter(accountnumber=self.username,brokername='UPSTOX').last()

        configuration = upstox_client.Configuration()
        configuration.access_token = access_token.imei
        
        self.streamer = upstox_client.MarketDataStreamerV3(upstox_client.ApiClient(configuration), subscribetoken, "full")

        self.streamer.on("message", self.on_message)

        self.streamer.connect()




      









# obj = HTTP(1)
# obj.getholdigs()
# searchscrip('NIFTY')

