
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
from growwapi import GrowwAPI,GrowwFeed


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

        
        data = requests.get('https://growwapi-assets.groww.in/instruments/instrument.csv')
        print(data)
        db= None
        csv_data = io.StringIO(data.text)
        db= pd.read_csv(csv_data,delimiter = ",",keep_default_na=False)
        print(db.head())
        print(db.columns)
        if exchange=='NFO':
            exchange= "NSE"
        elif exchange=='BFO':
            exchange= "BSE"

        
        if instrument=='FUTSTK' or instrument=='FUTIDX' :
            db =db[db['segment']=='FNO']
            db =db[db['instrument_type']=='FUT']


        
        
        if instrument=='OPTSTK' or instrument=='OPTIDX'  :
            db =db[db['segment']=='FNO']

            db =db[db['instrument_type'].isin(['CE', 'PE']) ]

            


        # if instrument=='EQ':
        #     instrument=''
        if  name and instrument and exchange:
            db =db[db['exchange']==exchange]
            # db =db[db['instrument_type']==instrument]
            db =db[db['underlying_symbol']==name]
        else:
            db =db[db['exchange']==exchange]
        


        db=db.rename(columns={'trading_symbol':'TradingSymbol','lot_size':'lotsize','exchange_token':'token','instrument_type':'instrument'})
        return db



savepath= os.path.join(BASE_DIR,"shoonya.json")
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
                findata['broker']='SHOONYA'
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
                                data1[i]['broker']='SHOONYA'
                                data1[i]['token']= data['tk']
                                data1[i]['volume']= data['v'] if 'v' in data.keys() else 0
                        datasub = json.dump(data1,incomingfile, indent=4)
                        incomingfile.truncate()
                        incomingfile.close()
                        
                
        
            
        except KeyError as e :
            print(e)
            pass














    
class growwsetup(object):
    def __init__(self,client_id ,secret_key , token=''):

      self.groww = GrowwAPI(API_AUTH_TOKEN)
      self.client_id=client_id
      self.access_token= self.gettoken()
      self.fyers = fyersModel.FyersModel(token=self.access_token,is_async=False,client_id=self.client_id,log_path=logpathfron1)

        
    def gettoken(self):
        try:
            logpath= os.path.join(BASE_DIR,'shoonyalogin')
            logpath= os.path.normpath(logpath)
            logpath= os.path.join(logpath,f"{self.user}.json")
            logpath= os.path.normpath(logpath)
            print(logpath)




            with open(logpath,'rb')as file:
                token= json.load(file)
            return token
        except Exception as e:
            logpathfron.error('Try Login Again')
            print(e)
        # api = ShoonyaApiPy()
        

    
    def login(self):
        try:
            appSession = fyersModel.SessionModel(client_id = self.client_id, redirect_uri = redirect_uri,response_type=response_type,state=state,secret_key=self.secret_key,grant_type=grant_type)

            generateTokenUrl = appSession.generate_authcode()
            webbrowser.open(generateTokenUrl,new=1)
            
            appSession.set_token(auth_code)
            response = appSession.generate_token()
            access_token = response["access_token"]

            token= {"Token":response['access_token']}
            logpath= os.path.join(BASE_DIR,'fyerslogin')
            logpath= os.path.normpath(logpath)



            if not os.path.exists(logpath):
                os.makedirs(logpath)
                print(f"Folder created at: {logpath}")
            else:
                print(f"Folder already exists at: {logpath}")
            logpath= os.path.join(logpath,f"{self.client_id}.json")
            logpath= os.path.normpath(logpath)

            finalout=open(logpath, 'w')
            json.dump(token, finalout)
            finalout.close()
            logpathfron.info('Login sucessful')



            return True,None
        except Exception as e:
            logpathfron.error(e)
            return False,e

    def logout(self):
        tokenkey=self.gettoken()
        param= dict()
        param['uid']= tokenkey['uid']
        param['actid']=tokenkey['actid']
        param= json.dumps(param)
        data = "jData="+param+"&jKey="+tokenkey['Token']
        ret= requests.post(self.baseurl+"Logout",data=data)




  
            

    


    

    
    
    
    
    
    
    
    
    
    
    

    
