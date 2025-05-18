from .Brokers import shoonyasdk


def createOrderpunchsymbol():
            exchangelist=['NFO','NSE','BSE','BFO']
            data= dict()

            for i in exchangelist:
                allsym= shoonyasdk.optionchain('',i,'')
                allsym['Symbol']=allsym['Symbol'].str.upper()
                allsym=sorted(set( allsym['Symbol'].str.replace(' ','').to_list()))
                
                data[i]= allsym
            # globalsymbols= dict()
            # for j in data.keys():
            #     globalsymbols['exchange']=j
            #     globalsymbols['symbol']=data[j]

                 
                
                 
            return data
