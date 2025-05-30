
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
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws

import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from asgiref.sync import sync_to_async

path = pathlib.Path(__file__).resolve().parent.parent.parent
# import ThreadPoolExecutor
log = logging.getLogger(__name__)


logging.basicConfig(level=logging.DEBUG)


#   


logger2path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpathfron1= os.path.normpath(logger2path)
logpathfron=env.setup_logger(logpathfron1)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def searchscrip (name,exchange='NFO',instrument=''):
        print(name,exchange,instrument)

        if exchange == 'NFO':
            data = requests.get('https://public.fyers.in/sym_details/NSE_FO.csv')
        elif exchange =='BFO':
            data = requests.get('https://public.fyers.in/sym_details/BSE_FO.csv')
        elif exchange =='NSE':
            data = requests.get('https://public.fyers.in/sym_details/NSE_CM.csv')
        elif exchange =='BSE':
            data = requests.get('https://public.fyers.in/sym_details/BSE_CM.csv')

        db= None
        columns=['Fytoken','Symbol','Instrument','lotsize','Ticksize','ISIN','TradingSession', 'Lastupdatedate','Expirydate',
        'TradingSymbol','exchange','Segment','token','name','Underlyingtoken',
        'Strikeprice','Optiontype','UnderlyingFyToken','Reservedcolumnstr','Reservedcolumnint','Reservedcolumnfloat']
        csv_data = io.StringIO(data.text)
        db= pd.read_csv(csv_data,delimiter = ",",keep_default_na=False,names=columns)
        print(db.columns)
        print(db.head())

        

        # OPTSTK=15
        #0 EQ
        # 11	FUTIDX
        # 12	FUTIVX
        # 13	FUTSTK
        # 14	OPTIDX
        # 15	OPTSTK


        if exchange=='NFO':
            exchange= "NSE"
        elif exchange=='BFO':
            exchange= "BSE"

        db['Instrument']= db['Instrument'].astype('string')
        db['exchange']= db['exchange'].astype('string')

        db.loc[db["Instrument"] == '11', "Instrument"] = "FUTIDX"
        db.loc[db["Instrument"] == '12', "Instrument"] = "FUTIVX"
        db.loc[db["Instrument"] == "13", "Instrument"] = "FUTSTK"
        db.loc[db["Instrument"] == "14", "Instrument"] = "OPTIDX"
        db.loc[db["Instrument"] == "15", "Instrument"] = "OPTSTK"
        db.loc[db["Instrument"] == "0", "Instrument"] = "EQ"
        db.loc[db["exchange"] == "10", "exchange"] = "NSE"
        db.loc[db["exchange"] == "12", "exchange"] = "BSE"




        print(db['Instrument'])
        
        
        if  name and instrument and exchange:
            db =db[db['exchange']==exchange]
            print(db)
            db =db[db['Instrument']==instrument]
            db =db[db['name']==name]
        else:
            db =db[db['exchange']==exchange]
        


        db=db.rename(columns={'scripname':'TradingSymbol','marketlot':'lotsize','scripcode':'token','Exchange':'exchange','Exchange Instrument type':'instrument'})
        return db


savepath= os.path.join(BASE_DIR,"fyers.json")
savepath= os.path.normpath(savepath)
submitdata=[]
tokenltp=0
class Ltp:
    def __init__(self,data) :
        
        try:
            global findata
            global tokenltp
            findata= dict()

            if data['t']=='tk' and data['tk']!=tokenltp:    
                print('check acknowl',data)

                findata['LTP'] =data['lp']
                findata['exchange']= data['e']
                findata['broker']='FYERS'
                findata['token']= data['tk']
                findata['Tradingsymbol']= data['ts']
                findata['Lotsize']= data['ls']
                findata['volume']= data['v'] if 'v' in data.keys() else 0
                tokenltp= data['tk']

                submitdata.append(findata)
                print(submitdata)
                file= open(savepath,'w')
                datasub = json.dump(submitdata,file)
                file.close()
            


            if data['t']=='tf':

                if 'lp' in  data.keys():
                    with open(savepath,'r+') as incomingfile:
                        data1 = json.load(incomingfile)
                        print(data1,'incomingfile')
                        incomingfile.seek(0)
                        for i in range(len(data1)):
                            if data['tk']==data1[i]['token']:
                                data1[i]['LTP'] =data['lp']
                                data1[i]['exchange']= data['e']
                                data1[i]['broker']='FYERS'
                                data1[i]['token']= data['tk']
                                data1[i]['volume']= data['v'] if 'v' in data.keys() else 0
                        datasub = json.dump(data1,incomingfile, indent=4)
                        incomingfile.truncate()
                        incomingfile.close()
                        
                
        
            
        except KeyError as e :
            print(e)
            pass














    
