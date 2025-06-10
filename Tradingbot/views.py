from django.shortcuts import render
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework import generics,permissions,status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import GenericAPIView,UpdateAPIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_protect
from . import serializers as ser 
from . import models as md
import datetime
from .Brokers import shoonyasdk,Angelsdk,motilalsdk,growwsdk,dhansdk,flattradesdk,stoxkartsdk,fyerssdk,upstoxsdk,zerodhasdk,hdfcsdk,samcosdk,Alicebluesdk
from .utility import utility
from . import env
import os
import pathlib
path = pathlib.Path(__file__).resolve().parent.parent
logpath= os.path.join(path,'Botlogs/Frontendlog.logs')
logpath= os.path.normpath(logpath)
import json
import pytz
import time
from django.middleware import csrf
from django.http import JsonResponse

print(logpath,'logpath')
logger=env.setup_logger(logpath)

# Create your views here.
def get_csrf_token(request):
    csrf_token = csrf.get_token(request)
    return JsonResponse({'csrfToken': csrf_token})








class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
            try:

                serializer = AuthTokenSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data['user']
            
                login(request, user)
                
                user_login = super(LoginAPI, self).post(request, format=None)
                format= '%Y-%m-%dT%H:%M:%S.%f%z'
                user_login.data['expiry']= datetime.datetime.strptime(user_login.data['expiry'],format).timestamp()
                print(user_login.data)
                logger.info("Login Sucessfull")

                return Response({"message":user_login.data,
                                "id":user.id},
                                status=status.HTTP_200_OK)
                
            except Exception as e :
                logger.error(e)
                return Response({
                            "message":e,
                            "code": status.HTTP_400_BAD_REQUEST
                        },  
                        status=status.HTTP_400_BAD_REQUEST)


