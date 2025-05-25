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
from Tradingbot import env
from .ShoonyaApi.api_helper import ShoonyaApiPy
from datetime import datetime, timedelta
import os 
from pathlib import Path
import pathlib


path = pathlib.Path(__file__).resolve().parent.parent.parent
# import ThreadPoolExecutor
log = logging.getLogger(__name__)
api = ShoonyaApiPy()
print(dir(api))

logging.basicConfig(level=logging.DEBUG)


#   


logger2path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpathfron= os.path.normpath(logger2path)
logpathfron=env.setup_logger(logpathfron)

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
           

            if data['t']=='tk' and data['tk']!=tokenltp:    
                
                obj = md.watchlist.objects.filter(broker='SHOONYA',symboltoken=data['tk']).last()
                obj.ltp= data['lp']
                obj.volume= data['v']  if 'v' in data.keys() else 0
                obj.save()

            if data['t']=='tf':
                obj = md.watchlist.objects.filter(broker='SHOONYA',symboltoken=data['tk']).last()
                obj.ltp= data['lp']
                obj.volume= data['v']  if 'v' in data.keys() else 0
                obj.save()
                        
                
        
            
        except KeyError as e :
            print(e)
            pass














    
class shoonyasetup(object):
    def __init__(self, user=1, pwd='', vendorcode= '',app_key='', imei='',token=''):

        self.user = user  
        self.pwd = pwd
        self.app_key = app_key
        self.imei = 'abc1234'
        self.vendorcode= vendorcode
        self.auth=None
        token= token
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
            logpathfron.error('Try Login Again')
            print(e)
        # api = ShoonyaApiPy()
        

    
    def login(self):
        try:

            res = api.login(userid=self.user, password=self.pwd,vendor_code= self.vendorcode,api_secret=self.app_key,imei=self.imei, twoFA=self.otp)
            token={}
            if res['stat']=='Ok':
                token= {"Token":res['susertoken'],"uid":res['uid'],"actid":res['actid']}
                logpathfron.info('Login sucessful')

                
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
            if res['stat']=='Ok':
                logpathfron.info('Shoonya Login sucessful')


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




  
            

    


    

    
    
    
    
    
    
    
    
    
    
    

    
class HTTP(shoonyasetup):
    # def __init__(self,user='FA383345', pwd=pwd, vendorcode= 'FA383345_U',app_key=apikey, imei=imei,token=token):
    #         super().__init__(self)
    #         self.user=user
    #         self.api=self.get_shoonya_client()
 
    
    # cancel modify orderbook replacement
    

    def cancel_order (self,orderid):
        try:
            
      
            param= dict()
            data= dict()
            tokenkey=self.gettoken()
            param['uid']= tokenkey['uid']
            param['actid']=tokenkey['actid']
            param['prd']='C'
            param['norenordno']=orderid
    
            param= json.dumps(param)
            data = "jData="+param+"&jKey="+tokenkey['Token']
            ret= requests.post(self.baseurl+"CancelOrder",data=data)
            findata= dict()
            if ret.status_code==200:
                position =ret.json()
                print(position)
                                
                return position
            else:
                    return None


        except Exception as e:
            print(e)
            return None

    
    def modifyorder(self,data,orderobject):

        try:
            
      
            param= dict()
            data= dict()
            tokenkey=self.gettoken()
            param['uid']= tokenkey['uid']
            param['actid']=tokenkey['actid']
            param['prd']='C'
            param['norenordno']=orderobject.orderid
            param['qty']=data['quantity']
            param['tsym']=data['tradingsymbol']
            param['prc']=data['ltp']
            param['prctyp']=data['product_type']

            


    
            param= json.dumps(param)
            data = "jData="+param+"&jKey="+tokenkey['Token']
            ret= requests.post(self.baseurl+"ModifyOrder",data=data)
            findata= dict()
            if ret.status_code==200:
                
                position =ret.json()
                if position['stat']=='Ok':
                    orderobj.orderid=position['result']
                
                    orderobj.save()
                                
                    return position,None
                else:
                    return None,position['emsg']


        except Exception as e:
            print(e)
            return None,e


    
  
    
    def placeorder(self,orderparam,orderobject,STOPLOSS,PAPER):
        try:

        
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
            discloseqty=int(float(orderparam['discloseqty']))
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
                    logpathfron.info(f'Broker Shoonya order placed, orderid :{ret['norenordno']}')

                    return data
                
                else:
                    return None
        except Exception as e:
            logpathfron.error(e)

           

       




      

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
    
   
    


    def getposition (self):
        try:
        
      
            param= dict()
            data= dict()
            tokenkey=self.gettoken()
            param['uid']= tokenkey['uid']
            param['actid']=tokenkey['actid']
    
            param= json.dumps(param)
            data = "jData="+param+"&jKey="+tokenkey['Token']
            ret= requests.post(self.baseurl+"PositionBook",data=data)

            print(ret.text,ret.json().keys(),'keyssssssssssss>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            findata= dict()
            listfin=[]
            if ret.status_code==200:
                position =ret.json()
                if position['stat']=='Ok':
                    for i in position:
                            
                        findata['exchange'] = i['exch']
                        findata['tradingsymbol'] = i['tsym']
                        findata['buyavgprice'] = i['daybuyavgprc']
                        findata['sellavgprice'] = i['daysellavgprc']
                        findata['netqty'] = i['netqty']
                        findata['ltp'] = i['lp']
                        findata['lotsize'] = i['ls']
                        findata['unrealised'] = i['urmtom']
                        findata['realised'] = i['rpnl']
                        listfin.append(finaldata)
                
                    return listfin ,None
                else:
                    return None,'Not found'


        except Exception as e:
            print(e)
            return None,e

    
    def allholding (self):
        try:
            
      
            param= dict()
            data= dict()
            tokenkey=self.gettoken()
            param['uid']= tokenkey['uid']
            param['actid']=tokenkey['actid']
            param['prd']='C'
    
            param= json.dumps(param)
            data = "jData="+param+"&jKey="+tokenkey['Token']
            ret= requests.post(self.baseurl+"Holdings",data=data)
            print(ret)
            findata= dict()
            listfin=[]
            if ret.status_code==200:
                position =ret.json()
                print(position)
                if not  position==[]:
                    for i in position:
                            
                        findata['exchange'] = i['exch_tsym'][0]['exch']
                        findata['tradingsymbol'] = i['exch_tsym'][2]['tsym']
                        findata['symboltoken'] = i['exch_tsym'][1]['token']
                        findata['quantity'] = i['holdqty']
                        findata['averageprice'] = i['upldprc']


                        listfin.append(finaldata)
                
                    return listfin ,None
                else:
                    return None,'Not found'


        except Exception as e:
            print(e)
            return None,e


    def orderbook (self):
        try:
            
      
            param= dict()
            data= dict()
            tokenkey=self.gettoken()
            param['uid']= tokenkey['uid']
            param['actid']=tokenkey['actid']
            param['prd']='C'
    
            param= json.dumps(param)
            data = "jData="+param+"&jKey="+tokenkey['Token']
            ret= requests.post(self.baseurl+"OrderBook",data=data)
            findata= dict()
            listfin=[]
            if ret.status_code==200:
                position =ret.json()
                print(position)
                                
                return position
            else:
                    return None


        except Exception as e:
            print(e)
            return None


    def checkfunds (self):
        try:
        
      
            param= dict()
            data= dict()
            tokenkey=self.gettoken()
            param['uid']= tokenkey['uid']
            # param['exch']=exchange
            # param['token']= str(TK)
            param['actid']=tokenkey['actid']
    
            param= json.dumps(param)
            data = "jData="+param+"&jKey="+tokenkey['Token']
            ret= requests.post(self.baseurl+"Limits",data=data)

            print(ret.text,ret.json().keys(),'keyssssssssssss>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            
            if ret.status_code==200:
                cash =ret.json()
                cash = cash['cash']
                return cash ,None
            
          

        except Exception as e:
            print(e)
            return None,e



    
    

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
        













 