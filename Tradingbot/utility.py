import Tradingbot.models as md 
import Tradingbot.serializers as ser 
from .Brokers import shoonyasdk,Angelsdk,motilalsdk,growwsdk,dhansdk,flattradesdk,stoxkartsdk,fyerssdk,upstoxsdk,Alicebluesdk,zerodhasdk,hdfcsdk,samcosdk
from concurrent.futures import ThreadPoolExecutor
import pathlib 
import os
import json
import asyncio
path = pathlib.Path(__file__).parent.parent
from Tradingbot import env

import threading
import time
import platform
print(platform.version())

logger2path= os.path.join(path,'Botlogs/Frontendlog.logs')
logpathfron= os.path.normpath(logger2path)
logpathfron=env.setup_logger(logpathfron)




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
            print(data['brokerid'])
            br= md.Broker.objects.filter(brokerid=data['brokerid']).last()
            print(br.brokername)
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


            elif br.brokername.lower()=='fyers':
                bruser= br.accountnumber
                secret_key= br.secretkey
                token= br.AuthToken

                self.fyers = fyerssdk.fyerssetup(bruser,secret_key,token)
                t = threading.Thread(target=self.fyers.login)
                t.start()   


            elif br.brokername.lower()=='motilal':
                bruser= br.accountnumber
                pwd= br.password
                apikey= br.apikey
                token= br.AuthToken
                self.motilal = motilalsdk.motilalsetup(bruser,pwd,apikey,token)
                flag,excp =self.motilal.login()
                if flag:
                     br.valid=True
                     br.save()
                else: 
                     br.valid=False
                     br.save()

                     
                     
                     return excp
            elif br.brokername.lower()=='upstox':
                bruser= br.accountnumber
                apikey= br.apikey
                token= br.AuthToken

                self.upstox = upstoxsdk.Upstoxapi(bruser,apikey)
                t = threading.Thread(target=self.upstox.login)
                t.start()   
            elif br.brokername.lower()=='aliceblue':
                bruser= br.accountnumber
                apikey= br.apikey
                token= br.AuthToken
                pwd= br.password
                secret= br.secretkey
                print(bruser)
                print(apikey)
                print(token)
                print(secret)
                print(pwd)


                Aliceblue= Alicebluesdk.Aliceapi(bruser,pwd,apikey,secret,token)
                t = threading.Thread(target=Aliceblue.login)
                t.start()   

            elif br.brokername.lower()=='zerodha':
                bruser= br.accountnumber
                apikey= br.apikey
                token= br.AuthToken
                secret=br.secretkey

                zerodha= zerodhasdk.kitesetup(bruser,apikey,secret)
                t = threading.Thread(target=zerodha.login)
                t.start()   

            elif br.brokername.lower()=='stoxkart':
                bruser= br.accountnumber
                apikey= br.apikey
                token= br.AuthToken
                secret=br.secretkey
                stoxkart= stoxkartsdk.StoxkartConnect(apikey,secret,bruser,br.password)
                t = threading.Thread(target=stoxkart.login3 )
                t.start()   

            elif br.brokername.lower()=='flattrade':
                bruser= br.accountnumber
                apikey= br.apikey
                token= br.AuthToken
                secret=br.secretkey
                stoxkart= flattradesdk.FlattradeConnect(apikey,secret,bruser,br.password)
                t = threading.Thread(target=stoxkart.login2)
                t.start()   

            elif br.brokername.lower()=='hdfc':
                bruser= br.accountnumber
                apikey= br.apikey
                token= br.AuthToken
                secret=br.secretkey
                hdfcuser= hdfcsdk.HDFCSkyConnect(apikey,secret,bruser)
                t = threading.Thread(target=hdfcuser.login2)
                t.start() 
            elif br.brokername.lower()=='samco':
                bruser= br.accountnumber
                apikey= br.apikey
                token= br.AuthToken
                secret=br.secretkey
                samco= samcosdk.SAMCOConnect(apikey,secret,bruser,br.password)
                t = threading.Thread(target=samco.login)
                t.start() 

        def checkfunds(self):
            accountlist= md.Broker.objects.filter(user=1,valid=True)
            for br in accountlist:
                print(br.brokername)
                if br.active:
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
                            br.funds="Unable to Fetch Login your account Again"
                            # br.valid=False

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
                            br.funds="Unable to Fetch Login your account Again"
                            # br.valid= False

                            br.save()
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                    elif br.brokername.lower()=='fyers':
                        bruser= br.accountnumber
                        pwd= br.password
                        apikey= br.apikey
                        token= br.AuthToken
                        print('eh')
                        self.broker = fyerssdk.HTTP(bruser,br.secretkey,token)
                        fund,excp=self.broker.checkfunds()
                        print(fund)

                        if fund:
                            br.funds=fund[0]['equityAmount']
                            br.valid= True
                            br.save()
                        else: 
                            br.funds="Unable to Fetch Login your account Again"
                            # br.valid= False

                            br.save()
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                    elif br.brokername.lower()=='motilal':
                        bruser= br.accountnumber
                        pwd= br.password
                        apikey= br.apikey
                        token= br.AuthToken
                        self.broker = motilalsdk.HTTP(bruser,pwd,apikey,token)
                        fund,excp=self.broker.checkfunds()
                        print(fund)

                        if fund:
                            br.funds=fund[0]['amount']
                            br.valid= True
                            br.save()
                        else: 
                            br.funds="Unable to Fetch Login your account Again"
                            # br.valid= False

                            br.save()
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                    
                    elif br.brokername.lower()=='groww':

                        token= br.AuthToken
                        self.broker = growwsdk.HTTP(token)
                        fund,excp=self.broker.checkfunds()
                        print(fund)

                        if fund:
                            br.funds=fund
                            br.valid= True
                            br.save()
                        else: 
                            br.funds="Unable to Fetch Login your account Again"
                            br.valid= False

                            br.save()
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                    elif br.brokername.lower()=='upstox':
                        print('heresssssss1')
                        token= br.AuthToken
                        bruser= br.accountnumber
                        apikey= br.apikey

                        self.broker = upstoxsdk.HTTP(bruser,apikey)
                        fund,excp=self.broker.checkfunds()
                        print(fund)

                        if fund:
                            br.funds=fund
                            br.valid= True
                            br.save()
                        else: 
                            br.funds="Unable to Fetch Login your account Again"
                            br.valid= False

                            br.save()
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                    elif br.brokername.lower()=='dhan':
                        print('heresssssss')
                        token= br.AuthToken
                        bruser= br.accountnumber
                        apikey= br.apikey

                        dhan = dhansdk.HTTP(bruser,token)
                        fund,excp=dhan.checkfunds()
                        print(fund)

                        if fund:
                            br.funds=fund
                            br.valid= True
                            br.save()
                        else: 
                            br.funds="Unable to Fetch Login your account Again"
                            br.valid= False

                            br.save()
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                    elif br.brokername.lower()=='zerodha':
                        print('heresssssss')
                        token= br.AuthToken
                        bruser= br.accountnumber
                        apikey= br.apikey
                        secret=br.secretkey

                        zerodha = zerodhasdk.HTTP(bruser,apikey,secret)
                        fund,excp=zerodha.checkfunds()
                        print(fund)

                        if fund:
                            br.funds=fund
                            br.save()
                        else: 
                            br.funds="Unable to Fetch Login your account Again"

                            br.save()
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                    elif br.brokername.lower()=='aliceblue':
                        token= br.AuthToken
                        bruser= br.accountnumber
                        apikey= br.apikey
                        secret=br.secretkey
                        pwd= br.password

                        Aliceblue= Alicebluesdk.HTTP(bruser,pwd,apikey,secret,token)
                        fund,excp=Aliceblue.checkfunds()
                        print(fund)

                        if fund:
                            br.funds=fund
                            br.save()
                        else: 
                            br.funds="Unable to Fetch Login your account Again"

                            br.save()
                            logpathfron.error(f'connect to administration with following error:-{excp}')



                    elif br.brokername.lower()=='stoxkart':
                            bruser= br.accountnumber
                            apikey= br.apikey
                            token= br.AuthToken
                            secret=br.secretkey

                            stoxkart= stoxkartsdk.HTTP(apikey,secret,bruser)
                            fund,excp=stoxkart.checkfunds()
                            if fund:
                                br.funds=fund
                                br.save()
                            else: 
                                br.funds="Unable to Fetch Login your account Again"

                                br.save()
                                logpathfron.error(f'connect to administration with following error:-{excp}')
                    elif br.brokername.lower()=='samco':
                            bruser= br.accountnumber
                            apikey= br.apikey
                            token= br.AuthToken
                            secret=br.secretkey

                            samco= samcosdk.HTTP(apikey,secret,bruser,br.password)

                            fund,excp=samco.checkfunds()
                            if fund:
                                br.funds=fund
                                br.save()
                            else: 
                                br.funds="Unable to Fetch Login your account Again"

                                br.save()
                                logpathfron.error(f'connect to administration with following error:-{excp}')

                    elif br.brokername.lower()=='hdfc':
                            bruser= br.accountnumber
                            apikey= br.apikey
                            token= br.AuthToken
                            secret=br.secretkey

                            hdfcuser= hdfcsdk.HTTP(apikey,secret,bruser)

                            fund,excp=hdfcuser.checkfunds()
                            if fund:
                                br.funds=fund
                                br.save()
                            else: 
                                br.funds="Unable to Fetch Login your account Again"

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
                        md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                        
                        for data in fund:
                            data['accountnumber']=br.accountnumber
                            data['user']=1
                            data['broker']='ANGEL'
                            data['nickname']=br.nickname
                            
                            serialize = ser.Allpositions(data=data)
                            if serialize.is_valid(raise_exception=True):
                                serialize.save()
                       
                    else: 
                        logpathfron.error(f'connect to administration with following error:-{excp}')

                elif br.brokername.lower()=='fyers':
                        bruser= br.accountnumber
                        pwd= br.password
                        apikey= br.apikey
                        token= br.AuthToken
                        print('eh')
                        self.broker = fyerssdk.HTTP(bruser,br.secretkey,token)
                        fund,excp=self.broker.getposition()
                        print(fund)

                        if fund:
                            md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                            
                            for data in fund:
                                data['accountnumber']=br.accountnumber
                                data['user']=1
                                data['broker']='FYERS'
                                data['nickname']=br.nickname
                                
                                serialize = ser.Allpositions(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                elif br.brokername.lower()=='motilal':
                        bruser= br.accountnumber
                        pwd= br.password
                        apikey= br.apikey
                        token= br.AuthToken
                        self.broker = motilalsdk.HTTP(bruser,pwd,apikey,token)
                        fund,excp=self.broker.getposition()

                        if fund:
                            md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()

                            for data in fund:
                                
                                data['accountnumber']=br.accountnumber
                                data['user']=1
                                data['broker']='MOTILAL'
                                data['nickname']=br.nickname
                                
                                serialize = ser.Allpositions(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                    
                elif br.brokername.lower()=='groww':

                        token= br.AuthToken
                        self.broker = growwsdk.HTTP(token)
                        fund,excp=self.broker.getposition()
                        print(fund)

                        if fund:
                            md.Allpositions.objects.filter(accountnumber=br.brokerid).delete()
                            
                            for data in fund:
                                data['accountnumber']=br.brokerid
                                data['user']=1
                                data['broker']='GROWW'
                                data['nickname']=br.nickname
                                
                                serialize = ser.Allpositions(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                        


                elif br.brokername.lower()=='upstox':

                        token= br.AuthToken

                        UPSTOX = upstoxsdk.HTTP(br.accountnumber,br.apikey)
                        fund,excp=UPSTOX.getposition()

                        if fund:
                            md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                            
                            for data in fund:
                                data['accountnumber']=br.accountnumber
                                data['user']=1
                                data['broker']='UPSTOX'
                                data['nickname']=br.nickname
                                
                                serialize = ser.Allpositions(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                
                elif br.brokername.lower()=='zerodha':

                        token= br.AuthToken

                        bruser= br.accountnumber
                        apikey= br.apikey
                        secret= br.secretkey
                        zerodha = zerodhasdk.HTTP(bruser,apikey,secret)
                        fund,excp=zerodha.getposition()

                        if fund:
                            md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                            
                            for data in fund:
                                data['accountnumber']=br.accountnumber
                                data['user']=1
                                data['broker']='UPSTOX'
                                data['nickname']=br.nickname
                                
                                serialize = ser.Allpositions(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                elif br.brokername.lower()=='stoxkart':
                    bruser= br.accountnumber
                    apikey= br.apikey
                    token= br.AuthToken
                    secret=br.secretkey

                    stoxkart= stoxkartsdk.StoxkartConnect(apikey,secret,bruser)

                elif br.brokername.lower()=='samco':
                    bruser= br.accountnumber
                    apikey= br.apikey
                    token= br.AuthToken
                    secret=br.secretkey

                    samco= samcosdk.HTTP(apikey,secret,bruser,br.password)
                    fund,excp=samco.getposition()
                    if fund:
                            md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                            
                            for data in fund:
                                data['accountnumber']=br.accountnumber
                                data['user']=1
                                data['broker']='SAMCO'
                                data['nickname']=br.nickname
                                
                                serialize = ser.Allpositions(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                    else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                elif br.brokername.lower()=='hdfc':
                    bruser= br.accountnumber
                    apikey= br.apikey
                    token= br.AuthToken
                    secret=br.secretkey

                    hdfcuser= hdfcsdk.HTTP(apikey,secret,bruser)
                    fund,excp=hdfcuser.getposition()
                    if fund:
                            md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                            
                            for data in fund:
                                data['accountnumber']=br.accountnumber
                                data['user']=1
                                data['broker']='SAMCO'
                                data['nickname']=br.nickname
                                
                                serialize = ser.Allpositions(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                    else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                elif br.brokername.lower()=='aliceblue':
                    bruser= br.accountnumber
                    apikey= br.apikey
                    token= br.AuthToken
                    secret=br.secretkey

                    Aliceblue= Alicebluesdk.HTTP(bruser,br.password,apikey,secret,token)
                    fund,excp=Aliceblue.getposition()
                    if fund:
                            md.Allpositions.objects.filter(accountnumber=br.accountnumber).delete()
                            
                            for data in fund:
                                data['accountnumber']=br.accountnumber
                                data['user']=1
                                data['broker']='SAMCO'
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

                elif br.brokername.lower()=='fyers':
                    bruser= br.accountnumber
                    pwd= br.password
                    apikey= br.apikey
                    token= br.AuthToken
                    print('eh')
                    self.broker = fyerssdk.HTTP(bruser,br.secretkey,token)
                    fund,excp=self.broker.allholding()
                    print(fund)
                    if fund:
                        md.allholding.objects.filter(accountnumber=br.accountnumber).delete()
                        for data in fund:

                            data['user']= 1
                            data['broker']= br.brokername
                            data['accountnumber']=br.accountnumber
                            data['nickname']= br.nickname



                            serialize = ser.allholding(data=data)
                            if serialize.is_valid(raise_exception=True):
                                serialize.save()

                       
                    else: 
                        logpathfron.error(f'connect to administration with following error:-{excp}')


                elif br.brokername.lower()=='motilal':
                    bruser= br.accountnumber
                    pwd= br.password
                    apikey= br.apikey
                    token= br.AuthToken
                    self.broker = motilalsdk.HTTP(bruser,pwd,apikey,token)
                    fund,excp=self.broker.allholding()

                    if fund:
                        md.allholding.objects.filter(accountnumber=br.accountnumber).delete()
                        for data in fund:

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

                    
                elif br.brokername.lower()=='groww':

                    token= br.AuthToken
                    self.broker = growwsdk.HTTP(token)
                    fund,excp=self.broker.allholding()
                    print(fund)

                    if fund:
                        md.allholding.objects.filter(accountnumber=br.brokerid).delete()
                        for data in fund:

                            data['user']= 1
                            data['broker']= br.brokername
                            data['accountnumber']=br.brokerid
                            data['nickname']= br.nickname


                            # data['totalprofitandloss']=fund['totalholding']['totalprofitandloss']
                            # data['totalpnlpercentage']=fund['totalholding']['totalpnlpercentage']

                            serialize = ser.allholding(data=data)
                            if serialize.is_valid(raise_exception=True):
                                serialize.save()

                       
                    else: 
                        logpathfron.error(f'connect to administration with following error:-{excp}')

                
                elif br.brokername.lower()=='upstox':

                        token= br.AuthToken

                        UPSTOX = upstoxsdk.HTTP(br.accountnumber,br.apikey)
                        fund,excp=UPSTOX.allholding()

                        if fund:
                            md.allholding.objects.filter(accountnumber=br.brokerid).delete()

                            for data in fund:
                                data['user']= 1

                                data['broker']= br.brokername
                                data['accountnumber']=br.brokerid
                                data['nickname']= br.nickname
                                
                                serialize = ser.allholding(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                elif br.brokername.lower()=='zerodha':

                        token= br.AuthToken

                           
                        bruser= br.accountnumber
                        apikey= br.apikey
                        secret= br.secretkey
                        zerodha = zerodhasdk.HTTP(bruser,apikey,secret)
                        fund,excp=zerodha.allholding()

                        if fund:
                            md.allholding.objects.filter(accountnumber=br.brokerid).delete()

                            for data in fund:
                                data['user']= 1

                                data['broker']= br.brokername
                                data['accountnumber']=br.brokerid
                                data['nickname']= br.nickname
                                
                                serialize = ser.allholding(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                elif br.brokername.lower()=='samco':

                        token= br.AuthToken

                           
                        bruser= br.accountnumber
                        apikey= br.apikey
                        secret= br.secretkey
                        samco= samcosdk.HTTP(apikey,secret,bruser,br.password)
                        fund,excp=samco.allholding()

                        if fund:
                            md.allholding.objects.filter(accountnumber=br.brokerid).delete()

                            for data in fund:
                                data['user']= 1

                                data['broker']= br.brokername
                                data['accountnumber']=br.brokerid
                                data['nickname']= br.nickname
                                
                                serialize = ser.allholding(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')

                elif br.brokername.lower()=='hdfc':

                        token= br.AuthToken

                           
                        bruser= br.accountnumber
                        apikey= br.apikey
                        secret= br.secretkey
                        hdfcuser= hdfcsdk.HTTP(apikey,secret,bruser)

                        fund,excp=hdfcuser.allholding()

                        if fund:
                            md.allholding.objects.filter(accountnumber=br.brokerid).delete()

                            for data in fund:
                                data['user']= 1

                                data['broker']= br.brokername
                                data['accountnumber']=br.brokerid
                                data['nickname']= br.nickname
                                
                                serialize = ser.allholding(data=data)
                                if serialize.is_valid(raise_exception=True):
                                    serialize.save()
                        
                        else: 
                            logpathfron.error(f'connect to administration with following error:-{excp}')
                elif br.brokername.lower()=='aliceblue':

                        token= br.AuthToken

                           
                        bruser= br.accountnumber
                        apikey= br.apikey
                        secret= br.secretkey
                        Aliceblue= Alicebluesdk.HTTP(bruser,pwd,apikey,secret,token)

                        fund,excp=Aliceblue.allholding()

                        if fund:
                            md.allholding.objects.filter(accountnumber=br.brokerid).delete()

                            for data in fund:
                                data['user']= 1

                                data['broker']= br.brokername
                                data['accountnumber']=br.brokerid
                                data['nickname']= br.nickname
                                
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

                            if br.brokername=='GROWW':
                           

                                
                                GROWW = growwsdk.HTTP(token )
                                order_ids=GROWW.cancel_order(orderobj.exchange,orderobj.orderid)

                            if  br.brokername=='MOTILAL':
                                MOTILAL = motilalsdk.HTTP(bruser,pwd,apikey,token)
                                order_ids=MOTILAL.cancel_order(orderobj.orderid)

                            if  br.brokername=='ZERODHA':
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret= br.secretkey
                                zerodha = zerodhasdk.HTTP(bruser,apikey,secret)  
                                order_ids=zerodha.cancel_order(orderobj.orderid)

                            if  br.brokername=='samco':
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret= br.secretkey
                                samco= samcosdk.HTTP(apikey,secret,bruser,br.password)
                                order_ids=samco.cancel_order(orderobj.orderid)
                            if  br.brokername=='hdfc':
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret= br.secretkey
                                hdfcuser= hdfcsdk.HTTP(apikey,secret,bruser)
                                order_ids=hdfcuser.cancel_order(orderobj.orderid)

                            
                              
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

            if broker =='GROWW':
                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['groww_order_id']).last()
                    if order:
                        order.orderstatus= 'OPEN' if  i['order_status'].upper()=='ACKED' else i['order_status'].upper()
                        order.avg_price=i['average_fill_price']
                        order.save()
            if broker =='DHAN':
                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['orderId']).last()
                    if order:
                        order.orderstatus= i['orderStatus'].upper()
                        order.avg_price=i['price']
                        order.save()
            if broker =='MOTILAL':
                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['uniqueorderid']).last()
                    if order:
                        order.orderstatus='COMPLETED' if i['orderstatus'].upper()== 'TRADED' else  i['orderstatus'].upper()
                        order.avg_price=i['price']
                        order.lastmodifiedtime= i['lastmodifiedtime']
                        order.save()

            if broker =='UPSTOX':
                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['order_id']).last()
                    if order:
                        order.orderstatus=i['status'].upper()
                        order.avg_price=i['average_price']
                        order.lastmodifiedtime= i['order_timestamp']
                        order.save()
            if broker =='ZERODHA':
                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['order_id']).last()
                    if order:
                        order.orderstatus=i['status'].upper()
                        order.avg_price=i['average_price']
                        order.lastmodifiedtime= i['order_timestamp']
                        order.save()

            if broker =='SAMCO':
                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['orderNumber']).last()
                    if order:
                        order.orderstatus=i['orderStatus'].upper()
                        order.avg_price=i['averagePrice']
                        order.lastmodifiedtime= i['orderTime']
                        order.save()
            if broker =='HDFC':
                for i in orderbook:
                    order= md.orderobject.objects.filter(orderid=i['oms_order_id']).last()
                    if order:
                        order.orderstatus=i['order_status'].upper()
                        order.avg_price=i['average_trade_price']
                        order.lastmodifiedtime= i['order_entry_time']
                        order.save()
            if broker =='ALICEBLUE':
                for i in orderbook:
                    # print(i)
                    order= md.orderobject.objects.filter(orderid=i['Nstordno']).last()
                    if order:
                        order.orderstatus=i['Status'].upper()
                        order.avg_price=i['Avgprc']
                        order.lastmodifiedtime= i['orderentrytime']
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
                            print(br.brokername)
                            if br.brokername=='SHOONYA':
                                        self.broker = shoonyasdk.HTTP(token=token,
                                                            user=bruser, 
                                                            pwd=pwd, 
                                                            vendorcode= vendorcode,
                                                            app_key=apikey, 
                                                            imei=imei)
                                        order_ids=self.broker.orderBook()
                                        if order_ids:
                                            self.asignorderstatus(order_ids,'SHOONYA')
                            if br.brokername=='ANGEL':
                                    

                                        
                                        Angel = Angelsdk.HTTP(token=token,
                                                            username=bruser, 
                                                            pwd=pwd, 
                                                            api_key=apikey, )
                                        order_ids=Angel.orderBook()
                                        time.sleep(1)
                                        if order_ids:

                                            self.asignorderstatus(order_ids,'ANGEL')


                            if br.brokername=='GROWW':
                                    

                                        
                                        groww = growwsdk.HTTP(token)
                                        order_ids=groww.orderBook()
                                        print(order_ids)
                                        self.asignorderstatus(order_ids,'GROWW')
                            if  br.brokername=='DHAN':
                                dhan = dhansdk.HTTP(bruser,token)
                                order_ids=dhan.orderBook()
                                print(order_ids)
                                self.asignorderstatus(order_ids,'DHAN')
                            if  br.brokername=='MOTILAL':
                                MOTILAL = motilalsdk.HTTP(bruser,pwd,apikey,token)
                                order_ids=MOTILAL.orderBook()
                                print(order_ids)
                                if order_ids['data']:

                                    self.asignorderstatus(order_ids['data'],'MOTILAL')

                            if  br.brokername=='UPSTOX':
                                UPSTOX = upstoxsdk.HTTP(bruser,apikey)
                                order_ids=UPSTOX.orderBook()
                                print(order_ids)
                                if order_ids:
                                    self.asignorderstatus(order_ids,'UPSTOX')

                            if  br.brokername=='ZERODHA':
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret= br.secretkey
                                zerodha = zerodhasdk.HTTP(bruser,apikey,secret)
                                order_ids=zerodha.orderBook()
                              
                                print(order_ids)
                                if order_ids:

                                    self.asignorderstatus(order_ids,'ZERODHA')
                            if  br.brokername=='SAMCO':
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret= br.secretkey
                                samco= samcosdk.HTTP(apikey,secret,bruser,br.password)

                                order_ids=samco.orderBook()
                              
                                print(order_ids)
                                if order_ids:

                                    self.asignorderstatus(order_ids,'SAMCO')

                            if  br.brokername=='HDFC':
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret= br.secretkey
                                hdfcuser= hdfcsdk.HTTP(apikey,secret,bruser)

                                order_ids=hdfcuser.orderBook()
                              
                                if order_ids:

                                    self.asignorderstatus(order_ids,'HDFC')

                            if  br.brokername=='ALICEBLUE':
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret= br.secretkey
                                Aliceblue= Alicebluesdk.HTTP(bruser,pwd,apikey,secret,token)

                                order_ids=Aliceblue.orderBook()
                                print(order_ids)
                              
                                if order_ids:

                                    self.asignorderstatus(order_ids,'ALICEBLUE')



                                

                        else:
                            
                            msg=f"Account Number {br.accountnumber} Nickname {br.nickname} is not logged in. Kindly Logged in to the Account"
                            logpathfron.error(msg)

        
            
                        
            except Exception as e:
                print(str(e))
                logpathfron.error(f'Contact to administrator with following error:{e}')

                return str(e)


        def modifyorder(self,data):
            try:
                print(data)
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
                        if br.brokername=='GROWW':
                           

                            
                            GROWW = growwsdk.HTTP(token )
                            order_ids=GROWW.modifyorder(data,orderobj)

                        if br.brokername=='MOTILAL':
                            motilal = motilalsdk.HTTP(bruser,pwd,apikey,token)
                            order_ids=motilal.modifyorder(data,orderobj)


                        if br.brokername=='ZERODHA':
                           


                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret=br.secretkey

                                zerodha = zerodhasdk.HTTP(bruser,apikey,secret)
                                order_ids=zerodha.modifyorder(data,orderobj)

                        if br.brokername=='hdfc':
                           


                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret=br.secretkey

                                hdfcuser= hdfcsdk.HTTP(apikey,secret,bruser)
                                order_ids=hdfcuser.modifyorder(data,orderobj)

                        if br.brokername=='samco':
                           


                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret=br.secretkey

                                samco= samcosdk.HTTP(apikey,secret,bruser,br.password)
                                order_ids=samco.modifyorder(data,orderobj)

                            

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
                order_ids= None
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
                            secretkey= br.secretkey

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
                            if br.brokername=='FYERS':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname

                                
                                FYERS = fyerssdk.HTTP(bruser,secretkey,token)
                                order_ids=FYERS.placeorder(orderparams,self.orderobject)
                            if br.brokername=='MOTILAL':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname

                                
                                FYERS = motilalsdk.HTTP(bruser,pwd,apikey,token)
                                order_ids=FYERS.placeorder(orderparams,self.orderobject)


                            if br.brokername=='GROWW':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname

                                
                                GROWW = growwsdk.HTTP(token)
                                order_ids=GROWW.placeorder(orderparams,self.orderobject)

                            if br.brokername=='UPSTOX':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname

                                
                                UPSTOX = upstoxsdk.HTTP(bruser,apikey)
                                order_ids=UPSTOX.placeorder(orderparams,self.orderobject)

                            if br.brokername=='DHAN':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname

                                
                                dhan = dhansdk.HTTP(bruser,token)
                                order_ids=dhan.placeorder(orderparams,self.orderobject)
                            if br.brokername=='ZERODHA':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret=br.secretkey

                                zerodha = zerodhasdk.HTTP(bruser,apikey,secret)
                                fund,excp=zerodha.placeorder(orderparams,self.orderobject)
                            if br.brokername=='SAMCO':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret=br.secretkey

                                samco= samcosdk.HTTP(apikey,secret,bruser,br.password)
                                fund,excp=samco.placeorder(orderparams,self.orderobject)
                            if br.brokername=='HDFC':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret=br.secretkey

                                hdfcuser= hdfcsdk.HTTP(apikey,secret,bruser)
                                fund,excp=hdfcuser.placeorder(orderparams,self.orderobject)

                            if br.brokername=='ALICEBLUE':
                                orderparams['broker']=br.brokername
                                orderparams['nickname']=br.nickname
                                bruser= br.accountnumber
                                apikey= br.apikey
                                secret=br.secretkey
                                Aliceblue= Alicebluesdk.HTTP(bruser,pwd,apikey,secret,token)
                                fund,excp=Aliceblue.placeorder(orderparams,self.orderobject)


                                
                               


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
            broker= md.Broker.objects.filter(brokername='DHAN').last()
            autoken= broker.AuthToken
            accountno= broker.accountnumber
            webobj= dhansdk.WebSocketConnect(accountno,autoken)
            webobj.start_thread()
        
        def fyerswebsocket(self):
           
                
            broker= md.Broker.objects.filter(brokername='FYERS',valid=True).last()
            autoken= broker.imei
            accountno= broker.accountnumber
            secretkey= broker.secretkey
            if autoken:
                webobj= fyerssdk.WebSocketConnect(accountno,secretkey,autoken)
                webobj.start_thread()
            else:
                logpathfron.error('no  access token found to get watchlist data kindly login at least 1 fyers account')


        def upstoxwebsoket(self):
           
                
            broker= md.Broker.objects.filter(brokername='UPSTOX',valid=True).last()
            autoken= broker.imei
            accountno= broker.accountnumber
            secretkey= broker.secretkey
            apikey= broker.apikey
            if autoken:
                webobj= upstoxsdk.WebSocketConnect(accountno,apikey)
                webobj.start_thread()
            else:
                logpathfron.error('no  access token found to get watchlist data kindly login at least 1 fyers account')


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
        

                 
                 
# obj=utility(1)
# obj.checkfunds()
# obj.upstoxwebsoket()

# data =obj.createOrderpunchsymbol()

