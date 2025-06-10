
from Tradingbot import env
from .SmartApi import smartConnect
from .SmartApi import smartWebSocketV2
import pyotp
import asyncio
import base64
import hashlib
import hmac
import json
import logging
from random import random
import time
import uuid
import requests
import threading
import pandas as pd 
import datetime
import math
import pytz
import os 
import pathlib 
from stat import *
from Tradingbot import models as md
import pathlib
from alice_blue import *
import uuid
import io
path = pathlib.Path(__file__).resolve().parent.parent.parent
logpath= os.path.join(path,'Botlogs/Angelbroker.logs')
logpath= os.path.normpath(logpath)



print(logpath,'logpath')
logger=env.setup_logger(logpath)

logger1path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpath1= os.path.normpath(logger1path)
logpath1=env.setup_logger(logpath1)


savepath= os.path.join(path,"angel.json")
savepath= os.path.normpath(savepath)
submitdata=[]
tokenltp=0
filtered_data = []


def searchscrip (name,exchange='NFO',instrument=''):
        print(name,exchange,instrument)

        if exchange == 'NFO':
            data = requests.get('https://v2api.aliceblueonline.com/restpy/static/contract_master/NFO.csv')
        elif exchange =='BFO':
            data = requests.get('https://v2api.aliceblueonline.com/restpy/static/contract_master/BFO.csv')
        elif exchange =='NSE':
            data = requests.get('https://v2api.aliceblueonline.com/restpy/static/contract_master/NSE.csv')
        elif exchange =='BSE':
            data = requests.get('https://v2api.aliceblueonline.com/restpy/static/contract_master/BSE.csv')

        db= None
        csv_data = io.StringIO(data.text)
        db= pd.read_csv(csv_data,delimiter = ",",keep_default_na=False)
        print(db.head())
        print(db.columns)
    
       
        db=db.rename(columns={'Trading Symbol':'TradingSymbol','Lot Size':'lotsize','Token':'token','Exch':'exchange','Instrument Type':'instrument'})
       
        if instrument=='EQ':
            instrument=0
          




        if  name and instrument and exchange:

            db =db[db['exchange']==exchange]
          

            db =db[db['instrument']==instrument]
            db =db[db['Symbol']==name]



        else:
            db =db[db['exchange']==exchange]
        


    
        return db


class Aliceapi(object) :
    
    def __init__(self, username = '',pwd = '',api_key ='',secret='',token=""):
       

        
        self.api= api_key
        self.username=username
        self.pwd = str(pwd)
        self.token =token  
        self.secret =secret  
        print(username,pwd,api_key,secret,token)
        self.orderid = None
        self.authToken= None
        self.refreshToken= None
        self.feedToken = None
        self.decimals = 10**6
        # self.secret
        self.baseurl="https://ant.aliceblueonline.com/rest/AliceBlueAPIService/api"

        
    def login(self):

        Payload= dict()
        Payload['client_id']= self.api
        response_type= "code"
        headers = {
                'Content-Type': 'application/json'
                                }        
        print(Payload)

        Payload['userId'] =self.username

        checktoken= md.Broker.objects.filter(user=1,accountnumber=self.username,brokername='ALICEBLUE').last()
        url = self.baseurl+"/customer/getAPIEncpkey"
        res= requests.post(url,headers=headers,json=Payload)
        print(res.text)
        response = res.json()
        checktoken.AuthToken= response['encKey']
        checktoken.save()
        time.sleep(2)
        self.login2()
        return True,None


    def login2(self):
        checktoken= md.Broker.objects.filter(user=1,accountnumber=self.username,brokername='ALICEBLUE').last()

        Payload= dict()
        Payload['client_id']= self.username
        response_type= "code"
        headers = {
                'Content-Type': 'application/json'
                                }        
        print(Payload)
        Payload['userId'] =self.username
        data = self.username + self.api + checktoken.AuthToken
        print(self.username,self.api,checktoken.AuthToken)
        hashed_data = hashlib.sha256(data.encode()).hexdigest()
        Payload['userData']= hashed_data

        checktoken= md.Broker.objects.filter(user=1,accountnumber=self.username,brokername='ALICEBLUE').last()
        url = self.baseurl+"/customer/getUserSID"
        res= requests.post(url,headers=headers,json=Payload)
        if res.status_code==200:
            response = res.json()
            print(response)
            if response['stat']=='Ok':
                checktoken.imei= response['sessionID']
                checktoken.valid= True
                checktoken.save()
                return True
            else:
                return False
        else:
            return None
    
        
    def login1(self):
        try:

            res= None
            try:
                pass
                totp = pyotp.TOTP(self.token).now()

            except Exception as e:
                logger.error(f"Invalid Token: The provided token is not valid or {e}") 
                raise e

            data = AliceBlue.login_and_get_sessionID(   username    = self.username, 
                                                    password    = self.pwd, 
                                                    twoFA       = totp,
                                                    app_id      = self.api,
                                                    api_secret  = self.secret)
            
            print(data)

            if not data['status']:
                logger.error(data)
                logpath1.error(data)

            else:
               
                filepath= os.path.join(path,f'Angellogin/{self.username}.json')
                filepath= os.path.normpath(filepath)
                tokendict= dict()
                tokendict['Authtoken']= data
                print(filepath)
                
                out=open(filepath, 'w')
                json.dump(tokendict,out,indent=6)
                logpath1.info('Alice Login successful')
                # out.close()
                return True , None
        except Exception as e :
            logpath1.error(e)
            return False,e
    def loginsession(self):
            checktoken = md.Broker.objects.filter(user=1, accountnumber=self.username, brokername='ALICEBLUE').last()
            headers = {
                'Authorization': f'Bearer {self.username} {checktoken.imei}'
                }
            
          

            return headers
  
    
    

