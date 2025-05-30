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
import platform
from .PythonSDK import MOFSLOPENAPI
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

        if exchange == 'NFO':
            data = requests.get('https://openapi.motilaloswal.com/getscripmastercsv?name=NSEFO')
        elif exchange =='BFO':
            data = requests.get('https://openapi.motilaloswal.com/getscripmastercsv?name=BSEFO')
        elif exchange =='NSE':
            data = requests.get('https://openapi.motilaloswal.com/getscripmastercsv?name=NSE')
        elif exchange =='BSE':
            data = requests.get('https://openapi.motilaloswal.com/getscripmastercsv?name=BSE')

        db= None
        csv_data = io.StringIO(data.text)
        db= pd.read_csv(csv_data,delimiter = ",",keep_default_na=False)
        print(db.head())
        
        if exchange=='NFO':
            exchange= "NSEFO"
        elif exchange=='BFO':
            exchange= "BSEFO"

        if instrument=='EQ':
            instrument=''
        if  name and instrument and exchange:
            db =db[db['exchangename']==exchange]
            db =db[db['instrumentname']==instrument]
            db =db[db['scripshortname']==name]
        else:
            db =db[db['exchangename']==exchange]
        


        db=db.rename(columns={'scripname':'TradingSymbol','marketlot':'lotsize','scripcode':'token','exchangename':'exchange','instrumentname':'instrument'})
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















class motilalsetup(object):
    def __init__(self,clientcode ='', pwd='',apikey='',token=''):

        self.user = clientcode  
        self.pwd =pwd
        self.clientcode = clientcode
        self.vendorcode= clientcode
        self.apikey= apikey
        self.token= token
        self.baseurl = 'https://openapi.motilaloswal.com/'
        self.Mofsl = MOFSLOPENAPI.MOFSLOPENAPI(self.apikey, self.baseurl, self.clientcode, 'Desktop', 'Chrome', '104')
        combined = pwd + apikey
        hashed_password = hashlib.sha256(combined.encode()).hexdigest()
        self.password = hashed_password


        self.headers=self.header()
        

    def header(self):

     
        headers = {
                "Accept": "application/json",
                "User-Agent": "MOSL/V.1.1.0",
                # "Authorization": Authorization['AuthToken'],
                "ApiKey": self.apikey,
                "ClientLocalIp": "1.2.3.4",
                "ClientPublicIp": "1.2.3.4",
                "MacAddress": "00:00:00:00:00:00",
                "SourceId": "WEB",
                "vendorinfo": self.vendorcode,
                "osname": str(os.name),
                "osversion": '10.0.19041',
                "devicemodel": "AHV",
                "manufacturer": "unknown",
                "productname": "Investor",
                "productversion": "1",
                "installedappid": str(uuid.uuid1()),
                "imeino": "abc123",
                "browsername": "Chrome",
                "browserversion": "105"
        }        

        return headers

    def gettoken(self):
        try:
            logpath= os.path.join(BASE_DIR,'motilallogin')
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

            otp = pyotp.TOTP(self.token).now()

            payload= {
                    "userid":self.user,
                    "password" :self.password,
                    "2FA":"18/10/2018",
                    "totp": otp
                        }
            login=requests.post('https://openapi.motilaloswal.com/rest/login/v3/authdirectapi',json=payload,headers=self.headers)
            
            print(login.json())
            if login.status_code==200:

                login=login.json()
                if login['status']=='SUCCESS':
                    token= {"Token":login['AuthToken']}
                    logpathfron.info('Login sucessful')

                        
                    # token= json.dumps(token)
                    print(token)
                    
                    logpath= os.path.join(BASE_DIR,'motilallogin')
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
            logpathfron.error(e)
            return False,e

   




  
            

    


    

    
    
    
    
    
    
    
    
    
    
    

    
