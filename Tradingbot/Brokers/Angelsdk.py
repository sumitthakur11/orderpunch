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


path = pathlib.Path(__file__).resolve().parent.parent.parent
logpath= os.path.join(path,'Botlogs/Angelbroker.logs')
logpath= os.path.normpath(logpath)



print(logpath,'logpath')
logger=env.setup_logger(logpath)

logger1path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpath1= os.path.normpath(logger1path)
logpath1=env.setup_logger(logpath1)

def searchscrip (Symbol,exchange,instrument):
        try:

            data = requests.get('https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json',timeout=3)
            if data.status_code == 200:
                db = pd.DataFrame(data.json())
            else:
                print(f"Failed to download the file. Status code: {data.status_code}")
            logpath= os.path.join(path,'data/NFO.csv')
            logpath= os.path.normpath(logpath)
            if  Symbol and instrument and exchange:
                if exchange=='NSE' or exchange=='BSE':

                    db =db[db['exch_seg']==exchange]
                    
                    db =db[db['name']==Symbol]

                else:
                    db =db[db['instrumenttype']==instrument]
                # db =db[db['exch_seg']==exchange]
                    db =db[db['name']==Symbol]
            else:
                db =db[db['exch_seg']==exchange]
            db=db.rename(columns={'symbol':'TradingSymbol'})

            logger.info("function called searchscrip")
            
            return db
        except Exception as err:
            logger.error(err)
            raise err

savepath= os.path.join(path,"angel.json")
savepath= os.path.normpath(savepath)
submitdata=[]
tokenltp=0
filtered_data = []

class Ltp:
    def __init__(self,data,totaltoken) :
        
        try:
            global findata
            global tokenltp
            global submitdata
            global filtered_data
            findata= dict()
            self.data= {}
            # print(data)
            obj = md.watchlist.objects.filter(broker='ANGEL',symboltoken=data['token']).last()
            obj.ltp= int(data['last_traded_price'])/100
            obj.volume= data['volume_trade_for_the_day']  if 'volume_trade_for_the_day' in data.keys() else 0
            obj.save()
            # if obj.symboltoken not in filtered_data:
            #     filtered_data.append(data['token'])

            #     self.data['LTP'] =int(data['last_traded_price'])/100 
            #     if data['exchange_type']==1:
            #         self.data['exchange']= 'NSE'
            #     elif data['exchange_type']==2:
            #         self.data['exchange']= 'NFO'
            #     elif data['exchange_type']==3:
            #         self.data['exchange']= 'BSE'
            #     elif data['exchange_type']==4:
            #         self.data['exchange']= 'BFO'
            #     self.data['token']= data['token']
            #     self.data['volume']= data['volume_trade_for_the_day']  if 'volume_trade_for_the_day' in data.keys() else 0
            #     self.data['Lotsize']= obj.lotsize
            #     self.data['Tradingsymbol']= obj.tradingsymbol 
            #     self.data['broker']='ANGEL'
            #     submitdata.append(self.data)



            
            # tokenltp=data['token']
            
            

            # if len(submitdata)>=totaltoken:
            #     print(submitdata)

            #     file= open(savepath,'w')

            #     datasub = json.dump(submitdata,file)
            #     submitdata=[]
            #     filtered_data=[]
            #     file.close()
            


        
                        
                
        
            
        except KeyError as e :
            print(e)
            pass



        
    def save_depth_data(self, symbol, depth_data,rawpath):
        """Save depth data to file"""
        try:
            file_exists = os.path.exists(rawpath)
            
            if not file_exists:
                with open(rawpath, 'a') as f:
                    
                    f.write('[')
                    json_data = depth_data.copy()
                    
                    f.write(json.dumps(json_data))
                    f.write(']')
            
            else:
                with open(rawpath, 'r+') as f:
                    
                    f.seek(0, os.SEEK_END)
                    f.seek(f.tell() - 1, os.SEEK_SET)
                    print(rawpath)
                    if f.read(1) == ']':
                        f.seek(f.tell() - 1, os.SEEK_SET)
                        f.truncate()
                        f.write(',')
                    else:
                        f.write('[')

                    json_data = depth_data.copy()
                    
                    f.write(json.dumps(json_data))
                    f.write(']')
            
            logger.info(f"Saved depth data for {symbol} to {rawpath}")
            return True
        except Exception as e:
            logger.error(f"Error saving depth data for {symbol}: {str(e)}",exc_info=True)
            return False

        


class order:
    def __init__(self,data) :
        self.data= {}
        self.finaldata= []
        for i in range(len(data)):
                self.data['qty']=i['qty']
                self.data['prc']= i['prc']
                self.data['trgprc']= i['trgprc']
                self.data['rpt']= i['rpt']
                self.finaldata.append(self.data)
        print(self.finaldata)