class fyerssetup(object):
    def __init__(self,client_id ,secret_key , token=''):

      self.client_id=client_id
      self.fyers,self.accesstoken= self.gettoken()
      self.secret_key=secret_key
      self.token= token
        
    def gettoken(self):
        try:
            checktoken= md.Broker.objects.filter(user=1,accountnumber=self.client_id,brokername='FYERS').last()
            logg= os.path.join(path,'Botlogs')
            logg= os.path.normpath(logg)

            fyers = fyersModel.FyersModel(token=checktoken.imei,is_async=False,client_id=self.client_id,log_path=logg)

            return fyers,checktoken.imei
        except Exception as e:
            logpathfron.error('Try Login Again')
            print(e)
            return False,None
        # api = FYERSApiPy()


                       

    
    def login(self):
            try:
                checktoken= md.Broker.objects.filter(user=1,accountnumber=self.client_id,brokername='FYERS').last()
                checktoken.AuthToken= None
                checktoken.save()
                while True:

                
                    response_type='code'
                    grant_type='authorization_code'
                    state = "sample"                                   ##  The state field here acts as a session manager. you will be sent with the state field after successfull generation of auth_code 

                    appSession = fyersModel.SessionModel(client_id = self.client_id, redirect_uri = 'https://tradeforsure.in/fyerstoken/',response_type=response_type,state=state,secret_key=self.secret_key,grant_type=grant_type)


                    
                    generateTokenUrl = appSession.generate_authcode()

                    print(generateTokenUrl)
                   
                    checktoken= md.Broker.objects.filter(user=1,accountnumber=self.client_id,brokername='FYERS').last()
                    token= checktoken.AuthToken
                    checktoken.url= generateTokenUrl
                    checktoken.save()
                    time.sleep(2)
                    breakcount = 300
                    if token :
                        appSession.set_token(token)
                        response = appSession.generate_token()
                        access_token = response["access_token"]
                        checktoken.imei=access_token
                        checktoken.valid=True

                        checktoken.save()
                        return True,None


                        



            except Exception as e:
                    logpathfron.error(e)
                    checktoken.valid=False
                    checktoken.save()
                    return False,e

    def logout(self):
        tokenkey=self.gettoken()
        param= dict()
        param['uid']= tokenkey['uid']
        param['actid']=tokenkey['actid']
        param= json.dumps(param)
        data = "jData="+param+"&jKey="+tokenkey['Token']
        ret= requests.post(self.baseurl+"Logout",data=data)




  
            

    


    

    
    
    
    
    
    
    
    
    
    
    

    