class HTTP(motilalsetup):
    # def __init__(self,clientcode ='', pwd='',apikey='',token=''):
    #     super().__init__(clientcode, pwd,apikey,token)
    
  
    
    
    
    

    
    def cancel_order(self, orderid):
        
        orderparams = {"uniqueorderid": orderid}
        ret= requests.post(self.baseurl+"rest/trans/v1/cancelorder",data=orderparams,header=self.headers)
        return ret.json()
    def modifyorder(self,data,orderobject):
        try:

            orderparams = {
            "uniqueorderid": orderobject.orderid,
            "newprice":data['ltp'],
            "producttype":data['product_type'],
            "newordertype":data['ordertype'],
            "neworderduration":'DAY',
            "newquantityinlot ":data['quantity']/data['lotsize'],
            "symboltoken":orderobject.symboltoken,
            'newdisclosedquantity':data['discloseqty'],
            'newtriggerprice':0,
            'lastmodifiedtime':orderobject.updated_at,
            'qtytradedtoday':0
            }
            ret= requests.post(self.baseurl+"rest/trans/v1/placeorder",data=orderparams,header=self.headers)

            if orderiddta['status']=='SUCCESS':
               return True, None
            else:
                return False,orderiddta['message']
        except Exception as e :
            return None,e


    
    


    
  
    
    def placeorder(self,orderparam,orderobject):
        try:
            print(orderparam)
            Authorization= self.gettoken()
            self.headers['Authorization'] = Authorization['Token']
        
            exchange_segment= orderparam['exchange']
            buy_or_sell=orderparam['transactiontype']
            if orderparam['product_type'].upper()== "INTRADAY":
                product_type="NORMAL"
            elif orderparam['product_type'].upper() == "CARRYFORWARD":
                product_type="M"
            elif orderparam['product_type'].upper() == "DELIVERY":
                product_type="DELIVERY"

           


            
            price_type= 'MARKET' if orderparam['ordertype']=='MARKET' else "LIMIT"
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

            

            
            param= dict()
            param['exchange']=exchange_segment
            param['symboltoken']= int(orderparam['symboltoken'])
            param['buyorsell']=buy_or_sell
            param['ordertype']=price_type
            param['producttype']=product_type
            param['orderduration']='DAY'
            param['price']=int(orderparam['ltp'])
            param['triggerprice']=int(trigger_price)
            param['quantityinlot']=int(int(orderparam['quantity'])/int(orderparam['lotsize']))
            param['disclosedquantity']=discloseqty
            param['amoorder']="N"

            # param= json.dumps(param)
            print(param)
            ret= requests.post(self.baseurl+"rest/trans/v1/placeorder",json=param,headers=self.headers)
            ret= ret.json()
            print(ret)
            if ret['status']=='SUCCESS':
                ret=ret.json()
                status=self.orderBook()
                status = pd.DataFrame(status['data'])
                status=status [status['uniqueorderid']==ret['uniqueorderid']]
                orderparam['orderid']=ret['uniqueorderid']
                orderparam['orderstatus']= status['orderstatus'].iloc[-1].upper()
                orderparam['status']=True if status['orderstatus'].upper()=='COMPLETE' else False
                orderparam['user']=1
                orderparam['broker']='MOTILAL'
                orderparam['avg_price']=status['averageprice'].iloc[-1].upper()

                orderobject(orderparam)
                logpathfron.info(f'Broker Shoonya order placed, orderid :{ret['uniqueorderid']}')

                return data
            
            else:
                return None
        except Exception as e:
            logpathfron.error(e)

           





      

    def orderBook(self):
        param= dict()
    
        ret= requests.post(self.baseurl+"rest/book/v2/getorderbook",data=param,header=self.headers)
        ret= ret.json()
    

        return ret
    
  


    def getposition (self):
        try:
        
      
            Authorization= self.gettoken()
            self.headers['Authorization'] = Authorization['Token']

            findata= dict()
            listfin=[]
            ret= requests.post(self.baseurl+"rest/book/v1/getposition",headers= self.headers)
            position =ret.json()
            print(position)
           
            if ret.status_code==200:
                position =ret.json()
                if position['status']=='SUCCESS':
                    if position['data'] is not None:

                        positionall= position['data']
                        for i in positionall:

                                
                            findata['exchange'] = i['exchange']
                            findata['tradingsymbol'] = i['symbol']
                            findata['symboltoken'] = i['symboltoken']
                            findata['buyavgprice'] = i['buyquantity']/i['buyamount']
                            findata['sellavgprice'] =  i['sellquantity']/i['sellamount']
                            findata['netqty'] = i['buyquantity']-i['sellquantity']
                            findata['ltp'] = i['LTP']
                            findata['unrealised'] = i['marktomarket']
                            findata['realised'] = i['bookedprofitloss']
                            listfin.append(findata)
                            findata={}

                    
                        return listfin ,None
                    else:
                        return None,'Not found'
                else:
                    return None,'Not found'


        except Exception as e:
            print(e)
            return None,e

    
    def allholding (self):
        try:
            Authorization= self.gettoken()
            self.headers['Authorization'] = Authorization['Token']

            ret= requests.post(self.baseurl+"rest/report/v1/getdpholding",headers= self.headers)
            findata= dict()
            listfin=[]
            if ret.status_code==200:
                position =ret.json()

                print(position)
                if position['status']=='SUCCESS':
                    positionall= position['data']
                    if positionall is not None:
                        for i in positionall:
                                
                            findata['tradingsymbol'] = i['scripname']
                            findata['symboltoken'] = i['nsesymboltoken']
                            findata['quantity'] = i['dpquantity']
                            findata['averageprice'] = i['buyavgprice']


                            listfin.append(findata)
                            findata={}

                    
                        return listfin ,None
                    else:
                        return None,'Not found'

                else:
                    return None,'Not found'


        except Exception as e:
            print(e)
            return None,e



    def checkfunds (self):
        try:
            Authorization= self.gettoken()
            self.headers['Authorization'] = Authorization['Token']

       
            ret= requests.post(self.baseurl+"rest/report/v1/getreportmarginsummary",headers=self.headers)
            if ret.status_code==200:
                cash =ret.json()
                
                return cash['data'] ,None
            
          

        except Exception as e:
            print(e)
            return None,e



   


    

