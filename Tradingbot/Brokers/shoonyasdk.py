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
BASE_DIR = Path(__file__).resolve().parent.parent

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
        
        
        db =db[db['Exchange']==exchange]
        db =db[db['Instrument']==instrument]
        db =db[db['Symbol']==name]



        
        return db

    
    
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
        res = api.login(userid=self.user, password=self.pwd,vendor_code= self.vendorcode,api_secret=self.app_key,imei=self.imei, twoFA=self.otp)
        print(res,'res')
        print(type(res),res.keys())
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
    
    
    # def getorderlist(self):
    #     """
    #     Info :Get order status
    #     """
    #     data = self.kite.orders()
    #     return data
    
    def placeorder(self,orderparam,orderobject,STOPLOSS,PAPER):
        
        exchange_segment= orderparam['exchange']
        buy_or_sell=orderparam['transactiontype']
        if orderparam['product_type'].upper()== "INTRADAY":
            product_type="I"
        elif orderparam['product_type'].upper() == "CARRYFORWARD":
            product_type="C"
        elif orderparam['product_type'].upper() == "DELIVERY":
            product_type="C"

        if orderparam['transactiontype'].upper()== "BUY":
            buy_or_sell='B'
        elif orderparam['transactiontype'].upper() == "SELL":
            buy_or_sell='S'

        price_type= 'MKT' if orderparam['ordertype']=='MARKET' else "LMT"
        price=orderparam['ltp']
        tradingsymbol=orderparam['tradingsymbol']
        discloseqty=orderparam['quantity']
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
                orderparam['buyorderid']=ret['norenordno']
                orderparam['orderstatus']= status['status'].upper()
                orderparam['status']=True if status['status'].upper()=='COMPLETE' else False
                orderparam['user']=1
                orderparam['broker']='SHOONYA'
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

    # def searchscrip(self,exchange,searchtext):
    #     RES= api.searchscrip(exchange=exchange, searchtext=searchtext)

    #     return RES

    

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
    
    














 