class SMARTAPI(object) :
    
    def __init__(self, username = '',pwd = '',api_key ='',token=""):
       

        
        self.api= api_key
        self.username=username
        self.pwd = str(pwd)
        self.token =token  
        self.orderid = None
        self.authToken= None
        self.refreshToken= None
        self.feedToken = None
        self.smartApi = smartConnect.SmartConnect(self.api)
        self.decimals = 10**6
        
   
    
        
    def smartAPI_Login(self):
        try:

            res= None
            try:
                totp = pyotp.TOTP(self.token).now()
            except Exception as e:
                logger.error(f"Invalid Token: The provided token is not valid or {e}") 
                raise e


            data = self.smartApi.generateSession(self.username, self.pwd, totp)
        

            if not data['status']:
                logger.error(data)
                logpath1.error(data)

            else:
                tokendict={}
                tokendict['authToken'] = data['data']['jwtToken']
                tokendict['refreshToken'] = data['data']['refreshToken']
                print(tokendict['refreshToken'],'===================================================')
                tokendict['feedToken'] = self.smartApi.getfeedToken()
                self.smartApi.generateToken(tokendict['refreshToken'])
                res = self.smartApi.getProfile(tokendict['refreshToken'])
                res = res['data']['exchanges']
                filepath= os.path.join(path,f'Angellogin/{self.username}.json')
                filepath= os.path.normpath(filepath)

                print(filepath)
                
                out=open(filepath, 'w')
                json.dump(tokendict,out,indent=6)
                logpath1.info('Angel Login successful')
                # out.close()
                return True , None
        except Exception as e :
            logpath1.error(e)
            return False,e

            
    def get_angel_client(self):
        try:
            print(self.username)
            filepath= os.path.join(path,f'Angellogin/{self.username}.json')
            filepath= os.path.normpath(filepath)

            with open(filepath, 'rb') as f:
                loaded_dict = json.load(f)
                print(loaded_dict,'loadeddict')
            return loaded_dict
        except Exception as e :
            logpath1.error('Try login Again')

            print(e)
    
        
    
    