class HTTP(growwsetup):
   
    
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

            if orderparam['orertype']='LIMIT':
                ORDTYPE=1

            if orderparam['orertype']='MARKET':
                ORDTYPE=2

            if orderparam['product_type']='INTRADAY' :
                PRDTYPE='INTRADAY'
            
            if orderparam['product_type']='CARRYFORWARD' :
                PRDTYPE='MARGIN'
            

            

            data ={"symbol":orderparam['tradingsymbol'],
            "qty":orderparam['quantity'], 
            "validity":'DAY',
            "exchange":orderparam['exchange'],
            "productType":PRDTYPE,
            "type":ORDTYPE,
            "order_type":orderparam['ordertype'],
            "side":ttp,
            "limitPrice":orderparam['ltp'],               # Optional: Price of the stock (for Limit orders)
            # trigger_price=orderparam['ltp'],
            "disclosedQty": orderparam['discloseqty']}
                # Optional: Trigger price (if applicable)
            

                
            
            
            orderiddta = self.fyers.place_order(data)
                                               
                                            

            if orderiddta['data']:
                orderobject.quantity= orderparam['quantity']
                orderobject.ordertype= orderparam['ordertype']
                orderobject.product_type= orderparam['product_type']
                orderobject.avg_price= orderparam['ltp']
                orderobject.transactiontype= orderparam['transactiontype']
                orderobject.discloseqty= orderparam['discloseqty']
                orderobj.orderid=orderiddta['groww_order_id']
                orderobj.orderstatus=orderiddta['order_status']

                orderobject.save()
          
                logpathfron.info(f'Broker Shoonya order placed, orderid :{orderiddta['groww_order_id']}')

                return data,None
                
            else:
                    return False,data
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
            if ret['positions']:
                for i in position:
                            
                        findata['exchange'] = i['exchange']
                        findata['tradingsymbol'] = i['trading_symbol']
                        findata['buyavgprice'] = i['credit_price']
                        findata['sellavgprice'] = i['debit_price']
                        findata['netqty'] = i['quantity']
                        # findata['ltp'] = i['lp']
                        # findata['lotsize'] = i['ls']
                        # # findata['unrealised'] = i['urmtom']
                        # findata['realised'] = i['rpnl']
                        listfin.append(finaldata)
                
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
            listfin=[]
            if ret['holdings']:
         
              
                for i in position:
                            
                    
                        findata['tradingsymbol'] = i['trading_symbol']
                        findata['quantity'] = i['quantity']
                        findata['averageprice'] = i['average_price']


                        listfin.append(finaldata)
                
                        return listfin ,None
            else:
                    return None,'Not found'


        except Exception as e:
            print(e)
            return None,e



    def checkfunds (self):
        try:
            cash = self.fyers.funds ()

            return cash['clear_cash'],None
            
          

        except Exception as e:
            print(e)
            return None,e


    

class WebSocketConnect(growwsetup):
    def __init__(self,user, pwd, vendorcode,app_key, imei,token,tokenlist=None):
        super().__init__(user, pwd, vendorcode,app_key, imei,token)

        self.feed = GrowwFeed(self.groww)




    def onmessage(self,message):
    """
    Callback function to handle incoming messages from the FyersDataSocket WebSocket.

    Parameters:
        message (dict): The received message from the WebSocket.

    """
    print("Response:", message)


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


    def onopen(self,):
        """
        Callback function to subscribe to data type and symbols upon WebSocket connection.

        """

        data_type = "SymbolUpdate"
        symbols = self.subscribetoken()

        fyers.subscribe(symbols=symbols, data_type=data_type)
        unsymbol = self.unsubscribetoken()
        
        fyers.subscribe(symbols=unsymbol, data_type=data_type)

        fyers.keep_running()




    def newevent(self):
        obj = md.watchlist.objects.filter(newevent=True,broker='GROWW').last()
        if obj:
            return obj,obj.newevent
        else:
            return obj, False

    def unsubscribetoken(self):
            try:

                obj = md.watchlist.objects.filter(subscribe=False,broker='GROWW')
                tokenlist=[]
                for  i in obj:
                  
                    
                    instruments_list =f"{i.exchange}:{i.tradingsymbol}"
                    tokenlist.append(instruments_list)              
                return tokenlist
            except Exception as e :
                print(e)
    def subscribetoken(self):
          

            try:
                
                obj = md.watchlist.objects.filter(subscribe=True,broker='GROWW')
                tokenlist=[]
                for  i in obj:
                    instruments_list =f"{i.exchange}:{i.tradingsymbol}"
                   
                    tokenlist.append(instruments_list)
                return tokenlist
            except Exception as e :
                print(e)


    
    async def start_thread(self):
        fyers = data_ws.FyersDataSocket(
                        access_token=self.access_token,       # Access token in the format "appid:accesstoken"
                        log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
                        litemode=False,                  # Lite mode disabled. Set to True if you want a lite response.
                        write_to_file=False,              # Save response in a log file instead of printing it.
                        reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
                        on_connect=onopen,               # Callback function to subscribe to data upon connection.
                        on_close=onclose,                # Callback function to handle WebSocket connection close events.
                        on_error=onerror,                # Callback function to handle WebSocket errors.
                        on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
                    )
      

        fyers.connect()

        

      












 