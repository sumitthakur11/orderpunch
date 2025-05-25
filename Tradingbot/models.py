from django.db import models
from Tradingbot import utility2
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
exchangelist= {
    'NSE':"NSE",
    'NFO':"NFO",
    'BSE':"BSE",
    'BFO':"BFO",



}

# symbolchoices=utility2.createOrderpunchsymbol()



class Broker(models.Model):
    user= models.IntegerField(null=False,blank=False,default=None)
    updated_at = models.DateTimeField(auto_now=True)
    brokerid = models.AutoField(primary_key=True)
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
    valid=models.BooleanField(blank=True,null=True,default=False)
    websocket= models.BooleanField(blank=True,null=True,default=False)
    nickname= models.CharField(null=True,blank=True,default=None,max_length=100)
    funds= models.CharField(null=True,blank=True,default=None,max_length=100)


    


class orderobject(models.Model):
    user= models.IntegerField(null=False,blank=False,default=None)
    updated_at = models.DateTimeField(auto_now=True)
    orderid=models.CharField(null=True,blank=True,default=None,max_length=200)
    status=models.BooleanField(null=True,blank=True,default=False)
    tradingsymbol= models.TextField(null=True,blank=True,default='')
    symboltoken=models.TextField(null=True,blank=True,default='')
    ordertype=models.TextField(null=True,blank=True,default=None)
    transactiontype=models.TextField(null=True,blank=True,default=None)
    product_type=models.TextField(null=True,blank=True,default=None)
    avg_price=models.FloatField(null=True,blank=True,default=None)
    indexprice=models.TextField(null=True,blank=True,default=None)
    quantity=models.TextField(null=True,blank=True,default=None)    
    exchange=models.TextField(null=True,blank=True,default=None)
    broker= models.CharField(null=True,blank=True,default=None,max_length=100,choices=brokerlist)
    accountnumber= models.CharField(null=True,blank=True,default=None,max_length=100)
    nickname= models.CharField(null=True,blank=True,default='',max_length=100)

    sellorderid=models.CharField(null=True,blank=True,default='',max_length=200)
    side=models.TextField(null=True,blank=True,default=None)
    orderstatus= models.TextField(null=True,blank=True,default='')
    ltp=models.FloatField(null=True,blank=True,default=None)
    lotsize= models.IntegerField(null=True,blank=True,default=None)
    sellorderstatus= models.CharField(null=True,blank=True,default='',max_length=20,choices=statuslist)
    buyorderstatus= models.CharField(null=True,blank=True,default='',max_length=20,choices=statuslist)
    paper= models.BooleanField(null=True,blank=True,default=False)
    pnl=models.FloatField(null=True,blank=True,default=0,editable=False)
    sellprice=models.FloatField(null=True,blank=True,default=0)
    instrument= models.CharField(null=True,blank=True,default='',max_length=100)
    discloseqty= models.CharField(null=True,blank=True,default='',max_length=100)





class globalsymbol(models.Model):
    
    user= models.IntegerField(null=False,blank=False,default=None)
    updated_at = models.DateTimeField(auto_now=True)
    orderpunchsymbol=models.CharField(null=True,blank=True,default=None,max_length=300)
    tradingsymbol=models.CharField(null=True,blank=True,default=None,max_length=200)
    symboltoken=models.CharField(null=True,blank=True,default=None,max_length=200)
    exchange=models.CharField(null=True,blank=True,default=None,max_length=200,choices=exchangelist)



