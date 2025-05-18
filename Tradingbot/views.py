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
from .Brokers import shoonyasdk,Angelsdk
from .utility import utility
from . import env
import os
import pathlib
path = pathlib.Path(__file__).parent.parent
logpath= os.path.join(path,'Botlogs/Frontendlog.logs')
logpath= os.path.normpath(logpath)
import json

print(logpath,'logpath')
logger=env.setup_logger(logpath)

# Create your views here.
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
                proj= md.Broker.objects.filter(user=users.id,brokername='SHOONYA').values('brokerid','Username','accountnumber','brokername','active','apikey','pasword',
                                                                 'vendorcode','AuthToken')
            elif request.GET.get('broker').lower()=='all':
                proj= md.Broker.objects.filter(user=users.id).values('brokerid','accountnumber','brokername')
            

            elif request.GET.get('broker').lower()=='angegl':
                proj= md.Broker.objects.filter(user=users.id,brokername='ANGEL').values('brokerid','accountnumber','brokername','active','apikey','pasword','secretkey','AuthToken')
            
            else:
                proj = []

            
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
    {"NAME":"FYERS"},
    {"NAME":"MOTILAL"},
    {"NAME":"ANANDRATHI"},
    {"NAME":"GROWW"},
    {"NAME":"ZERODHA"},
    {"NAME":"SAMCO"},
    {"NAME":"FLATTRADE"},
    {"NAME":"BIGUL"},
    {"NAME":"STOXKART"}

    
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
            if request.GET.get('Broker').lower()== "shoonya":
                exchange = request.GET.get('exchange')
                instrument = request.GET.get('instrument')
                name = request.GET.get('name')


                datas=shoonyasdk.optionchain(name.upper(),exchange.upper(),instrument.upper())
            if request.GET.get('Broker').lower()=="angel":
                exchange = request.GET.get('exchange')
                instrument = request.GET.get('instrument')
                name = request.GET.get('name')
                datas= Angelsdk.searchscrip(name.upper(),exchange.upper(),instrument.upper())
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



    def post(self, request):
        user = request.user
        data=dict()
        try:
            print(request.data)
            data['broker']= request.data.get('brokerName4')
            data['exchange'] = request.data.get('exchange')
            data['tradingsymbol'] = request.data.get('selectsymbol')
            data['ltp'] = request.data.get('price')
            data['symboltoken'] = request.data.get('token')


            data['quantity'] = request.data.get('quantity')
            data['ordertype'] =request.data.get('orderType')
            data['product_type'] = request.data.get('product')
            data['transactiontype'] = request.data.get('side')
            data['account'] = request.data.get('accountname')
            dash=utility(user)
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
            if request.GET.get('type')== "open":
                data=md.orderobject.objects.filter(user=users,status=True).values('updated_at','orderid','tradingsymbol','symboltoken','quantity','avg_price',
                                                                                  'exchange','broker','accountno','side','orderstatus' )
            elif  request.GET.get('type')== "close":
                data=md.orderobject.objects.filter(user=users,status=False).values('updated_at','orderid','tradingsymbol','symboltoken','quantity','avg_price',
                                                                                  'exchange','broker','accountno','side','orderstatus' )
            
            elif  request.GET.get('type')== "all":
                data=md.orderobject.objects.filter(user=users).values('updated_at','orderid','tradingsymbol','symboltoken','quantity','avg_price',
                                                                      'exchange','broker','accountno','side','orderstatus')


            
            
                

            
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
            data1= dict()
            if request.GET.get('broker')=='all':
                datas= brokerlist
            if request.GET.get('broker').lower()== "shoonya":
  

                datas= md.Broker.objects.filter(user=users.id,brokername='SHOONYA').values('brokerid','brokername','accountnumber','apikey','secretkey','password','vendorcode','AuthToken','active')
                print(datas)
            elif request.GET.get('broker').lower()=='angel':
                datas= md.Broker.objects.filter(user=users.id,brokername='ANGEL').values('brokerid','accountnumber','brokername','active','apikey','password','secretkey','AuthToken')
            

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
                print(data)

                file.close

            


            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


