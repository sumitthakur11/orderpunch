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

# from . import serializers as ser
import sys
import yaml
import zipfile
import io
import math
import pickle

# from random import randint

from .ShoonyaApi.api_helper import ShoonyaApiPy
from datetime import datetime, timedelta
import os 
from pathlib import Path
# import ThreadPoolExecutor
log = logging.getLogger(__name__)
api = ShoonyaApiPy()
print(dir(api))

logging.basicConfig(level=logging.DEBUG)


#   
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def optionchain (name,exchange='NFO',instrument=''):

        if exchange == 'NFO':
            data = requests.get('https://api.shoonya.com/NFO_symbols.txt.zip')
        elif exchange =='BFO':
            data = requests.get('https://api.shoonya.com/BFO_symbols.txt.zip')
        elif exchange =='NSE':
            data = requests.get('https://api.shoonya.com/NSE_symbols.txt.zip')
        elif exchange =='BSE':
            data = requests.get('https://api.shoonya.com/BSE_symbols.txt.zip')

    
        db= None
        logpath= os.path.join(BASE_DIR,"extracted_files")
        logpath= os.path.normpath(logpath)
        if not os.path.exists(logpath):
            os.makedirs(logpath)
            print(f"Folder created at: {logpath}")
        else:
            print(f"Folder already exists at: {logpath}")

        print(data.status_code)
        if data.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(data.content)) as zip_ref:
                zip_ref.extractall(logpath)  
            
            if exchange == 'NFO':
                logpath1= os.path.join(logpath,"NFO_symbols.txt")
                logpath1= os.path.normpath(logpath1)
                
                db= pd.read_csv(logpath1,delimiter = ",",keep_default_na=False)
                print('>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            elif exchange =='BFO':
                logpath2= os.path.join(logpath,"BFO_symbols.txt")
                logpath2= os.path.normpath(logpath2)

                db= pd.read_csv(logpath2,delimiter = ",",keep_default_na=False)
            elif exchange =='NSE':
                logpath3= os.path.join(logpath,"NSE_symbols.txt")
                logpath3= os.path.normpath(logpath3)

                db= pd.read_csv(logpath3,delimiter = ",",keep_default_na=False)

            elif exchange =='BSE':
                logpath4= os.path.join(logpath,"BSE_symbols.txt")
                logpath4= os.path.normpath(logpath4)

                
                db= pd.read_csv(logpath4,delimiter = ",",keep_default_na=False)


        else:
            print(f"Failed to download the file. Status code: {data.status_code}")
        
        if  name and instrument and exchange:
            db =db[db['Exchange']==exchange]
            db =db[db['Instrument']==instrument]
            db =db[db['Symbol']==name]
        else:
            db =db[db['Exchange']==exchange]







        
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














    
class shoonyasetup(object):
    def __init__(self, user=1, pwd='', vendorcode= '',app_key='', imei='',token=''):

        broker = md.Broker.objects.filter(brokername='SHOONYA').last()
        self.user = user  
        self.pwd = broker.password
        self.app_key = broker.apikey
        self.imei = 'abc1234'
        self.vendorcode= broker.vendorcode
        self.auth=None
        token= broker.AuthToken
        self.baseurl = 'https://api.shoonya.com/NorenWClientTP/'
        self.otp = pyotp.TOTP(token).now()
        
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
            print(e)
        # api = ShoonyaApiPy()
        

    
    def login(self):
        try:

            res = api.login(userid=self.user, password=self.pwd,vendor_code= self.vendorcode,api_secret=self.app_key,imei=self.imei, twoFA=self.otp)
            token={}
            if res['stat']=='Ok':
                token= {"Token":res['susertoken'],"uid":res['uid'],"actid":res['actid']}
                
            # token= json.dumps(token)
            print(token)
            
            logpath= os.path.join(BASE_DIR,'shoonyalogin')
            logpath= os.path.normpath(logpath)



            if not os.path.exists(logpath):
                os.makedirs(logpath)
                print(f"Folder created at: {logpath}")
            else:
                print(f"Folder already exists at: {logpath}")
            logpath= os.path.join(logpath,f"{self.user}.json")
            logpath= os.path.normpath(logpath)

            finalout=open(logpath, 'w')
            json.dump(token, finalout)
            finalout.close()
            return True,None
        except Exception as e:
            return False,e

    def logout(self):
        tokenkey=self.gettoken()
        param= dict()
        param['uid']= tokenkey['uid']
        param['actid']=tokenkey['actid']
        param= json.dumps(param)
        data = "jData="+param+"&jKey="+tokenkey['Token']
        ret= requests.post(self.baseurl+"Logout",data=data)




  
            

    


    

    
    
    
    
    
    
    
    
    
    
    

    
class HTTP(shoonyasetup):
    # def __init__(self,user='FA383345', pwd=pwd, vendorcode= 'FA383345_U',app_key=apikey, imei=imei,token=token):
    #         super().__init__(self)
    #         self.user=user
    #         self.api=self.get_shoonya_client()
    def wallet(self):
    
        """Get a list of accounts.

        Required args:
            None
        """
        """"api endpoint to fetch balance and account detail
        *kwargs: symbol (not mandatory)
        """
        data= api.get_limits()
        return data
    

    
    def cancel_order(self, orderno):
        data = api.cancel_order( orderno=orderno)
        return data
    
    
    def modifyorder(self,exchange, tradingsymbol, orderno, newprice,PAPER,orderobject):

        data= None
        
        if not PAPER:
            data = api.modify_order(exchange= exchange,
                                        tradingsymbol=tradingsymbol,
                                        orderno=orderno, newprice=newprice,newtrigger_price=newprice+1)
        orderobject.sellorderstatus='MODIFIED'
        orderobject.sellprice= float(newprice)
        if PAPER:
            # orderobject.status=False
            pass
        
        orderobject.save()
        return data
    


    def order_history(self,orderid):
        """
        Info :Get order status by order id  
        args: orderid 
        """
        data = api.single_order_history(orderid=orderid)
        return data
    
  
    
    def placeorder(self,orderparam,orderobject,STOPLOSS,PAPER):
        
        exchange_segment= orderparam['exchange']
        buy_or_sell=orderparam['transactiontype']
        if orderparam['product_type'].upper()== "INTRADAY":
            product_type="I"
        elif orderparam['product_type'].upper() == "CARRYFORWARD":
            product_type="M"
        elif orderparam['product_type'].upper() == "DELIVERY":
            product_type="C"

        if orderparam['transactiontype'].upper()== "BUY":
            buy_or_sell='B'
        elif orderparam['transactiontype'].upper() == "SELL":
            buy_or_sell='S'

        price_type= 'MKT' if orderparam['ordertype']=='MARKET' else "LMT"
        price=orderparam['ltp']
        tradingsymbol=orderparam['tradingsymbol']
        discloseqty='0'
        trigger_price='0'
        retention='IOC'
        remarks='NA'
        amo='NO'
        data= None
        orderparam['avg_price']=orderparam['ltp']
        orderparam['status']=True

        

        if not PAPER:
            param= dict()
            tokenkey=self.gettoken()
            param['uid']= tokenkey['uid']
            param['exch']=exchange_segment
            param['actid']=tokenkey['actid']
            param['tsym']=tradingsymbol
            param['qty']=str(orderparam['quantity'])
            param['prc']=str(orderparam['ltp'])
            param['trgprc']=trigger_price
            param['dscqty']=str(discloseqty)
            param['prd']=product_type
            param['trantype']=buy_or_sell
            param['prctyp']=price_type
            param['ret']=retention
            param= json.dumps(param)
            data = "jData="+param+"&jKey="+tokenkey['Token']
            print(data)
            ret= requests.post(self.baseurl+"PlaceOrder",data=data)
            print(ret.text,ret.json().keys(),'keyssssssssssss>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            if ret.status_code==200:
                ret=ret.json()
                status=self.order_history(str(ret['norenordno']),tokenkey)
                orderparam['orderid']=ret['norenordno']
                orderparam['orderstatus']= status['status'].upper()
                orderparam['status']=True if status['status'].upper()=='COMPLETE' else False
                orderparam['user']=1
                orderparam['broker']='SHOONYA'
                orderparam['avg_price']=status['prc']
                orderobject(orderparam)
                return data
            
            else:
                return None

           

            
            # data = api.place_order(buy_or_sell,product_type,exchange_segment, tradingsymbol, orderparam['quantity'], discloseqty,price_type, price, trigger_price)
            # status=self.order_history(str(data['norenordno']))
            # status= status[0]
            # orderparam['buyorderid']=data['norenordno']
            # orderparam['orderstatus']= status['status'].upper()
            # orderparam['status']=True if status['status'].upper()=='COMPLETE' else False





      

    def order_history(self,orderno,tokenkey):
        param= dict()
        param['norenordno']=orderno
        param['uid']= tokenkey['uid']
        param['actid']=tokenkey['actid']

        
        
        param= json.dumps(param)
        data = "jData="+param+"&jKey="+tokenkey['Token']
        ret= requests.post(self.baseurl+"SingleOrdHist",data=data)
        print(ret.text,ret.json(),'keyssssssssssss>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        ret= ret.json()
        ret=ret[0]

        return ret
    
    
    def get_order_book(self):
        """
        Info :Get order status
        """
        data = api.get_order_book()
        return data
    def searchscrip(self,exchange,SymbolName,ExpDate=None,type_=None,strike=[]):
        
        symbol = None
        Symbol= SymbolName
        symbolLIST= []
        nfo=[]
        
        for i in range(len(strike)):
            x= f'{SymbolName}{ExpDate}{type_}{strike[i]}'
            symbolLIST.append(x)
            nfo.append(exchange)

        token= []
        symbolslist= []
        tradesymbols= None
        ret=[]
        ret = list(map(api.searchscrip,nfo,symbolLIST))
        if ret != []:
            for i in range(len(ret)):
                symbols = ret[i]['values']
                for symbol in symbols:
                    token.append(symbol['token'])
                    symbolslist.append(symbol['tsym'])
# 
        return symbolslist,token

    

    def get_quotes (self,exchange,TK):
        try:
        
        
        # print(TK)
            #ret = api.get_quotes(exchange=exchange, token=str(TK))
            param= dict()
            data= dict()
            tokenkey=self.gettoken()
            param['uid']= tokenkey['uid']
            param['exch']=exchange
            param['token']= str(TK)
            param['actid']=tokenkey['actid']
            # data['jData']=param
            param= json.dumps(param)
            # param=str([param])
            data = "jData="+param+"&jKey="+tokenkey['Token']
            ret= requests.post(self.baseurl+"GetQuotes",data=data)

            print(ret.text,ret.json().keys(),'keyssssssssssss>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            
            if ret.status_code==200:
                return ret.json()
            
            elif ret['stats']=='Not_Ok':
                return None
            else:
                return None

        except Exception as e:
            print(e)

    def getindex (self):
        ret= api.GetIndexList()
        return ret
    
    

class WebSocketConnect(shoonyasetup):
    def __init__(self,user, pwd, vendorcode,app_key, imei,token,tokenlist=None):
        super().__init__(user, pwd, vendorcode,app_key, imei,token)

     
        self.NIFTY= 26000
        self.NIFTYBANK=26009
        self.FINNIFTY=26037
        self.MIDCAP= 26074
        self.SENSEX=1
        self.key = app_key
        feed_opened = False
        self.ltp= None
        self.tokenlist= tokenlist if len(tokenlist)>0 else ["NSE|26000"]
        self.login()

    def newevent(self):
        obj = md.watchlist.objects.filter(newevent=True,broker='SHOONYA').last()
        if obj:
            return obj,obj.newevent
        else:
            return obj, False

    def unsubscribetoken(self):
            try:

                obj = md.watchlist.objects.filter(subscribe=False,broker='SHOONYA')
                tokenlist=[]
                for  i in obj:
                        tlist= f"{i.exchange}|{i.symboltoken}"
                        i.delete()
                        tokenlist.append(tlist)
                return tokenlist
            except Exception as e :
                print(e)
    def subscribetoken(self):
            try:

                obj = md.watchlist.objects.filter(subscribe=True,broker='SHOONYA')
                tokenlist=[]
                for  i in obj:
                        tlist= f"{i.exchange}|{i.symboltoken}"
                        tokenlist.append(tlist)
                return tokenlist
            except Exception as e :
                print(e)


    
    async def start_thread(self):
        def event_handler_order_update(tick_data):
            
            pass

        def event_handler_feed_update(tick_data):
            print(tick_data)
            Ltp(data=tick_data)
            objnew,newevent= self.newevent()
            if newevent:
                tokelistunsb= self.unsubscribetoken()
                tokelistsubs= self.subscribetoken()
                if len(tokelistunsb)>0:
                    api.unsubscribe(tokelistunsb)
                if len(tokelistsubs)>0:
                    api.subscribe(tokelistsubs)
                objnew.newevent= False
                objnew.save()
            
            
           

        def open_callback():
            global feed_opened
            feed_opened = True
            api.subscribe(self.tokenlist)



        api.start_websocket( 
                             subscribe_callback=event_handler_feed_update, 
                             socket_open_callback=open_callback)


        while True:

            pass
        













 