class HTTP(SMARTAPI):
    def __init__(self,username = '',pwd = '',api_key ='',token=""):
        super().__init__(username ,pwd,api_key,token)
        self.smartApi=self.client_()
    
    

    def client_(self):
        self.client= self.get_angel_client()
        token=self.client['authToken'].split(' ')[1]
        self.smartApi = smartConnect.SmartConnect(self.api,access_token=token)

        return self.smartApi
    
    


    def checkfunds(self):
        try :
            data= self.smartApi.rmsLimit()
            print(data)
            if data['success']:
                return data['data'],None
            else:
                 return None,data
        
        except Exception as e:
            return None, e


    
    def optionchain(self,orderparam):
        print(orderparam['symbol'],''.join(orderparam['expiry']))
        expiry=(''.join(orderparam['expiry'])).upper().strip()
        payload =  {
        "name":orderparam['symbol'],    
        "expirydate":expiry
        }   

        data= self.smartApi.optionGreek(payload)
        data= pd.DataFrame(data['data'])
        data =data.sort_values(by=['tradeVolume','impliedVolatility'],key=lambda col: col.astype(float),ascending=False)
        
        print(data)

        return data

        
        
    #   

    
    def candels(self,exchange,symboltoken,interval):
        print(exchange,symboltoken,interval)
        todate= datetime.datetime.today().astimezone(pytz.timezone('Asia/Kolkata'))
        fromdate=todate- datetime.timedelta(days=100)
        todate= todate.strftime("%Y-%m-%d %H:%M")
        fromdate= fromdate.strftime("%Y-%m-%d %H:%M")

        candleParams={  
        "exchange": exchange,
        "symboltoken": symboltoken,
        "interval": interval,
        "fromdate":fromdate ,
        "todate": todate
        }
        candledetails= self.smartApi.getCandleData(candleParams)
        columns= ['updated_at', 'open', 'high', 'low', 'Close', 'Volume']
        candledetails= pd.DataFrame(candledetails['data'],columns=columns)
        candledetails['OI']=0

        return candledetails
                
    
    def get_quotes(self,exchangeTokens):
        mode= 'FULL'    
        
        
        data =self.smartApi.getMarketData(mode,exchangeTokens)
        
        return data
                

    def getposition(self):
        try:

            data = self.smartApi.position()
            print(data)
            return data['data'], None
        except Exception as e:
            return None,e

    
    def allholding(self):
        try:

            data = self.smartApi.allholding()
            return data['data'], None
        except Exception as e:
            return None,e









    def cancel_order(self, orderid):
        data = self.smartApi.cancelOrder(orderid, "NORMAL")
        return data
    
    

    
    def uniqueno(self):
        # import uuid
        return int(time.time()*1000)
    def closetrade(self, orderparam,PAPER):
        
        if not PAPER:

                orderparams1 = {
                        "variety": "NORMAL",
                        "tradingsymbol": orderparam['tradingsymbol'],
                        "symboltoken":str(orderparam['Token']),
                        "transactiontype": orderparam['Transactiontype'],
                        "exchange": orderparam['exchange'],
                        "ordertype": orderparam['order_type'],
                        "producttype": orderparam['product_type'],
                        "duration": "DAY",
                        "price": orderparam['price'],
                        'triggerprice':orderparam['price'],
                        "squareoff": "0",
                        "stoploss": "0",
                        "quantity": orderparam['quantity']}

                orderid = self.smartApi.placeOrder(orderparams1) 
        else:
                orderid  =self.uniqueno()
        

        return   orderid
    
    
    def placeorder(self, orderparam,orderobject,STOPLOSS,PAPER):
        try:

            
            print(orderparam)
            quantity=orderparam['quantity']

            orderid= None
            orderupdate= orderobject
          

            orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": orderparam['tradingsymbol'],
            "symboltoken":str(int(orderparam['symboltoken'])),
            "transactiontype": orderparam['transactiontype'],
            "exchange": orderparam['exchange'],
            "ordertype": orderparam['ordertype'],
            "producttype": orderparam['product_type'],
            "duration": "DAY",
            "price": float(orderparam['ltp']),
            "squareoff": "0",
            "stoploss": "0",
            "quantity": int(quantity),
            "disclosedquantity": int(orderparam['discloseqty'])
            
            }
            if not PAPER:
                orderid = self.smartApi.placeOrder(orderparams)
                print(orderid)
                

                if orderid:
                    
                    status = self.smartApi.orderBook()
                    status = pd.DataFrame(status['data'])
                    print(status)
                    status= status[status['orderid']==str(orderid)]
                    orderparam['orderid']=orderid
                    orderparam['orderstatus']= status['orderstatus'].iloc[-1].upper()
                    orderparam['status']=True if status['orderstatus'].iloc[-1].upper()=='COMPLETE' else False
                    orderparam['user']=1
                    orderparam['broker']='ANGEL'
                    orderparam['avg_price']=status['price'].iloc[-1]
                    orderobject(orderparam)
                    logpath1.info(f'Broker Angel order palced,orderid:{orderid}')
                


            return   orderid
        except Exception as e:
            logger.error(e,exc_info=True)
            logpath1.error(e)
            orderobject(orderparam)


    
    
    
    def gainersLosers(self,typedata):
        params= {
            "datatype":typedata, # Type of Data you want(PercOILosers/PercOIGainers/PercPriceGainers/PercPriceLosers)
            "expirytype":"NEAR" #Expiry Type (NEAR/NEXT/FAR)
            }
        data = self.smartApi.gainersLosers(params)
        logger.info(f"Order Book: {data}")
        return data

    def orderBook(self):


        data = self.smartApi.orderBook()
        if data['data']:
         return data['data']
        else:
            return None
    def modifyorder(self,data,orderobject):
        try:

            orderparams = {
            "variety": "NORMAL",
            "orderid": orderobject.orderid,
            "price":data['ltp'],
            "producttype":data['product_type'],
            "ordertype":data['ordertype'],
            "tradingsymbol":orderobject.tradingsymbol,
            "quantity":str(data['quantity']),
            "symboltoken":orderobject.symboltoken,

            }
            orderiddta = self.smartApi.modifyOrder(orderparams)
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
class WebSocketConnect(SMARTAPI):
    def __init__(self,username = '',pwd = '',api_key ='',token=""):
        super().__init__(username,pwd,api_key ,token)
        
        NIFTY= '26000'
        BANKNIFTY= 26009
        FINNIFTY = ''
        MIDCAP= 26014
        self.objlen= 0


    def newevent(self):
        obj = md.watchlist.objects.filter(newevent=True,broker='ANGEL').last()
        if obj:
            return obj,obj.newevent
        else:
            return obj, False

    def unsubscribetoken(self):
            try:
                TOKENS = {"exchangeType":1,"tokens":[],'action':0}

                obj = md.watchlist.objects.filter(subscribe=False,broker='ANGEL')
                tokenlist=[]
                for  i in obj:
                        

                        if i.exchange=='NSE':
                            TOKENS['exchangeType']=1
                            TOKENS['tokens'].append(i.symboltoken)
                        elif i.exchange=='NFO':
                            TOKENS['exchangeType']=2

                           
                            TOKENS['tokens'].append(i.symboltoken)

                             
                        elif i.exchange=='BSE':
                            TOKENS['exchangeType']=3
                           
                            TOKENS['tokens'].append(i.symboltoken)

                             
                        elif i.exchange=='BFO':
                            TOKENS['exchangeType']=4
                        
                            TOKENS['tokens'].append(i.symboltoken)
                          
                        elif i.exchange=='MCX':
                            TOKENS['exchangeType']=5
                          
                            TOKENS['tokens'].append(i.symboltoken)
                        
                        tokenlist.append(TOKENS)
                return tokenlist

            except Exception as e :
                print(e)
    def subscribetoken(self):
            """
            exchange type and their code
            1 (nse_cm)
            2 (nse_fo)
            3 (bse_cm)
            4 (bse_fo)
            5 (mcx_fo)
            7 (ncx_fo)
            13 (cde_fo)
            """
            
            try:
                tokend= 0
                
                obj = md.watchlist.objects.filter(subscribe=True,broker='ANGEL')
                tokenlist=[]
                self.objlen= len(set(obj))
                TOKENS = {"exchangeType":1,"tokens":[]}
                TOKENS1 = {"exchangeType":1,"tokens":[]}
                TOKENS2 = {"exchangeType":1,"tokens":[]}
                TOKENS3 = {"exchangeType":1,"tokens":[]}
                TOKENS4 = {"exchangeType":1,"tokens":[]}


                
                
                for  i in obj:
                        print(i.symboltoken)
                    
                        if i.exchange=='NSE':
                            TOKENS['exchangeType']=1
                            TOKENS['tokens'].append(i.symboltoken)
                            TOKENS['tokens']= list(set(TOKENS['tokens']))
                            tokenlist.append(TOKENS)

                        elif i.exchange=='NFO':
                            TOKENS1['exchangeType']=2
                           
                            TOKENS1['tokens'].append(i.symboltoken)
                            TOKENS1['tokens']= list(set(TOKENS1['tokens']))
                            tokenlist.append(TOKENS1)



                             
                        elif i.exchange=='BSE':
                            TOKENS2['exchangeType']=3
                           
                            TOKENS2['tokens'].append(i.symboltoken)
                            TOKENS2['tokens']= list(set(TOKENS2['tokens']))
                            tokenlist.append(TOKENS2)
    


                             
                        elif i.exchange=='BFO':
                            TOKENS3['exchangeType']=4
                        
                            TOKENS3['tokens'].append(i.symboltoken)
                            TOKENS3['tokens']= list(set(TOKENS3['tokens']))
                            tokenlist.append(TOKENS3)


                          
                        elif i.exchange=='MCX':
                            TOKENS['exchangeType']=5
                          
                            TOKENS['tokens'].append(i.symboltoken)
                            TOKENS['tokens']= list(set(TOKENS['tokens']))
                        tokend= i.symboltoken
                        # TOKENS['exchangeType']=0
                        # TOKENS['tokens']=[]




                        
                return tokenlist
            except Exception as e :
                print(e)
                logger1path.error(e)

    

        

        
    def start_thread(self):


        token = self.get_angel_client()
        authToken= token['authToken'].split(' ')[1]
        feedToken=token['feedToken']
        self.sws = smartWebSocketV2.SmartWebSocketV2(authToken, self.api, self.username, feedToken,
                                    max_retry_attempt=2, retry_strategy=0, retry_delay=10, retry_duration=30)



        self.correlation_id = "abcde"   
        self.mode =3

        self.token_list=self.subscribetoken()
        print(self.token_list)

        # Callback for tick reception.
        def close_connection(self):
            self.sws.close_connection()

        def on_data(wsapp, message):
            logger.info("Ticks: {}".format(message))
            Ltp(message,self.objlen)

            objnew,newevent= self.newevent()
            if newevent:
                tokelistunsb= self.unsubscribetoken()
                tokelistsubs= self.subscribetoken()
                if len(tokelistunsb)>0:
                        self.sws.unsubscribe(self.correlation_id, self.mode, tokelistsubs)
                if len(tokelistsubs)>0:
                    self.sws.subscribe(self.correlation_id, self.mode, tokelistunsb)
                objnew.newevent= False
                objnew.save()
            
          
            # print(message)
            # close_connection()


        def on_open(wsapp):
            logger.info("on open")
            print('open...')
            some_error_condition = False
            if some_error_condition:
                error_message = "Simulated error"
                if hasattr(wsapp, 'on_error'):
                    wsapp.on_error("Custom Error Type", error_message)
            else:
                self.sws.subscribe(self.correlation_id, self.mode, self.token_list)
        # Callback when current connection is closed.
        def on_close(wsapp):
           logger.info("Close")


        # Callback when connection closed with error.
        def on_error(wsapp, error):
            logger.error(error)
        # Callback when all reconnect failed (exhausted max retries)
        def on_control_message(wsapp, message):
            logger.info(f"Control Message: {message}")
        # Assign the callbacks.
        self.sws.on_data = on_data
        self.sws.on_open = on_open
        self.sws.on_close = on_close
        self.sws.on_error = on_error
        self.sws.on_control_message = on_control_message

        self.sws.connect()


