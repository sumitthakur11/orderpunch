from django.contrib.auth.models import User
from rest_framework import serializers
from . import models as md 


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True, 'allow_null': False}
        }

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        return user
    
class Broker(serializers.ModelSerializer):
    class Meta:
        model = md.Broker
        fields = "__all__"



class orderobject(serializers.ModelSerializer):
    class Meta:
        model = md.orderobject
        fields = "__all__"


class globalsymbol(serializers.ModelSerializer):
    class Meta:
        model = md.globalsymbol
        fields = "__all__"

class watchlist(serializers.ModelSerializer):
    class Meta:
        model = md.watchlist
        fields = "__all__"



class Allpositions(serializers.ModelSerializer):
    class Meta:
        model = md.Allpositions
        fields = "__all__"
class allholding(serializers.ModelSerializer):
    class Meta:
        model = md.allholding

        fields = "__all__"