class broker(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            users = request.user
            if request.GET.get('broker').lower()=='shoonya':
                proj= md.Broker.objects.filter(user=users.id,brokername='SHOONYA').values('brokerid','Username','accountnumber','brokername','active','apikey','password',
                                                                 'vendorcode','AuthToken')

            elif request.GET.get('broker').lower()=='angel':
                proj= md.Broker.objects.filter(user=users.id,brokername='ANGEL').values('brokerid','accountnumber','brokername','active','apikey','password','secretkey','AuthToken')
            
            else:
                proj = []
            if request.GET.get('account').lower()=='all':
                proj= md.Broker.objects.filter(user=users.id,valid=True,brokername=request.GET.get('broker').upper()).values('brokerid','accountnumber','brokername')
            

            
            return Response({"message":proj})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        user = request.user
        data=dict()
        try:
            if not request.data.get('brokerid'):

                print(request.data)
                request.data['brokername']=request.data.get('brokerName')
                request.data['user']= user.id
                serialize = ser.Broker(data=request.data)
                if serialize.is_valid(raise_exception=True):
                        serialize.save()
                
            
                logger.info('Broker added sucessfully')
                
                return Response({"Message":'sucessfl'},status=status.HTTP_200_OK)


          
           
           

            
        except Exception as e:
            logger.error(e)
            
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        

    def put(self, request, *args, **kwargs):
        """
        Update the profile
        user.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:

            user = request.user
            print(request.data)
            put=request.data.get('put')
            if not put :
                proj= md.Broker.objects.filter(brokerid=request.data.get('brokerid')).last()
                proj.active= False if proj.active else True
                print(proj.brokername)
                if proj.brokername=='GROWW':    
                    proj.valid=True
                if proj.brokername=='DHAN':    
                    proj.valid=True

                proj.save()

            else :
                    serialize = ser.Broker(data=request.data)
                    serialize.is_valid(raise_exception=True)
                    valuessetbr = serialize.validated_data
                    md.Broker.objects.filter(brokerid=request.data.get('brokerid')).update(**valuessetbr)
                    print(put)

            logger.info('Broked saved')

                

                
            
        
            return Response(
                {"Message": "Successfully Updated Attendance"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,*args,**kwargs):
        try:

            user = request.user
              
            print(request.GET.get('brokerid'))
            if int(request.GET.get('brokerid')) == 0:

                block= md.Broker.objects.filter(user=user.id,brokerid=request.GET.get('brokerid'))
                for i in block:
                 

                    i.delete()
            else:
              block=  md.Broker.objects.filter(user=user.id,brokerid=request.GET.get('brokerid')).last()
              block.delete()    

            return Response({"message":'deleted'})
            
        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


brokerlist=[
    {"NAME":"ANGEL"},
    {"NAME":"SHOONYA"},
    {"NAME":"DHAN"},
    {"NAME":"MOTILAL"},
    {"NAME":"GROWW"},
    {"NAME":"FYERS"},
    {"NAME":"UPSTOX"},
    {"NAME":"ZERODHA"},
    {"NAME":"SAMCO"},
    {"NAME":"HDFC"},
    {"NAME":"FLATTRADE"},
    {"NAME":"STOXKART"},
    {"NAME":'ALICEBLUE'}
    # {"NAME":"BIGUL"},
    # {"NAME":"ANANDRATHI"},



    
]





class Getsymbols(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):


        try:
            users = request.user
            data= []
            data1= dict()
            if request.GET.get('Broker')=='all':
                datas= brokerlist

            else:
                exchange = request.GET.get('exchange')
                instrument = request.GET.get('instrument')
                name = request.GET.get('name')
                if request.GET.get('Broker').lower()== "shoonya":
                


                    datas=shoonyasdk.optionchain(name.upper(),exchange.upper(),instrument.upper())
                if request.GET.get('Broker').lower()=="angel":
                   
                    datas= Angelsdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())

                
                if request.GET.get('Broker').lower()=="motilal":
                    datas= motilalsdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())

                if request.GET.get('Broker').lower()=="groww":
                    datas= growwsdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())

                if request.GET.get('Broker').lower()=="dhan":
                    datas= dhansdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())
               
                if request.GET.get('Broker').lower()=="flattrade":
                    datas= flattradesdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())
                if request.GET.get('Broker').lower()=="stoxkart":
                    datas= stoxkartsdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())

                if request.GET.get('Broker').lower()=="fyers":
                    datas= fyerssdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())

                if request.GET.get('Broker').lower()=="upstox":
                    datas= upstoxsdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())
                if request.GET.get('Broker').lower()=="zerodha":
                    sdk =zerodhasdk.kitesetup('')
                    datas= sdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())
                if request.GET.get('Broker').lower()=="hdfc":
            
                    datas= hdfcsdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())
                if request.GET.get('Broker').lower()=="samco":
                    HT=samcosdk.HTTP()
            
                    datas= HT.searchscrip(name.upper(),exchange.upper(),instrument.upper())

                if request.GET.get('Broker').lower()=="aliceblue":
            
                    datas= Alicebluesdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())


                if datas.empty:
                    datas= []



         
            
            print(datas)


                # datas = datas.to_dict(orient="records")

            return Response({"message":datas},status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


class placeorder (GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):


        try:
            users = request.user
            dash=utility(users)
            oderids= request.GET.get('selectedRows')
            oderids= eval(oderids)
            print(type(oderids),oderids)
            dash.cancel_order(oderids)

            
           



            return Response({"message":'ok'},status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)






    def post(self, request):
        user = request.user
        data=dict()
        try:
            print(request.data)
            data['broker']= request.data.get('brokerName4')
            data['exchange'] = request.data.get('exchange')
            data['instrument'] = request.data.get('instrument')
            data['tradingsymbol'] = request.data.get('selectsymbol')
            data['ltp'] = request.data.get('price')
            data['symboltoken'] = request.data.get('token')
            data['quantity'] = request.data.get('quantity')
            data['ordertype'] =request.data.get('orderType')
            data['product_type'] = request.data.get('product')
            data['transactiontype'] = request.data.get('side')
            data['account'] = request.data.get('accountname')
            data['discloseqty'] = request.data.get('discloseqty')
            data['lotsize'] = request.data.get('lotsize')



            
            dash=utility(user)
            if request.data.get('modify'):
                data['orderid']= request.data.get('orderid')
                oid=dash.modifyorder(data)
            else :
                oid=dash.placeorder(data)

            
            
                    
            

          
           
           

            
            return Response({"message":"successful" },status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            print(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )



class loginbroker (GenericAPIView):
    def post(self, request):
        user = request.user
        data=dict()
        try:

       
        
            data['brokerid'] = request.data.get("brokerid")



            dash=utility(user)
            oid=dash.loginbroker(data)

          
           
           

            
            return Response({"message":"successful" },status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class loginbrokerredirect (GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):


        try:
            user = request.user

            data= dict()
            data['brokerid'] = request.GET.get("brokerid")
            dash=utility(user)
            oid=dash.loginbroker(data)
            time.sleep(2)
            db = md.Broker.objects.filter(brokerid=data['brokerid']).last()
            print(db.url,'urlssssssssssssssssssssssssssssssssssssssssssssss')
           



            return Response({"message":db.url},status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)




    def post(self, request):
        user = request.user
        data=dict()
        try:

       
        
            data['brokerid'] = request.data.get("brokerid")
            print(request.data)
            db = md.Broker.objects.filter(brokerid=int(data['brokerid'])).last()
            db.AuthToken=  request.data.get("accesstoken")
            db.save()


          
           
           

            
            return Response({"message":'ok' },status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )




class logoutbroker (GenericAPIView):
    def post(self, request):
        user = request.user
        data=dict()
        try:


            dash=utility(user)
            data['broker'] = request.data.get("brokerName3")
            oid=dash.logoutbroker(data)
                    
            

          
           
           

            
            return Response({"message":"successful" },status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class postionsobj(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            finaldata= []
            users = request.user.id
            data = dict()
            start= datetime.datetime.now(tz= pytz.timezone('Asia/Kolkata')).replace(hour=23, minute=59, second=0, microsecond=0)
            end = start- datetime.timedelta(days=1)
            print(end,start)
            dash=utility(users)
            
            dash.orderstatus()

            if  request.GET.get('type')== "all":
                data=md.orderobject.objects.filter(user=users,updated_at__range=(end,start)).values('id','updated_at','orderid','tradingsymbol','symboltoken','quantity','avg_price',
                                                                      'exchange','broker','accountnumber','side','orderstatus','transactiontype','instrument')
                
                # data['sid']=data['id']
                

            
            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)

class watchlist(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            users = request.user
            data =dict()
            proj= md.Broker.objects.filter(user=users.id).values('id','Username','accountnumber','brokername','value')
            
            print(proj) 
            return Response({"message":proj})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        user = request.user
        data=dict()
        try:
            print(request.data)
            request.data['broker']=request.data.get('brokerName4')
            request.data['tradingsymbol']=request.data.get('selectsymbol')
            request.data['symboltoken']=request.data.get('token')
            request.data['exchange']=request.data.get('exchange')
            request.data['user']= user.id
            request.data['subscribe']= True
            request.data['newevent']= True
            

            
            serialize = ser.watchlist(data=request.data)
            if serialize.is_valid(raise_exception=True):
                    serialize.save()
            
        
            
            return Response({"Message":'sucessfl'},status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            logger.error(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    def delete(self,request,*args,**kwargs):
        try:

            user = request.user
              
            print(request.GET.get('id'))
            if int(request.GET.get('id')) == 0:

                block= md.watchlist.objects.filter(user=user.id,broker=request.GET.get('brokername'),symboltoken=int(request.GET.get('id')))
                for i in block:
                    i.subscribe=False
                    i.newevent=True

                    i.save()
            else:
              block=  md.watchlist.objects.filter(user=user.id,broker=request.GET.get('brokername'),symboltoken=request.GET.get('id'),subscribe=True).last()
              print(block)
              block.subscribe=False
              block.newevent=True

              block.save()    


                 
            
            return Response(
                {"message": "Successfully deleted"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
                        logger.error(e)
                        return Response(
                {"message": e},
                status=status.HTTP_400_BAD_REQUEST
            )




class loadaccount(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):


        try:
            users = request.user
            data= []
            print(request.GET.get('broker'))
            data1= dict()
            if request.GET.get('broker')=='all':
                datas= brokerlist
            if request.GET.get('broker').lower()== "shoonya":
  

                datas= md.Broker.objects.filter(user=users.id,brokername='SHOONYA').values('brokerid','brokername','accountnumber','apikey','secretkey','password','vendorcode','AuthToken','active')
            elif request.GET.get('broker').lower()=='angel':
                datas= md.Broker.objects.filter(user=users.id,brokername='ANGEL').values('brokerid','accountnumber','brokername','active','apikey','password','secretkey','AuthToken')
            
            elif request.GET.get('broker').lower()=='fyers':
                datas= md.Broker.objects.filter(user=users.id,brokername='FYERS').values('brokerid','accountnumber','secretkey','AuthToken','active')
            

            elif request.GET.get('broker').lower()=='motilal':
                datas= md.Broker.objects.filter(user=users.id,brokername='MOTILAL').values('brokerid','accountnumber','password','AuthToken','apikey','active')

            elif request.GET.get('broker').lower()=='groww':
                datas= md.Broker.objects.filter(user=users.id,brokername='GROWW').values('brokerid','AuthToken','active')
            
            elif request.GET.get('broker').lower()=='dhan':
                datas= md.Broker.objects.filter(user=users.id,brokername='DHAN').values('brokerid','accountnumber','AuthToken','active','password')
            
            elif request.GET.get('broker').lower()=='upstox':
                datas= md.Broker.objects.filter(user=users.id,brokername='UPSTOX').values('brokerid','accountnumber','AuthToken','active','apikey','secretkey')
            
            elif request.GET.get('broker').upper()=='ALICEBLUE':
                print('here')
                datas= md.Broker.objects.filter(user=users.id,brokername='ALICEBLUE').values('brokerid','accountnumber','active','apikey','AuthToken','secretkey','password')

            elif request.GET.get('broker').upper()=='ZERODHA' or  request.GET.get('broker').upper()=='STOXKART'or request.GET.get('broker').upper()=='FLATTRADE' :
                print('here')
                datas= md.Broker.objects.filter(user=users.id,brokername=request.GET.get('broker').upper()).values('brokerid','accountnumber','active','AuthToken','apikey','secretkey','password')

            elif request.GET.get('broker').upper()=='HDFC'  :
                print('here')
                datas= md.Broker.objects.filter(user=users.id,brokername=request.GET.get('broker').upper()).values('brokerid','accountnumber','active','AuthToken','apikey','secretkey')
            elif request.GET.get('broker').upper()=='SAMCO'  :
                print('here')
                datas= md.Broker.objects.filter(user=users.id,brokername=request.GET.get('broker').upper()).values('brokerid','accountnumber','active','password','secretkey')

                # datas = datas.to_dict(orient="records")

            return Response({"message":datas})

        except Exception as e:
            print(e)
            logger.error(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


class sendlog(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):


        try:
            users = request.user
            data= []
            
            with open (logpath) as file:
                # data= json.load(file)
                data=file.readlines()

                file.close
                data.reverse()

            


            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


class getfunds(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user

            dash=utility(user)
            oid=dash.checkfunds()
            data = md.Broker.objects.filter(valid= True).values('brokername','nickname','accountnumber','funds')

            


            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


class getposition(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user

            dash=utility(user)

            oid=dash.getposition()
            data = md.Allpositions.objects.filter(user=1).values()

            


            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)




class getholding(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user

            dash=utility(user)

            oid=dash.getholding()
            data = md.allholding.objects.filter(user=1).values()

            


            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)



