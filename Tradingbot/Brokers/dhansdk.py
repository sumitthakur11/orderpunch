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
import io 
from random import randint

import pandas as pd 
from dhanhq import marketfeed
import os 
from dhanhq import dhanhq
from Tradingbot import env
from Tradingbot import models as md
import pathlib
from datetime import datetime, timedelta
# import ThreadPoolExecutor

path = pathlib.Path(__file__).resolve().parent.parent.parent

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)



logger1path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpath1= os.path.normpath(logger1path)
logpath1=env.setup_logger(logpath1)

def searchscrip (name,exchange='NFO',instrument=''):
        print(name,exchange,instrument)

        
        data = requests.get('https://images.dhan.co/api-data/api-scrip-master.csv')
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

       
            


        if instrument=='EQ':
            instrument='EQUITY'
        if  name and instrument and exchange:
            db =db[db['SEM_EXM_EXCH_ID']==exchange]
            db =db[db['SEM_INSTRUMENT_NAME']==instrument]
            db['SEM_CUSTOM_SYMBOL'] =db['SEM_CUSTOM_SYMBOL'].str.split().str[0]

            print(db['SEM_CUSTOM_SYMBOL'])

            db =db[db['SEM_CUSTOM_SYMBOL']==name]
        else:
            db =db[db['SEM_EXM_EXCH_ID']==exchange]
        


        db=db.rename(columns={'SEM_TRADING_SYMBOL':'TradingSymbol','SEM_LOT_UNITS':'lotsize','SEM_SMST_SECURITY_ID':'token','SEM_INSTRUMENT_NAME':'instrument'})
        return db




class Ltp:
    def __init__(self,data) :
        self.data= {}
        self.finaldata= []
        if  data['LTP']['type']=='Ticker Data':
            self.data['security_id']=data['LTP']['instrument_token']
            self.data['LTP']= data['LTP']['last_price']
            self.data['exchange_segement']= data['LTP']['volume_traded']
            self.finaldata.append(self.data)
        
        print(self.finaldata)
        Quotes(self.finaldata)

    







class dhansetup(object):
    def __init__(self,client_id = "101010", access_token=""):
        
        self.dhan = dhanhq(client_id,access_token)
        print(self.dhan)

        
    


 

class HTTP(dhansetup):
  
    
    
    def cancel_order(self, orderno):
        data = self.dhan.cancel_order( orderno=orderno)
        return data
    
    def modifyorder(self,data,orderobj):
    


        data = self.dhan.modify_order(order_id=orderobj.orderid,
                                     order_type=data['ordertype'],
                                     leg_name=leg_name, quantity=quantity, price=data['ltp'],
                                     trigger_price=trigger_price, disclosed_quantity= disclosed_quantity,
                                     validity=validity)
        return data
    
    
    
    def orderbook(self):
        """
        Info :Get order status
        """
        data = self. dhan.get_order_list()
        return data
    
    def placeorder(self,orderparam,orderobject):
        #security_id, exchange_segment, transaction_type, quantity,  order_type, product_type, price
         #common = tradingsymbol,symboltoken,order_type,transactiontype,product_type,price,quantity,exchange,broker
        security_id=orderparam['symboltoken']
        exchange_segment=orderparam['exchange']
        transaction_type=orderparam['transactiontype']
        product_type=orderparam['product_type']
        quantity=orderparam['quantity']
        order_type=orderparam['order_type']
        price=orderparam['price']
        stoploss=orderparam['stoploss']
        
        data=self.dhan.place_order(tag='',transaction_type=transaction_type,exchange_segment=exchange_segment,product_type=product_type,
                        order_type=order_type,validity='DAY',security_id=security_id,quantity=quantity,disclosed_quantity=quantity,
                        price=0,trigger_price=0,after_market_order=False,amo_time='OPEN',bo_profit_value=0,
                        bo_stop_loss_Value=0,drv_expiry_date=None,drv_options_type=None,
                        drv_strike_price=None  )                   
        
        ordersent=dict()
        ordersent['user']=1
        ordersent['buyorderid']=data['orderId']
        ordersent['orderstatus']=data['orderStatus']
        ordersent['status']=True

        
       
        orderobject(ordersent)
        logpath1.info(f'Broker Angel order palced,orderid:{data['orderId']}')

        
        return data


    def checkfunds(self):
        try :
            data =self.dhan.get_fund_limits()

            return data['availabelBalance'],None
        
        except Exception as e:
            return None, e

    
    def getposition(self):
        try:
            findata = dict()
            listfin=[]

            data = self.dhan.get_positions()
            positionall= data
            for i in positionall:
                
  


                            
                findata['exchange'] = i['exchangeSegment']
                findata['tradingsymbol'] = i['tradingSymbol']
                findata['symboltoken'] = i['securityId']
                findata['buyavgprice'] = i['buyAvg']
                findata['sellavgprice'] =  i['sellAvg']
                findata['netqty'] = i['netQty']
                findata['unrealised'] = i['realizedProfit']
                findata['realised'] = i['unrealizedProfit']
                listfin.append(finaldata)
                    
        





            return listfin, None
        except Exception as e:
            return None,e

  
    def allholding(self):
        try:

            findata = dict()
            listfin=[]
            data = self.dhan.get_holdings()

            positionall= data
            for i in positionall:
                findata['tradingsymbol'] = i['tradingSymbol']
                findata['symboltoken'] = i['securityId']
                findata['quantity'] = i['totalQty']
                findata['averageprice'] = i['avgCostPrice']
                listfin.append(finaldata)
                    
        
            return listfin, None
        except Exception as e:
            return None,e




    










    
    
   
    
    def order_history(self,orderno):
        data = self.dhan.order_status(orderno=orderno)
        return order(data)
    
    
        

    
 


