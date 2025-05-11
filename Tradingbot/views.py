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
from .Brokers import shoonyasdk
from .utility import utility

# Create your views here.
class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
       
        login(request, user)
        
        user_login = super(LoginAPI, self).post(request, format=None)
        format= '%Y-%m-%dT%H:%M:%S.%f%z'
        user_login.data['expiry']= datetime.datetime.strptime(user_login.data['expiry'],format).timestamp()
        print(user_login.data)

        return Response({"message":user_login.data,
                         "id":user.id},
                          status=status.HTTP_200_OK)


class broker(GenericAPIView):
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
            request.data['brokername']=request.data.get('brokerName1')
            request.data['user']= user.id
            serialize = ser.Broker(data=request.data)
            if serialize.is_valid(raise_exception=True):
                    serialize.save()
            
        
            
            return Response({"Message":'sucessfl'},status=status.HTTP_200_OK)


          
           
           

            
        except Exception as e:
            print(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )



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


                datas=shoonyasdk.optionchain(name,exchange.upper(),instrument)

                # data1['Tradingsymbol']= datas['TradingSymbol']
                # data1['Lot']= datas['LotSize']
                # data1['Token']= datas['Token']
                # data1['Instrument']= datas['Instrument']

                # datas = datas.to_dict(orient="records")

                DATA=datas[datas['Instrument']=='FUTIDX']
                print(DATA)
            return Response({"message":datas})

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
            data['quantity'] = request.data.get('quantity')
            data['ordertype'] =request.data.get('ordertype')
            data['product_type'] = request.data.get('product')
            data['transactiontype'] = request.data.get('side')

            




            dash=utility(user)
            oid=dash.placeorder(data)
                    
            

          
           
           

            
            return Response({"message":"successful" },status=status.HTTP_200_OK)
        except Exception as e:
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

       
        
            data['broker'] = request.data.get("brokerName2")

            dash=utility(user)
            oid=dash.loginbroker(data)

          
           
           

            
            return Response({"message":"successful" },status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
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
                data=md.orderobject.objects.filter(user=users,status=True).values()
            elif  request.GET.get('type')== "close":
                data=md.orderobject.objects.filter(user=users,status=False).values()

            
            
                

            
            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)