class HTTP(fyerssetup):
   
    
    def cancel_order(self, exchange,orderno):
        data = {"id":orderno}



            

        data = self.fyers.cancel_order(data)
        return data
    
    
    def modifyorder(self,data,orderobject):
        try:
            data =  {
          "id":orderobject.orderid, 
          "type":1, 
          "limitPrice":data['ltp'],
          "qty":data['quantity']
      }
            data = self.fyers.modify_order(quantity =data['quantity'],segment =segment ,groww_order_id =orderobject.orderid, price=data['ltp'],trigger_price=data['ltp'],order_type=data['ordertype'])
        
            if data['groww_order_id']:
                orderobject.orderid=data['groww_order_id']
                

                return data,None
            else:
                return False,data
        except Exception as e:
            return False,e


   
    
  
    
    def placeorder(self,orderparam,orderobject):
        try:
           
          
            if orderparam['transactiontype']=='BUY':
                ttp= 1
            else:
                ttp =-1

            if orderparam['ordertype']=='LIMIT':
                ORDTYPE=1

            if orderparam['ordertype']=='MARKET':
                ORDTYPE=2

            if orderparam['product_type']=='INTRADAY' :
                PRDTYPE='INTRADAY'
            
            if orderparam['product_type']=='CARRYFORWARD' :
                PRDTYPE='MARGIN'

            if orderparam['product_type']=='DELIVERY' :
                PRDTYPE='CNC'
            
            if orderparam['exchange']=='NSE':
                exchange= 10
            if orderparam['exchange']=='NFO':
                exchange= 10
            elif orderparam['exchange']=='BSE':
                exchange= 12
            elif orderparam['exchange']=='BFO':
                exchange= 12


            
            

            data ={"symbol":orderparam['tradingsymbol'],
            "qty":orderparam['quantity'], 
            "validity":'DAY',
            "productType":PRDTYPE,
            "type":ORDTYPE,
            "side":ttp,
            "limitPrice":float(orderparam['ltp']),               # Optional: Price of the stock (for Limit orders)
            # trigger_price=orderparam['ltp'],
            "disclosedQty": orderparam['discloseqty'],
            "offlineOrder":False,
            "stopLoss":0,
            "takeProfit":0
            }
                # Optional: Trigger price (if applicable)
            print(data)

                
            
            
            orderiddta = self.fyers.place_order(data)
            print(orderiddta,'orderiddta')
                                               
                                     

            if orderiddta['s']=='ok':
             
                orderparam['orderid']=orderiddta['id']
                orderparam['orderstatus']=orderiddta['OPEN']

                orderobject(orderparam)
          
                logpathfron.info(f'Broker FYERS order placed, orderid :{orderiddta['id']}')

                return orderiddta,None
                
            else:
                orderparam['orderid']=orderiddta['id']
                orderparam['orderstatus']='REJECTED'

                orderobject(orderparam)

                logpathfron.info(f'Broker FYERS order placed, orderid :{orderiddta}')

                return False,orderiddta
        except Exception as e:
            logpathfron.error(e)
            return False,e


           



      

  
    
    
    def orderbook(self):
        """
        Info :Get order status
        """
        data= self.fyers.orderbook()
        data=data['order_list']
        return data
   



    def getposition (self):
        try:
  
        
            ret= self.fyers.positions()
            findata= dict()
            listfin=[]
            print(ret)
            position=ret['netPositions']
            if ret['netPositions']:
                for i in position:
                            
                        findata['tradingsymbol'] = i['symbol']
                        findata['buyavgprice'] = i['buyAvg']
                        findata['sellavgprice'] = i['sellAvg']
                        findata['netqty'] = i['netQty']
                        findata['producttype'] = i['productType']

                        findata['ltp'] = i['ltp']
                        findata['ltp'] = i['ltp']

                        # findata['lotsize'] = i['ls']
                        findata['unrealised'] = i['overall']['pl_unrealized']
                        findata['realised'] = i['overall']['pl_realized']
                        listfin.append(findata)
                        findata={}

                
                return listfin ,None
            else:
                    return None,'Not found'


        except Exception as e:
            print(e)
            return None,e

      
    def allholding (self):
        try:
            
            ret= self.fyers.holdings()
      
            print(ret)
            findata= dict()
            finaldata=dict()
            listfin=[]
            if ret['holdings']:
         
              
                for i in ret['holdings']:
                        print(i)
                            
                    
                        findata['tradingsymbol'] = i['symbol']
                        findata['quantity'] = i['quantity']
                        findata['averageprice'] = i['costPrice']
                        findata['ltp'] = i['ltp']
                        findata['profitandloss']=i['pl']
                        findata['totalprofitandloss']=ret['overall']['total_pl']
                        findata['totalpnlpercentage']=ret['overall']['pnl_perc']
                        listfin.append(findata)
                        findata={}
                print(listfin,'checklist')
                return listfin ,None
            else:
                    return None,'Not found'


        except Exception as e:
            print(e)
            return None,e



    def checkfunds (self):
        try:
            cash = self.fyers.funds()
            return cash['fund_limit'],None
            
          

        except Exception as e:
            print(e)
            return None,e


    