class HTTP(Aliceapi):

    

  
    
    


    def checkfunds(self):
        try :
            headers= self.loginsession()
            url = self.baseurl+"/limits/getRmsLimits"
            payload = ""
               
            response = requests.request("GET", url, headers=headers, json=payload)
            if response.status_code==200:
                print(response.json())
                response= response.json()
                if response:
                    return response[0]['cashmarginavailable'],None
                else:
                    return None, response
        
        except Exception as e:
            return None, e


  

        
        

    
  
                
   

    def getposition(self):
        try :
            headers= self.loginsession()
            url = self.baseurl+"/positionAndHoldings/positionBook"
            payload = {
                         "ret":"DAY"

            }
               
            response = requests.request("POST", url, headers=headers, json=payload)
            if response.status_code==200:
                print(response.json())
                balance= response.json()
                if balance:
                    listfin = []
                    finddata ={}
                    for i in balance:
                        findata['exchange'] = i['Exchange']
                        findata['tradingsymbol'] = i['Tsym']
                        findata['buyavgprice'] = i['Buyavgprc']
                        findata['sellavgprice'] = i['Sellavgprc']
                        findata['netqty'] = i['Netqty']
                        findata['ltp'] = i['LTP']
                        findata['realised']=i['realisedprofitloss']
                        findata['unrealised']=i['unrealisedprofitloss']
                        listfin.append(findata)
                        findata={}
                    return listfin,None
                else:
                    return None, balance
            else:
                    return None, response.text
        
        
        except Exception as e:
            return None, e

    
    def allholding(self):
        try :
            headers= self.loginsession()
            url = self.baseurl+"/positionAndHoldings/holdings"
            payload = ""
               
            response = requests.request("GET", url, headers=headers, json=payload)
            if response.status_code==200:
                balance= response.json()
                print(balance)
                if balance['stat']=='Ok':
                    listfin = []
                    finddata ={}
                    for i in balance['HoldingVal']:
                        finddata['tradingsymbol'] = i['Bsetsym'] if i['Bsetsym'] else i['Nsetsym']
                        finddata['quantity'] = i['Holdqty']
                        finddata['averageprice'] = i['Price']
                        finddata['ltp'] = i['Ltp']
                        
                        listfin.append(finddata)
                        finddata={}
                    return listfin,None
                else:
                    return None, balance
            else:
                    return None, response.text
        
        
        except Exception as e:
            return None, e









    def cancel_order(self, orderid):
        try :
            orderob= md.orderobject.objects.filter(orderid=orderid)
            headers= self.loginsession()
            url = self.baseurl+"/placeOrder/cancelOrder"
            payload = {

                "exch": orderob.exchange,
                "nestOrderNumber": orderid,
                "trading_symbol": orderob.tradingsymbol,
                "deviceNumber": uuid.uuid4()
            }
               
            
            response = requests.request("GET", url, headers=headers, json=payload)
            if response.status_code==200:
                balance= response.json()
                
                return balance,None
               
            else:
                    return None, response.text

        except Exception as e:
            return None, e
        
    
    

 
  
    
    
    def placeorder(self, orderparam,orderobject):
        try:

            
            print(orderparam)
            quantity=orderparam['quantity']

            orderid= None
            orderupdate= orderobject
          
            headers= self.loginsession()

            ttype=orderparam['transactiontype']
            instrument = orderparam['tradingsymbol']
            quantity =  int(quantity)
            order_type = orderparam['ordertype']
            product = orderparam['product_type'] 
            price = float(orderparam['ltp'])

            if product=='INTRADAY':
                product= 'MIS'
            if product=='DELIVERY':
                product='CNC'

            if product=='CARRYFORWARD':
                product='NRML'

            if order_type=='LIMIT':
                order_type='L'
            if order_type=='MARKET':
                order_type='MKT'


            url = self.baseurl+"/placeOrder/executePlaceOrder"
            payload= [{
                "complexty": "regular",
                "discqty": int(orderparam['discloseqty']),
                "exch": orderparam['exchange'],
                "pCode": product,
                "prctyp": order_type,
                "price": float(price),
                "qty": quantity,
                "ret": "DAY",
                "symbol_id": orderparam['symboltoken'],
                "trading_symbol": instrument,
                "transtype": ttype,
                "trigPrice": float(price)+1,
                "orderTag": str(time.time()*1000),
                "deviceNumber": str(uuid.uuid4())
            }   ]

            print(payload)
            response = requests.request("POST", url, headers=headers, json=payload)

            if response.status_code==200:
                response= response.json()
                print(response,'text')

                if response[0]['stat']:
                    
                   
                    
                    orderparam['orderid']=response[0]['NOrdNo']
                    orderparam['user']=1
                    orderparam['broker']='ALICEBLUE'
                    orderobject(orderparam)
                    logpath1.info(f'Broker Angel order palced,orderid:{orderparam['orderid']}')
            


            return   response
        except Exception as e:
            logger.error(e,exc_info=True)
            logpath1.error(e)
            orderobject(orderparam)


    
    
    
    
    def orderBook(self):

        try :
            headers= self.loginsession()
            url = self.baseurl+"/placeOrder/fetchOrderBook"
            payload = {

              
            }
               
            
            response = requests.request("GET", url, headers=headers, json=payload)
            if response.status_code==200:
                balance= response.json()
                
                return balance
               
            else:
                    return None
        except Exception as e:
            return None, e

        
    def modifyorder(self,data,orderobject):
        try:
            orderiddta= self.alice.modify_order( order_id = orderobject.orderid, 
                            transaction_type = TransactionType.Buy, 
                            instrument = orderobject.tradingsymbol, 
                            quantity = str(data['quantity']), 
                            order_type = data['ordertype'],
                            product_type = data['product_type'], 
                            price = data['ltp'])
            if orderiddta['data']:
                orderobject.quantity= data['quantity']
                orderobject.ordertype= data['ordertype']
                orderobject.product_type= data['product_type']
                orderobject.avg_price= data['ltp']
                orderobject.transactiontype= data['transactiontype']
                orderobject.discloseqty= data['discloseqty']
                orderobj.orderid=orderiddta['orderid']
                orderobject.save()
                return orderiddta['data'], None
        except Exception as e:
            return None,e





