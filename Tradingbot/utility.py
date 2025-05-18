import Tradingbot.models as md 
import Tradingbot.serializers as ser 
from .Brokers import shoonyasdk,Angelsdk
from concurrent.futures import ThreadPoolExecutor
import pathlib 
import os
import json
import asyncio
path = pathlib.Path(__file__).parent.parent
print(path)



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

        

        
                    

        def logoutbroker(self,data):
            if data['broker'].lower()=='shoonya':
                   self.broker = shoonyasdk.shoonyasetup()
                   self.broker.logout()


              
              

        def placeorder(self,orderparams,batmcal=60,subclients=0,STOPLOSS=True,PAPER=True,makesymbol=True,advicecheck=''):
            try:

                
                orderid=  []
                placeorders=False
                quantity=orderparams['quantity']

                # if orderparams['']
                if not orderparams['account']:


                    alllist=md.Broker.objects.filter(brokername=orderparams['broker'])
                    for i in alllist:
                        if i.valid:
                            bruser= i.accountnumber
                            pwd= i.password
                            vendorcode=i.vendorcode
                            apikey= i.apikey
                            imei= i.imei
                            token= i.AuthToken
                            if i.brokername=='SHOONYA':
                                 
                                shoonya = shoonyasdk.HTTP(token=token,
                                                    user=bruser, 
                                                    pwd=pwd, 
                                                    vendorcode= vendorcode,
                                                    app_key=apikey, 
                                                    imei=imei)
                                order_ids=shoonya.placeorder(orderparams,self.orderobject,False,False)

                            if i.brokername=='ANGEL':
                                Angel = Angelsdk.HTTP(token=token,
                                                    username=bruser, 
                                                    pwd=pwd, 
                                                    api_key=apikey, )
                                order_ids=Angel.placeorder(orderparams,self.orderobject,False,False)

                   
                elif orderparams['account']:
                         br=md.Broker.objects.filter(brokerid=orderparams['account']['brokerid']).last()
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
                                order_ids=self.broker.placeorder(orderparams,self.orderobject,False,False)
                        
                            if br.brokername=='ANGEL':
                                Angel = Angelsdk.HTTP(token=token,
                                                    username=bruser, 
                                                    pwd=pwd, 
                                                    api_key=apikey, )
                                order_ids=Angel.placeorder(orderparams,self.orderobject,False,False)

                              
                        


                    # self.broker=self.brokerobj(orderparams['broker'])


                # quotes= self.broker.get_quotes(orderparams['segment'],orderparams['symboltoken'])
                # orderparams['ltp']= float(quotes['lp'])
                # orderparams['lotsize']=quotes['ls'] if orderparams['fno']!= 'EQ' else 1
                # orderparams['quantity']= str(quantity*orderparams['lotsize'])
                
                return order_ids
                        
            except Exception as e:
                print(str(e))
                return str(e)


        def loginshoonya(self):
            obj2= md.Broker.objects.filter(websocket=True,brokername='SHOONYA').last()
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
# obj.shoonyawebsocket()
# data =obj.createOrderpunchsymbol()

