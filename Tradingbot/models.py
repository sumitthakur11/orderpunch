from django.db import models

# Create your models here.


brokerlist={
    "ANGEL":"ANGEL",
    "SHOONYA":"SHOONYA",
    "DHAN":"DHAN",
    "FYERS":"FYERS",
    "MOTILAL":"MOTILAL",
    "ANANDRATHI":"ANANDRATHI",
    "GROWW":"GROWW",
    "ZERODHA":"ZERODHA",
    "SAMCO":"SAMCO",
    "FLATTRADE":"FLATTRADE",
    "BIGUL":"BIGUL",
    "STOXKART":"STOXKART"

    
}


statuslist = {
    'OPEN':'OPEN',
    'CLOSE':'CLOSE',
    'CANCELED':'CANCELED',
    'PENDING':'PENDING',
    'MODIFIED':'MODIFIED',
    'COMPLETE':'COMPLETE',
}



class Broker(models.Model):
    user= models.IntegerField(null=False,blank=False,default=None)
    updated_at = models.DateTimeField(auto_now=True)
    Username= models.CharField(null=True,blank=True,default=None,max_length=100)
    brokername= models.CharField(null=True,blank=True,default=None,max_length=100,choices=brokerlist)
    accountnumber= models.CharField(null=True,blank=True,default=None,max_length=100)
    active=models.BooleanField(blank=True,null=True,default=False)
    apikey=models.CharField(null=True,blank=True,default=None,max_length=100)
    secretkey= models.CharField(null=True,blank=True,default=None,max_length=100)
    password= models.CharField(null=True,blank=True,default=None,max_length=100)
    vendorcode= models.CharField(null=True,blank=True,default=None,max_length=100)
    imei= models.CharField(null=True,blank=True,default=None,max_length=100)
    AuthToken= models.CharField(null=True,blank=True,default=None,max_length=100)
    value=models.BooleanField(blank=True,null=True,default=False)
    websocket= models.BooleanField(blank=True,null=True,default=False)
    indexscalp= models.BooleanField(blank=True,null=True,default=False)

class orderobject(models.Model):
    user= models.IntegerField(null=False,blank=False,default=None)
    updated_at = models.DateTimeField(auto_now=True)
    buyorderid=models.CharField(null=True,blank=True,default=None,max_length=200)
    status=models.BooleanField(null=True,blank=True,default=False)
    tradingsymbol= models.TextField(null=True,blank=True,default='')
    symboltoken=models.TextField(null=True,blank=True,default='')
    order_type=models.TextField(null=True,blank=True,default=None)
    transactiontype=models.TextField(null=True,blank=True,default=None)
    product_type=models.TextField(null=True,blank=True,default=None)
    avg_price=models.FloatField(null=True,blank=True,default=None)
    indexprice=models.TextField(null=True,blank=True,default=None)
    quantity=models.TextField(null=True,blank=True,default=None)    
    exchange=models.TextField(null=True,blank=True,default=None)
    broker= models.CharField(null=True,blank=True,default=None,max_length=100,choices=brokerlist)
    sellorderid=models.CharField(null=True,blank=True,default=None,max_length=200)
    side=models.TextField(null=True,blank=True,default=None)
    orderstatus= models.TextField(null=True,blank=True,default=None)
    Blockid= models.IntegerField(null=True,blank=True,default=None)
    ltp=models.FloatField(null=True,blank=True,default=None)
    lotsize= models.IntegerField(null=True,blank=True,default=None)
    sellorderstatus= models.CharField(null=True,blank=True,default=None,max_length=20,choices=statuslist)
    buyorderstatus= models.CharField(null=True,blank=True,default=None,max_length=20,choices=statuslist)
    paper= models.BooleanField(null=True,blank=True,default=False)
    pnl=models.FloatField(null=True,blank=True,default=0,editable=False)
    sellprice=models.FloatField(null=True,blank=True,default=0)