class WebSocketConnect(Aliceapi):
    def __init__(self, username = '',pwd = '',api_key ='',secret='',token=""):
        super().__init__(username ,pwd,api_key,secret,token)
    
     

    def newevent(self):
        obj = md.watchlist.objects.filter(newevent=True,broker='ALICEBLUE').last()
        if obj:
            return obj,obj.newevent
        else:
            return obj, False

    def unsubscribetoken(self):
            try:

                obj = md.watchlist.objects.filter(subscribe=False,broker='ALICEBLUE')
                tokenlist=[]
                for  i in obj:
                  
                    
                    instruments_list =i.tradingsymbol
                    tokenlist.append(instruments_list)              
                return tokenlist
            except Exception as e :
                print(e)

    
    def subscribetoken(self):
          

            try:
                
                obj = md.watchlist.objects.filter(subscribe=True,broker='ALICEBLUE')
                tokenlist=[]
                for  i in obj:
                    instruments_list =i.tradingsymbol
                   
                    tokenlist.append(instruments_list)
                return tokenlist
            except Exception as e :
                print(e)

   
    def event_handler_quote_update(self,message):
            print(f"quote update {message}")

          
            
        

        
    def start_thread(self):
        

        # token = self.get_angel_client()
        authToken= token['Authtoken']
        alice = AliceBlue(self.username,access_token=authToken)

        
       

        alice.start_websocket(subscribe_callback=self.event_handler_quote_update)
        token_list=self.subscribetoken()
        
        alice.subscribe(token_list, LiveFeedType.TICK_DATA)

        while True:
            objnew,newevent= self.newevent()
            if newevent:
                    tokelistunsb= self.unsubscribetoken()
                    tokelistsubs= self.subscribetoken()
                    if len(tokelistunsb)>0:
                            alice.unsubscribe(token_list, LiveFeedType.TICK_DATA)
                    if len(tokelistsubs)>0:
                            alice.subscribe(token_list, LiveFeedType.TICK_DATA)
                    objnew.newevent= False
                    objnew.save()



        


