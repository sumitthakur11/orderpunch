import Tradingbot.models as md 
import Tradingbot.serializers as ser 
from .Brokers import shoonyasdk,Angelsdk,motilalsdk,growwsdk,dhansdk,flattradesdk,stoxkartsdk
from concurrent.futures import ThreadPoolExecutor
import pathlib 
import os
import json
import asyncio
path = pathlib.Path(__file__).parent.parent
from Tradingbot import env


import time
import platform
print(platform.version())

logger2path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpathfron= os.path.normpath(logger2path)
logpathfron=env.setup_logger(logpathfron)


stoxkartsdk.searchscrip('','NSE','EQ')


class utility:
        def __init__(self,USER):
             self.user= USER
             
        def orderobject(self,data):
            print(data)
            serialize = ser.orderobject(data=data)
            if serialize.is_valid(raise_exception=True):
                        serialize.save()
        



        def brokerobj(self,broker):
            self.broker= None
            if broker =='SHOONYA':
                  self.broker = shoonyasdk.HTTP()

            return self.broker

        def loginbroker(self,data):
            br= md.Broker.objects.filter(brokerid=data['brokerid']).last()
            if br.brokername.lower()=='shoonya':
                bruser= br.accountnumber
                pwd= br.password
                vendorcode=br.vendorcode
                apikey= br.apikey
                imei= br.imei
                token= br.AuthToken

                self.broker = shoonyasdk.shoonyasetup(bruser,pwd,vendorcode,apikey,imei,token)
                flag,excp= self.broker.login()
                if flag:
                     br.valid=True
                     br.save()
                else: 
                     br.valid=False
                     br.save()
                     
                     
                     
                     return excp

            elif br.brokername.lower()=='angel':
                bruser= br.accountnumber
                pwd= br.password
                apikey= br.apikey
                token= br.AuthToken

                self.broker = Angelsdk.SMARTAPI(bruser,pwd,apikey,token)
                flag,excp=self.broker.smartAPI_Login()
                if flag:
                     br.valid=True
                     br.save()
                else: 
                     br.valid=False
                     br.save()

                     
                     
                     return excp

        def checkfunds(self):
            accountlist= md.Broker.objects.filter(user=1,valid=True)
            for br in accountlist:
                if br.brokername.lower()=='shoonya':
                    print(br.brokername)
                    bruser= br.accountnumber
                    pwd= br.password
                    vendorcode=br.vendorcode
                    apikey= br.apikey
                    imei= br.imei
                    token= br.AuthToken

                    self.broker = shoonyasdk.HTTP(bruser,pwd,vendorcode,apikey,imei,token)
                    fund,excp= self.broker.checkfunds()
                    if fund:

                        br.funds=fund
                        br.valid=True

                        br.save()
                    else: 
                        br.funds="Unable to Fetch"
                        br.valid=False

                        br.save()
                        logpathfron.error(f'connect to administration with following error:-{excp}')
                        
                        
                        

                elif br.brokername.lower()=='angel':
                    bruser= br.accountnumber
                    pwd= br.password
                    apikey= br.apikey
                    token= br.AuthToken
                    print('eh')
                    self.broker = Angelsdk.HTTP(bruser,pwd,apikey,token)
                    fund,excp=self.broker.checkfunds()
                    print(fund)

                    if fund:
                        br.funds=fund['net']
                        br.valid= True
                        br.save()
                    else: 
                        br.funds="Unable to Fetch"
                        br.valid= False

                        br.save()
                        logpathfron.error(f'connect to administration with following error:-{excp}')

                        
                        
        def getposition(self):
            accountlist= md.Broker.objects.filter(user=1,valid=True)
            print(accountlist)
            for br in accountlist:
                if br.brokername.lower()=='shoonya':
                    bruser= br.accountnumber
                    pwd= br.password
                    vendorcode=br.vendorcode
                    apikey= br.apikey
                    imei= br.imei
                    token= br.AuthToken

                    self.broker = shoonyasdk.HTTP(bruser,pwd,vendorcode,apikey,imei,token)

                    fund,excp= self.broker.getposition()
                    if fund:
                        

                        md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                        for data in fund:
                            data['accountnumber']=br.accountnumber
                            data['user']=1
                            data['broker']='SHOONYA'
                            data['nickname']=br.nickname

                            serialize = ser.Allpositions(data=data)
                            if serialize.is_valid(raise_exception=True):
                                serialize.save()


                        pass
                    else:
                        pass
                       
                        logpathfron.error(f'connect to administration with following error:-{excp}')
                        
                        
                        

                elif br.brokername.lower()=='angel':
                    print('here')
                    bruser= br.accountnumber
                    pwd= br.password    
                    apikey= br.apikey
                    token= br.AuthToken

                    self.broker = Angelsdk.HTTP(bruser,pwd,apikey,token)
                    fund,excp=self.broker.getposition()
                    time.sleep(0.5)
                    if fund:

                        for data in fund:
                            md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                            data['accountnumber']=br.accountnumber
                            data['user']=1
                            data['broker']='ANGEL'
                            data['nickname']=br.nickname
                            
                            serialize = ser.Allpositions(data=data)
                            if serialize.is_valid(raise_exception=True):
                                serialize.save()
                       
                    else: 
                        logpathfron.error(f'connect to administration with following error:-{excp}')

                        
                        




        

        def getholding(self):
            accountlist= md.Broker.objects.filter(user=1,valid=True)
            for br in accountlist:
                if br.brokername.lower()=='shoonya':
                    bruser= br.accountnumber
                    pwd= br.password
                    vendorcode=br.vendorcode
                    apikey= br.apikey
                    imei= br.imei
                    token= br.AuthToken

                    self.broker = shoonyasdk.HTTP(bruser,pwd,vendorcode,apikey,imei,token)
                    md.allholding.objects.filter(accountnumber=br.accountnumber).delete()

                    fund,excp= self.broker.allholding()
                    if fund:
                        md.allholding.objects.filter(accountnumber=br.accountnumber).delete()

                        for data in fund:

                            
                            data=data['holdings']
                        

                            serialize = ser.allholding(data=data)
                            if serialize.is_valid(raise_exception=True):
                                serialize.save()


                        pass
                    else:
                        pass
                       
                        logpathfron.error(f'connect to administration with following error:-{excp}')
                        
                        
                        

                elif br.brokername.lower()=='angel':
                    print('here')
                    bruser= br.accountnumber
                    pwd= br.password
                    apikey= br.apikey
                    token= br.AuthToken

                    self.broker = Angelsdk.HTTP(bruser,pwd,apikey,token)
                    fund,excp=self.broker.allholding()
                    time.sleep(0.5)
                    if fund:
                        md.allholding.objects.filter(accountnumber=br.accountnumber).delete()
                        for data in fund['holdings']:

                            data['user']= 1
                            data['broker']= br.brokername
                            data['accountnumber']=br.accountnumber
                            data['nickname']= br.nickname


                            data['totalprofitandloss']=fund['totalholding']['totalprofitandloss']
                            data['totalpnlpercentage']=fund['totalholding']['totalpnlpercentage']

                            serialize = ser.allholding(data=data)
                            if serialize.is_valid(raise_exception=True):
                                serialize.save()

                       
                    else: 
                        logpathfron.error(f'connect to administration with following error:-{excp}')

                        
                        

        







        def logoutbroker(self,data):

            if data['broker'].lower()=='shoonya':
                   self.broker = shoonyasdk.shoonyasetup()
                   self.broker.logout()


        def cancel_order(self,orderid):
            try:
                print(orderid)
                for i in orderid:

                    orderobj = md.orderobject.objects.filter(id=i).last()
                    br=md.Broker.objects.filter(accountnumber=orderobj.accountnumber).last()
                    if br.valid:
                            bruser= br.accountnumber
                            pwd= br.password
                            vendorcode=br.vendorcode
                            apikey= br.apikey
                            imei= br.imei
                            token= br.AuthToken
                            if br.brokername=='SHOONYA':
                                self.broker = shoonyasdk.HTTP(token=token,
                                                    user=bruser, 
                                                    pwd=pwd, 
                                                    vendorcode= vendorcode,
                                                    app_key=apikey, 
                                                    imei=imei)
                                order_ids=self.broker.cancel_order(orderobj.orderid)
                        
                            if br.brokername=='ANGEL':
                            

                                
                                Angel = Angelsdk.HTTP(token=token,
                                                    username=bruser, 
                                                    pwd=pwd, 
                                                    api_key=apikey, )
                                order_ids=Angel.cancel_order(orderobj.orderid)
                            return order_ids

                                

                    else:
                            
                            msg=f"Account Number {br.accountnumber} Nickname {br.nickname} is not logged in. Kindly Logged in to the Account"
                            logpathfron.error(msg)

        
            
                        
            except Exception as e:
                print(str(e))
                logpathfron.error(f'Contact to administrator with following error:{e}')

                return str(e)

        def asignorderstatus(self,orderbook,broker):
            if broker == 'SHOONYA':

                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['norenordno']).last()
                    if order:
                        order.orderstatus= i['status'].upper()
                        order.avg_price=i['avgprc']
                        order.save()
                    
            if broker =='ANGEL':
                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['orderid']).last()
                    if order:
                        order.orderstatus= i['status'].upper()
                        order.avg_price=i['averageprice']
                        order.save()





              
        def orderstatus(self):
            try:

                    account=md.Broker.objects.filter(valid=True)


                    for br in account:

                        if br.valid:
                            bruser= br.accountnumber
                            pwd= br.password
                            vendorcode=br.vendorcode
                            apikey= br.apikey
                            imei= br.imei
                            token= br.AuthToken
                            if br.brokername=='SHOONYA':
                                        self.broker = shoonyasdk.HTTP(token=token,
                                                            user=bruser, 
                                                            pwd=pwd, 
                                                            vendorcode= vendorcode,
                                                            app_key=apikey, 
                                                            imei=imei)
                                        order_ids=self.broker.orderBook()
                                        self.asignorderstatus(order_ids,'SHOONYA')
                            if br.brokername=='ANGEL':
                                    

                                        
                                        Angel = Angelsdk.HTTP(token=token,
                                                            username=bruser, 
                                                            pwd=pwd, 
                                                            api_key=apikey, )
                                        order_ids=Angel.orderBook()
                                        self.asignorderstatus(order_ids,'ANGEL')

                            return order_ids

                                

                    else:
                            
                            msg=f"Account Number {br.accountnumber} Nickname {br.nickname} is not logged in. Kindly Logged in to the Account"
                            logpathfron.error(msg)

        
            
                        
            except Exception as e:
                print(str(e))
                logpathfron.error(f'Contact to administrator with following error:{e}')

                return str(e)


        def modifyorder(self,data):
            try:
                orderobj = md.orderobject.objects.filter(orderid=data['orderid']).last()
                br=md.Broker.objects.filter(accountnumber=orderobj.accountnumber).last()
                if br.valid:
                        bruser= br.accountnumber
                        pwd= br.password
                        vendorcode=br.vendorcode
                        apikey= br.apikey
                        imei= br.imei
                        token= br.AuthToken
                        if br.brokername=='SHOONYA':
                            self.broker = shoonyasdk.HTTP(token=token,
                                                user=bruser, 
                                                pwd=pwd, 
                                                vendorcode= vendorcode,
                                                app_key=apikey, 
                                                imei=imei)
                            order_ids=self.broker.modifyorder(data,orderobj)
                    
                        if br.brokername=='ANGEL':
                           

                            
                            Angel = Angelsdk.HTTP(token=token,
                                                username=bruser, 
                                                pwd=pwd, 
                                                api_key=apikey, )
                            order_ids=Angel.modifyorder(data,orderobj)
                        return order_ids

                            

                else:
                        
                        msg=f"Account Number {br.accountnumber} Nickname {br.nickname} is not logged in. Kindly Logged in to the Account"
                        logpathfron.error(msg)

                            
            
                        
            except Exception as e:
                print(str(e))
                logpathfron.error(f'Contact to administrator with following error:{e}')

                return str(e)
              

        def placeorder(self,orderparams,batmcal=60,subclients=0,STOPLOSS=True,PAPER=True,makesymbol=True,advicecheck=''):
            try:

                
                orderid=  []
                placeorders=False
                quantity=orderparams['quantity']

                
                
                if orderparams['account']:
                    for i in orderparams['account']:
                        orderparams['accountnumber']=i
                        orderparams['user']=1


                        
                        br=md.Broker.objects.filter(accountnumber=i).last()
                        if br.valid:
                            orderparams['broker']=br.brokername
                            orderparams['nickname']=br.nickname


                            bruser= br.accountnumber
                            pwd= br.password
                            vendorcode=br.vendorcode
                            apikey= br.apikey
                            imei= br.imei
                            token= br.AuthToken
                            if br.brokername=='SHOONYA':
                                self.broker = shoonyasdk.HTTP(token=token,
                                                    user=bruser, 
                                                    pwd=pwd, 
                                                    vendorcode= vendorcode,
                                                    app_key=apikey, 
                                                    imei=imei)
                                order_ids=self.broker.placeorder(orderparams,self.orderobject,False,False)
                        
                            if br.brokername=='ANGEL':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname

                                
                                Angel = Angelsdk.HTTP(token=token,
                                                    username=bruser, 
                                                    pwd=pwd, 
                                                    api_key=apikey, )
                                order_ids=Angel.placeorder(orderparams,self.orderobject,False,False)

                        else:
                            
                            msg=f"Account Number {br.accountnumber} Nickname {br.nickname} is not logged in. Kindly Logged in to the Account"
                            logpathfron.error(msg)

                              
                
                return order_ids
                        
            except Exception as e:
                print(str(e))
                logpathfron.error(f'Contact to administrator with following error:{e}')

                return str(e)


        def loginshoonya(self):
            obj2= md.Broker.objects.filter(brokername='SHOONYA').last()
            bruser= obj2.accountnumber
            pwd= obj2.password
            vendorcode=obj2.vendorcode
            apikey= obj2.apikey
            imei= obj2.imei
            token= obj2.AuthToken


            self.broker = shoonyasdk.HTTP(token=token,
                                            user=bruser, 
                                            pwd=pwd, 
                                            vendorcode= vendorcode,
                                            app_key=apikey, 
                                            imei=imei)

            return self.broker



        def addsymbol(self,symda):
            data =dict()
            a, b = symda[0],symda[1]
            print(a,b)
            data['user']=1
            data['exchange']=b
            data['orderpunchsymbol']=a
            serialize = ser.globalsymbol(data=data)
            if serialize.is_valid(raise_exception=True):
                        serialize.save()
                 

        def writesubscriptions(self):
            obj = md.watchlist.objects.filter().values()
            print(obj)
            data = dict()
            data1=[]
        
       

            for i in range(len(obj)):
                file1 = os.path.join(path,f'{obj[i]['broker'].upper()}.json')
            
                if not obj[i]['symboltoken'] in data.values():
                    data['token']=obj[i]['symboltoken']
                    data['tradingsymbol']=obj[i]['tradingsymbol']
                    data['subscribe']=obj[i]['tradingsymbol']

                    self.save_depth_data(data,file1)
              
                        
                  
        def save_depth_data(self, depth_data,rawpath):
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
                        if f.read(1) == ']':
                            f.seek(f.tell() - 1, os.SEEK_SET)
                            f.truncate()
                            f.write(',')
                        else:
                            f.write('[')

                        json_data = depth_data.copy()
                        
                        f.write(json.dumps(json_data))
                        f.write(']')
                
                # logger.info(f"Saved depth data for {symbol} to {rawpath}")
                return True
            except Exception as e:
                # logger.error(f"Error saving depth data for {symbol}: {str(e)}",exc_info=True)
                return False

        def shoonyawebsocket(self):
            obj = md.watchlist.objects.filter(broker='SHOONYA',subscribe= True)
            tokenlist=[]
            for  i in obj:
                
                    tlist= f"{i.exchange}|{i.symboltoken}"
                    tokenlist.append(tlist)
                    i.newevent=False
                    i.save()
                
            broker= md.Broker.objects.filter(brokername='SHOONYA').last()
            autoken= broker.AuthToken
            accountno= broker.accountnumber
            passwrd= broker.password
            apikey= broker.apikey
            imei= "abc1234"
            vendorcode= broker.vendorcode
            webobj= shoonyasdk.WebSocketConnect(accountno,passwrd,vendorcode,apikey,imei,autoken,tokenlist)
            asyncio.run(webobj.start_thread())

                     
                  
        def angelwebsocket(self):
            obj = md.watchlist.objects.filter(broker='ANGEL',subscribe= True)
            broker= md.Broker.objects.filter(brokername='ANGEL').last()
            autoken= broker.AuthToken
            accountno= broker.accountnumber
            passwrd= broker.password
            apikey= broker.apikey
            imei= "abc1234"
            vendorcode= broker.vendorcode
            webobj= Angelsdk.WebSocketConnect(accountno,passwrd,apikey,autoken)
            asyncio.run(webobj.start_thread())
        

        def dhanwebsocket(self):
            obj = md.watchlist.objects.filter(broker='ANGEL',subscribe= True)
            broker= md.Broker.objects.filter(brokername='ANGEL').last()
            autoken= broker.AuthToken
            accountno= broker.accountnumber
            webobj= dhansdk.WebSocketConnect(accountno,autoken)
            asyncio.run(webobj.start_thread())
        



        def createOrderpunchsymbol(self):
            exchangelist=['NFO','NSE','BSE','BFO']
            data= dict()

            for i in exchangelist:
                allsym= shoonyasdk.optionchain('',i,'')
                allsym['Symbol']=allsym['Symbol'].str.upper()
                allsymb=sorted(set( allsym['Symbol'].str.replace(' ','').to_list()))
                allex=allsym['Exchange'].str.replace(' ','').to_list()
                zipped= list(zip(allsymb,allex))
                with ThreadPoolExecutor() as executor:
                    executor.map(self.addsymbol, zipped)

             
        
            return data
        

                 
                 
obj=utility(1)
# obj.checkfunds()
# obj.orderstatus()

# data =obj.createOrderpunchsymbol()