class watchlist(models.Model):
    user= models.IntegerField(null=False,blank=False,default=None)
    updated_at = models.DateTimeField(auto_now=True)
    broker = models.CharField(null=True,blank=True,default=None,max_length=200,choices=brokerlist)
    orderpunchsymbol=models.CharField(null=True,blank=True,default=None,max_length=300)
    tradingsymbol=models.CharField(null=True,blank=True,default=None,max_length=200)
    symnol=models.CharField(null=True,blank=True,default=None,max_length=200)
    symboltoken=models.CharField(null=True,blank=True,default=None,max_length=200)
    exchange=models.CharField(null=True,blank=True,default=None,max_length=200,choices=exchangelist)
    subscribe=models.BooleanField(null=True,blank=True,default=False)
    newevent=models.BooleanField(null=True,blank=True,default=False)
    lotsize=models.CharField(null=True,blank=True,default=None,max_length=200)
    ltp=models.CharField(null=True,blank=True,default=None,max_length=200)
    volume=models.CharField(null=True,blank=True,default=None,max_length=200)
    OI=models.CharField(null=True,blank=True,default=None,max_length=200)
    instrument=models.CharField(null=True,blank=True,default=None,max_length=200)


class Allpositions(models.Model):
    user= models.IntegerField(null=False,blank=False,default=None)
    updated_at = models.DateTimeField(auto_now=True)
    tradingsymbol= models.TextField(null=True,blank=True,default='')
    symboltoken=models.TextField(null=True,blank=True,default='')
    ordertype=models.TextField(null=True,blank=True,default=None)
    transactiontype=models.TextField(null=True,blank=True,default=None)
    producttype=models.TextField(null=True,blank=True,default=None)
    buyavgprice=models.FloatField(null=True,blank=True,default=None)
    indexprice=models.TextField(null=True,blank=True,default=None)
    netqty=models.TextField(null=True,blank=True,default=None)    
    exchange=models.TextField(null=True,blank=True,default=None)
    broker= models.CharField(null=True,blank=True,default=None,max_length=100,choices=brokerlist)
    accountnumber= models.CharField(null=True,blank=True,default=None,max_length=100)
    nickname= models.CharField(null=True,blank=True,default=None,max_length=100)
    ltp=models.FloatField(null=True,blank=True,default=None)
    lotsize= models.IntegerField(null=True,blank=True,default=None)
    sellorderstatus= models.CharField(null=True,blank=True,default=None,max_length=20,choices=statuslist)
    buyorderstatus= models.CharField(null=True,blank=True,default=None,max_length=20,choices=statuslist)
    pnl= models.CharField(null=True,blank=True,default=None,max_length=100)
    realised= models.CharField(null=True,blank=True,default=None,max_length=100)
    unrealised= models.CharField(null=True,blank=True,default=None,max_length=100)
    sellavgprice =models.CharField(null=True,blank=True,default=None,max_length=100)
    instrument= models.CharField(null=True,blank=True,default=None,max_length=100)



    
class allholding(models.Model):
    user= models.IntegerField(null=False,blank=False,default=None)
    updated_at = models.DateTimeField(auto_now=True)
    tradingsymbol= models.TextField(null=True,blank=True,default='')
    symboltoken=models.TextField(null=True,blank=True,default='')
    product=models.TextField(null=True,blank=True,default=None)
    averageprice=models.FloatField(null=True,blank=True,default=None)
    quantity=models.TextField(null=True,blank=True,default=None)    
    exchange=models.TextField(null=True,blank=True,default=None)
    broker= models.CharField(null=True,blank=True,default=None,max_length=100,choices=brokerlist)
    accountnumber= models.CharField(null=True,blank=True,default=None,max_length=100)
    nickname= models.CharField(null=True,blank=True,default=None,max_length=100)
    ltp=models.FloatField(null=True,blank=True,default=None)
    lotsize= models.IntegerField(null=True,blank=True,default=None)
    profitandloss= models.CharField(null=True,blank=True,default=None,max_length=100)
    instrument= models.CharField(null=True,blank=True,default=None,max_length=100)
    pnlpercentage= models.CharField(null=True,blank=True,default=None,max_length=100)
    totalprofitandloss= models.CharField(null=True,blank=True,default=None,max_length=100)
    totalpnlpercentage= models.CharField(null=True,blank=True,default=None,max_length=100)

    