class WebSocketConnect(motilalsetup):
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
    def Broadcast_on_open(ws1):
        # print("########Broadcast_Opened########")
        # print("AuthValidate after connection opened")

        # Exchange -BSE, NSE, NSEFO, MCX, NSECD, NCDEX
        # Exchange Type- CASH,DERIVATIVES   Scrip Code-eg 532540

        self.subscribetoken()
        self.unsubscribetoken()
        # Mofsl.UnRegister("BSE", "CASH", 532540)


        # Index BSE, NSE
        # Mofsl.IndexRegister("NSE")
        # Mofsl.IndexRegister("BSE")

        # Mofsl.IndexUnregister("NSE")
        # Mofsl.IndexUnregister("BSE")

        # Broadcast Logout
        # Mofsl.Broadcast_Logout()


    def Broadcast_on_message(self,ws1, message_type, message):
        
        print(message)
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
            

        

    
    def Broadcast_on_close(self,ws1, close_status_code, close_msg):
        # print("########Broadcast_closed########")
        # print("Broadcast Connection Closed")
        print("Close Message : %s" %(close_msg))
        print("Close Message Code : %s" %(close_status_code)) 
        




    def newevent(self):
        obj = md.watchlist.objects.filter(newevent=True,broker='MOTILAL').last()
        if obj:
            return obj,obj.newevent
        else:
            return obj, False

    def unsubscribetoken(self):
            try:

                obj = md.watchlist.objects.filter(subscribe=False,broker='MOTILAL')
                tokenlist=[]
                for  i in obj:
                        tlist= f"{i.exchange}|{i.symboltoken}"
                        if i.exchange=='NSEFO':
                            exc= "NSE"
                            tYPES='DERIVATIVE'
                            self.Mofsl.UnRegister(exc,tYPES, int(i.symboltoken))

                        if i.exchange=='BSEFO':
                            exc= "BSE"
                            tYPES='DERIVATIVE'
                            self.Mofsl.UnRegister(exc,tYPES, int(i.symboltoken))

                        if i.exchange=='NSE':
                            exc= "NSE"
                            tYPES='CASH'
                            self.Mofsl.UnRegister(exc,tYPES, int(i.symboltoken))

                        if i.exchange=='BSE':
                            exc= "BSE"
                            tYPES='CASH'
                            self.Mofsl.UnRegister(exc,tYPES, int(i.symboltoken))
                        i.delete()
                        tokenlist.append(tlist)
                return tokenlist
            except Exception as e :
                print(e)
    def subscribetoken(self):
            try:

                obj = md.watchlist.objects.filter(subscribe=True,broker='MOTILAL')
                tokenlist=[]
                for  i in obj:
                        tlist= f"{i.exchange}|{i.symboltoken}"
                        if i.exchange=='NSEFO':
                            exc= "NSE"
                            tYPES='DERIVATIVE'
                            self.Mofsl.Register(exc,tYPES, int(i.symboltoken))

                        if i.exchange=='BSEFO':
                            exc= "BSE"
                            tYPES='DERIVATIVE'
                            self.Mofsl.Register(exc,tYPES, int(i.symboltoken))

                        if i.exchange=='NSE':
                            exc= "NSE"
                            tYPES='CASH'
                            self.Mofsl.Register(exc,tYPES, int(i.symboltoken))

                        if i.exchange=='BSE':
                            exc= "BSE"
                            tYPES='CASH'
                            self.Mofsl.Register(exc,tYPES, int(i.symboltoken))


                return tokenlist
            except Exception as e :
                print(e)


    
    async def start_thread(self):
        self.Mofsl._Broadcast_on_open = Broadcast_on_open
        self.Mofsl._Broadcast_on_message = Broadcast_on_message
        self.Mofsl._Broadcast_on_close = Broadcast_on_close
        self.Mofsl.Broadcast_connect()


        
        while True:

            pass
        













 