class WebSocketConnect(dhansetup):
    def __init__(self, client_id='', access_token='' ):
        
        self.client_id = client_id
        self.access_token = access_token







    def newevent(self):
        obj = md.watchlist.objects.filter(newevent=True,broker='DHAN').last()
        if obj:
            return obj,obj.newevent
        else:
            return obj, False

    def unsubscribetoken(self):
            try:
                
                
                    obj = md.watchlist.objects.filter(subscribe=False,broker='DHAN')
                    tokenlist=[]
                    for i in obj :
                        if i.exchange == 'NSE':
                            subs= (marketfeed.NSE, i.symboltoken, marketfeed.Quote)
                        elif i.exchange=='NFO':
                            subs= (marketfeed.NSE, i.symboltoken, marketfeed.Quote)
                        elif i.exchange=='BFO':
                            subs= (marketfeed.BSE, i.symboltoken, marketfeed.Quote)
                        elif i.exchange=='BSE':
                            subs=(marketfeed.BSE, i.symboltoken, marketfeed.Quote)
                        tokenlist.append(subs)

                    return tokenlist

            except Exception as e :
                print(e)
    def subscribetoken(self):
            
            try:
                
                obj = md.watchlist.objects.filter(subscribe=True,broker='DHAN')
                tokenlist=[]
                for i in obj :
                    if i.exchange == 'NSE':
                        subs= (marketfeed.NSE, i.symboltoken, marketfeed.Quote)
                    elif i.exchange=='NFO':
                        subs= (marketfeed.NSE, i.symboltoken, marketfeed.Quote)
                    elif i.exchange=='BFO':
                       subs= (marketfeed.BSE, i.symboltoken, marketfeed.Quote)
                    elif i.exchange=='BSE':
                        subs=(marketfeed.BSE, i.symboltoken, marketfeed.Quote)
                    tokenlist.append(subs)


            
             


                        
                return tokenlist
            except Exception as e :
                print(e)
                logger1path.error(e)

    

    def start_thread(self):




        try:
            subs= self.subscribetoken()
            self.feed = marketfeed.DhanFeed(client_id=self.client_id,access_token=self.access_token,instruments=subs)
        
            
            while True:
                self.feed.run_forever()
                response = self.feed.get_data()
                obj = md.watchlist.objects.filter(broker='DHAN',symboltoken=data['token']).last()
                obj.ltp= int(data['last_traded_price'])/100
                obj.volume= data['volume_trade_for_the_day']  if 'volume_trade_for_the_day' in data.keys() else 0
                obj.save()

                
                objnew,newevent= self.newevent()
                if newevent:
                    tokelistunsb= self.unsubscribetoken()
                    tokelistsubs= self.subscribetoken()
                    if len(tokelistunsb)>0:
                         self.feed.unsubscribe_symbols(tokelistunsb)
                        
                    if len(tokelistsubs)>0:
                         self.feed.subscribe_symbols(tokelistsubs)

                    objnew.newevent= False
                    objnew.save()





        except Exception as e:
                print(e)



# dh= dhansetup()
# orderparam= dict()
# orderparam['symboltoken']='54445'
# orderparam['exchange']=dh.dhan.NSE_FNO
# orderparam['transactiontype']=dh.dhan.BUY
# orderparam['order_type']=dh.dhan.MARKET
# orderparam['product_type']=dh.dhan.INTRA
# orderparam['quantity']=75
# orderparam['price']=0
# orderparam['stoploss']=0
# print(orderparam)







token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzQ2Nzc5MTU2LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNDE2ODQ4OSJ9._Mmbztj6OvDvuWD5nL6R9a3zWfpZ6gBbCQSecysr7vam3GtHivkJgu_TPm_xCkHOW5J02uhk_nDujlUaGgkfqA'
# http_= HTTP(client_id='1104168489',access_token=token)
# a=http_.placeorder(orderparam,'','')

# print(a)
websock= WebSocketConnect(client_id='1104168489',access_token=token)
websock.start_thread()





 