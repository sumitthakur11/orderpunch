
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
logpathfron= os.path.normpath(logger2path)
logpathfron=env.setup_logger(logpathfron)

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
            # print(db)


        
        
        if instrument=='OPTSTK' or instrument=='OPTIDX'  :
            db =db[db['segment']=='FNO']

            db =db[db['instrument_type'].isin(['CE', 'PE']) ]
            # print(db)


        if instrument =='EQ' and name:
            db =db[db['instrument_type']=='EQ']
            db =db[db['trading_symbol']==name]

        else:

            if  name and instrument and exchange:
                db =db[db['exchange']==exchange]
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
    def __init__(self, token=''):
    
      self.groww = GrowwAPI(token)

class HTTP(growwsetup):
   
    
    def cancel_order(self, exchange,orderno):
    
        if exchange == "NSE" or exchange =='BSE':
            segment = self.groww.SEGMENT_CASH 
        elif exchange=='NFO'or exchange=='BFO':
            segment = 'FNO'


            

        data = self.groww.cancel_order( segment=segment,groww_order_id=orderno)
        
        return data
    
    
    def modifyorder(self,data,orderobject):
        
        try:
            print(data,'modify')

            if data['exchange'] == "NSE" or data['exchange']  =='BSE':
                segment = 'CASH'
            elif data['exchange'] =='NFO'or data['exchange'] =='BFO':
                segment = 'FNO'
            res = self.groww.modify_order(quantity =data['quantity'],segment =segment ,groww_order_id =orderobject.orderid, price=float(data['ltp']),order_type=data['ordertype'])
            print(res,"res")
            if res['groww_order_id']:
                orderobject.orderid=res['groww_order_id']
                orderobject.save()

                return data,None
            else:
                return False,data
        except Exception as e:
            print(e)
            return False,e


   
    
  
    
    def placeorder(self,orderparam,orderobject):
        try:
            if orderparam['exchange'] == "NSE" or orderparam['exchange'] =='BSE':
                segment = self.groww.SEGMENT_CASH 
            elif orderparam['exchange']=='NFO'or orderparam['exchange']=='BFO':
                segment = 'FNO'

            if orderparam['product_type']=='DELIVERY':
                PRD='CNC'
            if orderparam['product_type']=='INTRADAY':
                PRD='MIS'
            if orderparam['product_type']=='INTRADAY':
                PRD='NRML'


            

                
            
            
            orderiddta = self.groww.place_order(
                                                trading_symbol=orderparam['tradingsymbol'],
                                                quantity=orderparam['quantity'], 
                                                validity=self.groww.VALIDITY_DAY,
                                                exchange=orderparam['exchange'],
                                                segment=segment,
                                                product=PRD,
                                                order_type=orderparam['ordertype'],
                                                transaction_type=orderparam['transactiontype'],
                                                price=orderparam['ltp'],               # Optional: Price of the stock (for Limit orders)
                                                trigger_price=orderparam['ltp'],       # Optional: Trigger price (if applicable)
                                            )
            print(orderiddta    )
            if orderiddta['groww_order_id']:
           
                orderparam['orderid']=orderiddta['groww_order_id']
                orderparam['orderstatus']=orderiddta['order_status']
                orderparam['lotsize']=int(orderparam['lotsize']) 



                orderobject(orderparam)
          
                logpathfron.info(f'Broker Shoonya order placed, orderid :{orderiddta['groww_order_id']}')

                return data,None
                
            else:
                    return False,data
        except Exception as e:
            logpathfron.error(e)
            return False,e


           



      

  
    
    
    def orderBook(self):
        """
        Info :Get order status
        """
        data = self.groww.get_order_list()
        data=data['order_list']
        return data
   



    def getposition (self):
        try:
        
            ret= self.groww.get_positions_for_user()
            print(ret)
            findata= dict()
            listfin=[]
            if ret['positions']:
                for i in ret['positions']:
                            
                        findata['exchange'] = i['exchange']
                        findata['tradingsymbol'] = i['trading_symbol']
                        findata['buyavgprice'] = i['credit_price']
                        findata['sellavgprice'] = i['debit_price']
                        findata['netqty'] = i['quantity']
                        # findata['ltp'] = i['lp']
                        # findata['lotsize'] = i['ls']
                        # # findata['unrealised'] = i['urmtom']
                        # findata['realised'] = i['rpnl']
                        listfin.append(findata)
                        findata= {}
                
                return listfin ,None
            else:
                    return None,'Not found'



        except Exception as e:
            print(e)
            return None,e

    
    def allholding (self):
        try:
            
            ret= self.groww.get_holdings_for_user()
      
            print(ret)
            findata= dict()
            listfin=[]
            if ret['holdings']:
         
              
                for i in ret['holdings']:
                            
                    
                        findata['tradingsymbol'] = i['trading_symbol']
                        findata['quantity'] = i['quantity']
                        findata['averageprice'] = i['average_price']



                        listfin.append(findata)
                        findata= {}

                
                return listfin ,None
            else:
                    return None,'Not found'


        except Exception as e:
            print(e)
            return None,e



    def checkfunds (self):
        try:
            cash = self.groww.get_available_margin_details ()
            print(cash)

            return cash['clear_cash'],None
            
          

        except Exception as e:
            print(e)
            return None,e


    

class WebSocketConnect(growwsetup):
    def __init__(self,user, pwd, vendorcode,app_key, imei,token,tokenlist=None):
        super().__init__(user, pwd, vendorcode,app_key, imei,token)

        self.feed = GrowwFeed(self.groww)


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
                    if i.exchange == "NSE" or i.exchange =='BSE':
                            segment = self.groww.SEGMENT_CASH 
                    elif i.exchange=='NFO'or i.exchange=='BFO':
                            segment = 'FNO'
                    instruments_list ={"exchange": i.exchange, "segment": segment, "exchange_token": i.symboltoken}
                    tokenlist.append(instruments_list)              
                return tokenlist
            except Exception as e :
                print(e)
    def subscribetoken(self):
          

            try:
                
                obj = md.watchlist.objects.filter(subscribe=True,broker='GROWW')
                tokenlist=[]
                for  i in obj:
                    if i.exchange == "NSE" or i.exchange =='BSE':
                            segment = self.groww.SEGMENT_CASH 
                    elif i.exchange=='NFO'or i.exchange=='BFO':
                            segment = 'FNO'
                    instruments_list ={"exchange": i.exchange, "segment": segment, "exchange_token": i.symboltoken}
                    tokenlist.append(instruments_list)
                return tokenlist
            except Exception as e :
                print(e)


    
    async def start_thread(self):
        def on_data_received(meta): # callback function which gets triggered when data is received
                print("Data received")
                print(self.feed.get_ltp())
                if newevent:
                    tokelistunsb= self.unsubscribetoken()
                    tokelistsubs= self.subscribetoken()
                    if len(tokelistunsb)>0:
                        api.unsubscribe(tokelistunsb)
                    if len(tokelistsubs)>0:
                        api.subscribe(tokelistsubs)
                    objnew.newevent= False
                    objnew.save()

        instruments_list=self.subscribetoken()
        self.feed.subscribe_ltp(instruments_list, on_data_received=on_data_received)

        while True:
            pass
      


      












 