class WebSocketConnect(fyerssetup):
    def __init__(self,client_id ,secret_key , token=''):
        super().__init__(client_id ,secret_key , token)





    def onmessage(self,message):
        """
        Callback function to handle incoming messages from the FyersDataSocket WebSocket.

        Parameters:
            message (dict): The received message from the WebSocket.

        """
        data = message
        if 'symbol' in data.keys():
            obj = md.watchlist.objects.filter(broker='FYERS',tradingsymbol=data['symbol']).last()
            obj.ltp= int(data['ltp'])
            obj.volume= data['vol_traded_today']  if 'vol_traded_today' in data.keys() else 0
            obj.save()

        print("Response:", message)

        objnew,newevent= self.newevent()
        if newevent:
            tokelistunsb= self.unsubscribetoken()
            tokelistsubs= self.subscribetoken()
            if len(tokelistunsb)>0:
                self.websocketfy.unsubscribe(symbols=tokelistunsb, data_type="SymbolUpdate")

            if len(tokelistsubs)>0:
                self.websocketfy.subscribe(symbols=tokelistsubs, data_type="SymbolUpdate")
            objnew.newevent= False
            objnew.save()


    def onerror(self,message):
        """
        Callback function to handle WebSocket errors.

        Parameters:
            message (dict): The error message received from the WebSocket.


        """
        print("Error:", message)


    def onclose(self,message):
        """
        Callback function to handle WebSocket connection close events.
        """
        print("Connection closed:", message)
    def _handle_onopen_async(self):
        try:
            symbols =self.subscribetoken()
            unsymbol = self.unsubscribetoken()

            self.websocketfy.subscribe(symbols=symbols, data_type="SymbolUpdate")
            self.websocketfy.unsubscribe(symbols=unsymbol, data_type="SymbolUpdate")
            self.websocketfy.keep_running()

        except Exception as e:
            self.onerror(e)

    def onopen(self):
        """
        Callback function to subscribe to data type and symbols upon WebSocket connection.

        """
        # self.websocketfy.subscribe(symbols=["NSE:SBIN25MAYFUT"]	, data_type="SymbolUpdate")
        self._handle_onopen_async()

        # asyncio.create_task(self._handle_onopen_async())




    def newevent(self):
        obj = md.watchlist.objects.filter(newevent=True,broker='FYERS').last()
        if obj:
            return obj,obj.newevent
        else:
            return obj, False
    
    def unsubscribetoken(self):
            try:

                obj = md.watchlist.objects.filter(subscribe=False,broker='FYERS')
                tokenlist=[]
                for  i in obj:
                  
                    
                    instruments_list =i.tradingsymbol
                    tokenlist.append(instruments_list)              
                return tokenlist
            except Exception as e :
                print(e)

    
    def subscribetoken(self):
          

            try:
                
                obj = md.watchlist.objects.filter(subscribe=True,broker='FYERS')
                tokenlist=[]
                for  i in obj:
                    instruments_list =i.tradingsymbol
                   
                    tokenlist.append(instruments_list)
                return tokenlist
            except Exception as e :
                print(e)


    
    def start_thread(self):
        self.websocketfy = data_ws.FyersDataSocket(
                        access_token=self.token,       # Access token in the format "appid:accesstoken"
                        log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
                        litemode=False,                  # Lite mode disabled. Set to True if you want a lite response.
                        write_to_file=False,              # Save response in a log file instead of printing it.
                        reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
                        on_connect=self.onopen,               # Callback function to subscribe to data upon connection.
                        on_close=self.onclose,                # Callback function to handle WebSocket connection close events.
                        on_error=self.onerror,                # Callback function to handle WebSocket errors.
                        on_message=self.onmessage             # Callback function to handle incoming messages from the WebSocket.
                    )
      

        self.websocketfy.connect()
        # while True:
        #     pass

        

      












 