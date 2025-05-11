import Tradingbot.models as md 
import Tradingbot.serializers as ser 
from .Brokers import shoonyasdk

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
            if broker.upper() =='SHOONYA':
                  self.broker = shoonyasdk.HTTP()

            return self.broker

        def loginbroker(self,data):
              if data['broker'].lower()=='shoonya':
                self.broker = shoonyasdk.shoonyasetup()
                self.broker.login()

                    
                    

        def logoutbroker(self,data):
            if data['broker'].lower()=='shoonya':
                   self.broker = shoonyasdk.shoonyasetup()
                   self.broker.logout()


              
              

        def placeorder(self,orderparams,batmcal=60,subclients=0,STOPLOSS=True,PAPER=True,makesymbol=True,advicecheck=''):
            try:

                
                orderid=  []
                placeorders=False
                quantity=orderparams['quantity']
                self.broker=self.brokerobj(orderparams['broker'])

                # quotes= self.broker.get_quotes(orderparams['segment'],orderparams['symboltoken'])
                # orderparams['ltp']= float(quotes['lp'])
                # orderparams['lotsize']=quotes['ls'] if orderparams['fno']!= 'EQ' else 1
                # orderparams['quantity']= str(quantity*orderparams['lotsize'])
                order_ids=self.broker.placeorder(orderparams,self.orderobject,False,False)
                
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

