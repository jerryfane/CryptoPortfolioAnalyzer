
# coding: utf-8

# In[650]:


get_ipython().magic('matplotlib inline')
import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy import stats
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime
import json
from bs4 import BeautifulSoup
import requests
import time
import urllib.request
from bs4 import BeautifulSoup
from lxml import html

# define some custom colours
grey = .6, .6, .6


# In[651]:


initial_time = time.time()


# In[652]:


def timestamp2date(timestamp):
    # function converts a Unix timestamp into Gregorian date
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
 
def date2timestamp(date):
    # function coverts Gregorian date in a given format to timestamp
    return datetime.strptime(date_today, '%Y-%m-%d').timestamp()

def get_initial_price(fsym, date):
    f = time.mktime(datetime.datetime.strptime(str(date), "%d/%m/%Y").timetuple())
    o = str(f)
    response = json.loads(requests.get('https://min-api.cryptocompare.com/data/pricehistorical?fsym=' + fsym + '&tsyms=USD,EUR&ts='+ o).text)
    dato = str(response)
    posiniz = dato.find("'USD': ")
    posiniz2 = dato.find(" ",posiniz)
    posfin = dato.find(",",posiniz2)
    c = dato[posiniz2+1:posfin]
    floatc=float(c)
    return floatc

limit = 180
def fetchCryptoClose(fsym, tsym):
    # function fetches the close-price time-series from cryptocompare.com
    # it may ignore USDT coin (due to near-zero pricing)
    # daily sampled
    cols = ['date', 'timestamp', fsym]
    lst = ['time', 'open', 'high', 'low', 'close']
    timestamp_today = datetime.today().timestamp()
    #timestamp_today = datetime.today().timestamp() - 7603200 - 220200 - 1123200 + 86400
    curr_timestamp = timestamp_today
 
    for j in range(2):
        df = pd.DataFrame(columns=cols)
        url = "https://min-api.cryptocompare.com/data/histoday?fsym=" + fsym +               "&tsym=" + tsym + "&toTs=" + str(int(curr_timestamp)) + "&limit=" + str(limit)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        dic = json.loads(soup.prettify())
        for i in range(1, (limit+1)):
            tmp = []
            for e in enumerate(lst):
                x = e[0]
                y = dic['Data'][i][e[1]]
                if(x == 0):
                    tmp.append(str(timestamp2date(y)))
                tmp.append(y)
            if(np.sum(tmp[-4::]) > 0):  # remove for USDT
                tmp = np.array(tmp)
                tmp = tmp[[0,1,4]]  # filter solely for close prices
                df.loc[len(df)] = np.array(tmp)
        # ensure a correct date format
        df.index = pd.to_datetime(df.date, format="%Y-%m-%d")
        df.drop('date', axis=1, inplace=True)
        curr_timestamp = int(df.ix[0][0])
        if(j == 0):
            df0 = df.copy()
        else:
            data = pd.concat([df, df0], axis=0)
    data.drop("timestamp", axis=1, inplace=True)
 
    return data  # DataFrame


# In[653]:


from datetime import datetime
timestamp_today = datetime.today().timestamp()
curr_timestamp = timestamp_today - 7603200 - 220200 - 1123200 + 86400
print(timestamp_today)


# In[654]:


import datetime
print(
    datetime.datetime.fromtimestamp(
        int(timestamp_today)
    ).strftime('%Y-%m-%d %H:%M:%S')
)


# In[655]:


import datetime
print(
    datetime.datetime.fromtimestamp(
        int(curr_timestamp)
    ).strftime('%Y-%m-%d %H:%M:%S')
)


# In[656]:


historical_date = ['20170101', '20170108', '20170115', '20170122', '20170129', '20170205', '20170212', '20170219', '20170226', '20170305', '20170312', '20170319', '20170326', '20170402','20170409', '20170416', '20170423', '20170430', '20170507', '20170514', '20170521', '20170528', '20170604', '20170611', '20170618', '20170625', '20170702', '20170709', '20170716', '20170723', '20170730', '20170806', '20170813', '20170820', '20170827', '20170903', '20170910', '20170917', '20170924', '20171001', '20171008', '20171015', '20171022', '20171029', '20171105', '20171112', '20171119', '20171126', '20171203', '20171210', '20171217', '20171224', '20171231', '20180107', '20180114', '20180121', '20180128', '20180204', '20180211', '20180218', '20180225', '20180304', '20180311', '20180318', '20180325', '20180401', '20180408']


# In[657]:


def get_error_price(fsym, date):
    
    if fsym == 'IOT':
        fsym = 'MIOTA'
    elif fsym == 'XRB':
        fsym = 'NANO'
    elif fsym == 'BCCOIN':
        fsym = 'BCC'
    else:
        pass
        
    quote_date = date[6:10] + date[3:5] + date[0:2]
    quote_page = 'https://coinmarketcap.com/historical/' + quote_date
    page = urllib.request.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    container_box = str(soup.find('tbody'))

    pos_test = container_box.find('<td class="text-left col-symbol">' + fsym )
    #print(pos_test)
    pos_test2 = (container_box[pos_test:].find('<a class="price"'))
    #print(pos_test2)
    pos_test3 = (container_box[pos_test+pos_test2:].find('data-usd="'))
    #print(pos_test3)
    pos_test4 = (container_box[pos_test+pos_test2+pos_test3+10:].find('"'))
    #print(pos_test4)
    error_price = container_box[pos_test+pos_test2+pos_test3+10:pos_test+pos_test2+pos_test3+10+pos_test4]
    error_price_float = float(error_price)
    return error_price_float


# In[658]:


def get_coin_value(fsymnum, fsym):
    values = []
    #for date in dates_list:
    for i, date in enumerate(dates_list_reversed):
        try:
            index = get_data_index(fsymnum, i)
            price = data[fsym][index]
            value = amount[fsymnum] * price
            print('indexing done')
            if str(price) == 'nan':
                print('data = nan, refetching...')
                price = get_initial_price(fsym, date)
                value = amount[fsymnum] * price
                if price == 0:
                    print('data = nan & 0, refetching...')
                    try:
                        price = get_error_price(fsym, histoday_dic.get(dates_list_reversed[(i)]))
                        value = amount[fsymnum] * price
                    except:
                        print('error, check the code: "get_coin_value"') 
                else:
                    pass
            else:
                pass
        except:
            print('cant get data index, refetching...')
            price = get_initial_price(fsym, date)
            value = amount[fsymnum] * price
            if price == 0:
                print('data = nan & 0, refetching...')
                try:
                    price = get_error_price(fsym, histoday_dic.get(dates_list_reversed[(i)]))
                    value = amount[fsymnum] * price
                except:
                    print('error, check the code: "get_coin_value"') 
            else:
                pass            
        values.append(value)
    return values 


# In[659]:


def get_coin_value_per_histoday_real(fsymnum, fsym, monthnum):
    values = []
    #for date in dates_list:
    for date in dates_list_reversed:
        value = amount_per_histoday[monthnum][fsymnum] * get_initial_price(fsym, date)
        values.append(value)
    return values 


# In[660]:


def get_coin_value_per_histoday_raw(fsymnum, fsym, monthnum):
    values = []
    #for date in dates_list:
    for i, date in enumerate(dates_list_reversed):
        try:
            index = get_data_index(fsymnum, i)
            price = data[fsym][index]
            value = amount_per_histoday[monthnum][fsymnum] * price
            values.append(value)
            if str(price) == 'nan':
                value = amount_per_histoday[monthnum][fsymnum] * get_initial_price(fsym, date)
                values.append(value)
            else:
                pass
        except:
            value = amount_per_histoday[monthnum][fsymnum] * get_initial_price(fsym, date)
            values.append(value)
    return values 


# In[661]:


def get_coin_value_per_histoday_old(fsymnum, fsym, monthnum):
    values = []
    #for date in dates_list:
    for i, date in enumerate(dates_list_reversed):
        try:
            index = get_data_index(fsymnum, i)
            price = data[fsym][index]
            value = amount_per_histoday[monthnum][fsymnum] * price
            print('indexing done',  date, i, fsymnum, fsym, monthnum)
            if str(price) == 'nan':
                print('data = nan, refetching...',  date, i, fsymnum, fsym, monthnum)
                price = get_initial_price(fsym, date)
                value = amount_per_histoday[monthnum][fsymnum] * price
                if price == 0:
                    print('data = nan & 0, refetching...',  date, i, fsymnum, fsym, monthnum)
                    #try:
                    price = get_error_price(fsym, histoday_dic.get(date))
                    value = amount_per_histoday[monthnum][fsymnum] * price
                   # except:
                    #    print('error, check the code: "get_coin_value_per_histoday", date:', date, i, fsymnum, fsym, monthnum) 
                else:
                    pass
            else:
                pass
        except:
            print('cant get data index, refetching...',  date, i, fsymnum, fsym, monthnum)
            price = get_initial_price(fsym, date)
            value = amount_per_histoday[monthnum][fsymnum] * price
            if price == 0:
                print('data = 0, refetching...',  date, i, fsymnum, fsym, monthnum)
                error_counter = 1
                try:
                    time.sleep(2)
                    price = get_error_price(fsym, histoday_dic.get(dates_list_reversed[i+error_counter]))
                    value = amount_per_histoday[monthnum][fsymnum] * price
                    print('Coin isnt available in coinmarketcap in this date, fetched data from next date', error_counter)
                except:
                    error_counter = error_counter + 1
                    try:
                        price = get_error_price(fsym, histoday_dic.get(dates_list_reversed[i+error_counter]))
                        value = amount_per_histoday[monthnum][fsymnum] * price
                        print('Coin isnt available in coinmarketcap in this date, fetched data from next date', error_counter)
                    except:
                        error_counter = error_counter + 1
                        try:
                            price = get_error_price(fsym, histoday_dic.get(dates_list_reversed[i+error_counter]))
                            value = amount_per_histoday[monthnum][fsymnum] * price
                            print('Coin isnt available in coinmarketcap in this date, fetched data from next date', error_counter)       
                        except:
                            error_counter = error_counter + 1
                            price = 0
                            value = amount_per_histoday[monthnum][fsymnum] * price
                            print('Coin isnt available in coinmarketcap in this date, ASSUMING PRICE IS 0')
    #print('error, check the code: "get_coin_value_per_histoday", date:', date, i, fsymnum, fsym, monthnum) 
            else:
                pass
        values.append(value)
    return values 


# In[662]:


def get_coin_value_per_histoday(fsymnum, fsym, monthnum):
    values = []
    
    
    #for date in dates_list:
    for i, date in enumerate(dates_list_reversed):
        try:
            index = get_data_index(fsymnum, i)
            price = data[fsym][index]
            value = amount_per_histoday[monthnum][fsymnum] * price
            print('indexing done',  date, i, fsymnum, fsym, monthnum)
            if str(price) == 'nan':
                print('data = nan, refetching...',  date, i, fsymnum, fsym, monthnum)
                price = get_initial_price(fsym, date)
                value = amount_per_histoday[monthnum][fsymnum] * price
                if price == 0:
                    if fsym == 'IOT':
                        fsym = 'MIOTA'
                    elif fsym == 'XRB':
                        fsym = 'NANO'
                    elif fsym == 'BCCOIN':
                        fsym = 'BCC'
                    else:
                        pass
                    print('data = nan & 0, refetching...',  date, i, fsymnum, fsym, monthnum)
                    price = get_error_price(fsymR, histoday_dic.get(date))
                    value = amount_per_histoday[monthnum][fsymnum] * price
                else:
                    pass
            else:
                pass
        except:
            
            if fsym == 'MIOTA':
                fsym = 'IOT'
            elif fsym == 'NANO':
                fsym = 'XRB'
            elif fsym == 'BCC':
                fsym = 'BCCOIN'
            else:
                pass
            
            print('cant get data index, refetching...',  date, i, fsymnum, fsym, monthnum)
            price = get_initial_price(fsym, date)
            value = amount_per_histoday[monthnum][fsymnum] * price
            if price == 0:
                if fsym == 'IOT':
                    fsym = 'MIOTA'
                elif fsym == 'XRB':
                    fsym = 'NANO'
                elif fsym == 'BCCOIN':
                    fsym = 'BCC'
                else:
                    pass
                print('data = 0, refetching...',  date, i, fsymnum, fsym, monthnum)
                error_counter = 1
                try:
                    time.sleep(2)
                    price = get_error_price(fsym, histoday_dic.get(dates_list_reversed[i+error_counter]))
                    value = amount_per_histoday[monthnum][fsymnum] * price
                    print('Coin isnt available in coinmarketcap in this date, fetched data from next date', error_counter)
                except:
                    error_counter = error_counter + 1
                    try:
                        price = get_error_price(fsym, histoday_dic.get(dates_list_reversed[i+error_counter]))
                        value = amount_per_histoday[monthnum][fsymnum] * price
                        print('Coin isnt available in coinmarketcap in this date, fetched data from next date', error_counter)
                    except:
                        error_counter = error_counter + 1
                        try:
                            price = get_error_price(fsym, histoday_dic.get(dates_list_reversed[i+error_counter]))
                            value = amount_per_histoday[monthnum][fsymnum] * price
                            print('Coin isnt available in coinmarketcap in this date, fetched data from next date', error_counter)       
                        except:
                            error_counter = error_counter + 1
                            price = 0
                            value = amount_per_histoday[monthnum][fsymnum] * price
                            print('Coin isnt available in coinmarketcap in this date, ASSUMING PRICE IS 0')
            #print('error, check the code: "get_coin_value_per_histoday", date:', date, i, fsymnum, fsym, monthnum) 
            else:
                pass
        values.append(value)
    return values 


# In[663]:


def get_coin_error_value(fsymnum, fsym):
    values = []
    #for date in dates_list:
    for date in dates_list_reversed:
        value = amount[fsymnum] * get_error_price(fsym, histoday_dic.get(date))
        values.append(value)
    return values 


# In[664]:


def get_coin_error_value_per_histoday(fsymnum, fsym, monthnum):
    values = []
    #for date in dates_list:
    for date in dates_list_reversed:
        value = amount_per_histoday[monthnum][fsymnum] * get_error_price(fsym, histoday_dic.get(date))
        values.append(value)
    return values 


# In[665]:


def get_fsym_in_date(datehisto):
    quote_page = 'https://coinmarketcap.com/historical/' + datehisto
    page = urllib.request.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    container_box = str(soup.find('tbody'))
    
    #MODIFICARE IL NUMERO DI FSYM, cioé numfsym
    numfsym = 20
    counter = 0
    pos_list = []
    container_box_list = [0]
    counter_list = []
    fsym_list = []
    while counter < numfsym:
        if counter == 0:
            pos1 = container_box.find('tr class="" id="id-')
            x = container_box[pos1+19:]
            pos2 = x.find('">')
            y = x[:pos2]
            #print(counter, y)
            counter_list.append(counter)
            counter = counter + 1
            pos_list.append(pos1)
            pos_list.append(pos2)
            container_box_list.append(x)
            fsym_list.append(y)
        else:
            z = container_box_list[counter][pos_list[counter]:]
            pos3 = z.find('tr class="" id="id-')
            w = z[pos3+19:]
            pos4 = w.find('">')
            u = w[:pos4]
            #print(counter, u)
            counter_list.append(counter)
            counter = counter + 1
            pos_list.append(pos3)
            pos_list.append(pos4)
            container_box_list.append(w)
            fsym_list.append(u)
            
    page = requests.get(quote_page)
    tree = html.fromstring(page.content)
    fsym = []

    for i in counter_list:
        coin_symbol = str(tree.xpath('//*[@id="id-' + fsym_list[i] + '"]/td[3]/text()'))[2:-2]
        fsym.append(coin_symbol) 
            
    return fsym


# In[666]:


def get_data_index(fsym, date):
    D = datesdic.get(date)
    Newdates = D[6:] + '-' + D[3:5] + '-' + D[:2]
    for i in range(0, len(data[count_fsym_dic.get(fsym)])):
        if (str(data[count_fsym_dic.get(fsym)].index[i]))[:10] == Newdates:
            #print(i)
            index = i
        else:
            pass
    return index


# In[667]:


def remove(glist):
    seen = set()
    def unseen():
        for val in glist:
            if not val in seen:
                yield val
                seen.add(val)
    glist[:] = unseen()
    return glist # if you must


# In[668]:


histodaycounts = []
histocount = 0
for i in historical_date:
    histodaycounts.append (histocount)
    histocount = histocount + 1
#print(histodaycounts)


# In[669]:


historical_date_list = []
for i in histodaycounts:
    histoday = historical_date[i][-2:] + '/' + historical_date[i][4:6] + '/' + historical_date[i][:4]
    historical_date_list.append(histoday)
#print(historical_date_list)


# In[670]:


import datetime
X = datetime.datetime.now() - datetime.timedelta(days = (2 * limit) - 2)
Z = str(X)
initialdate = Z[8:10] + '/' + Z[5:7] + '/' + Z[:4]
print('initialdate is', initialdate)


# In[671]:


#import datetime
#var = datetime.datetime.now().day + ((datetime.datetime.now().month)-1)*30 + 364
#var1 = datetime.datetime.now().day + ((datetime.datetime.now().month)-1)*30 -1
##print(var1)
#X = datetime.datetime.now() - datetime.timedelta(days = var)
#Y = datetime.datetime.now() - datetime.timedelta(days = var1)
#print(Y)
#Z = str(X)
#initialdate = Z[8:10] + '/' + Z[5:7] + '/' + Z[:4]
#print('initialdate is', initialdate)


# In[673]:


import datetime

weeks = int(limit/7)
today = datetime.date.today()

datelist = {}
for dates in datelist:
    dates == initialdate
    if dates < today:
        dates == dates + 7
    else:
        null
    datelist.append(dates)


# In[674]:


numdays = (limit + 1) * 2 -1
base = datetime.datetime.today() 
#base = Y
print(base)
datelist = [base - datetime.timedelta(days=x) for x in range(0, numdays)]

nummonths = (int(numdays / 31)) + 1
#print(nummonths)

monthlist = []
monthlist.append(0)
months = 0
months_list = []

while months < nummonths:
    months = months + 1
    monthlist.append(months)
#print(monthlist)

print('There are', nummonths, 'months')

dates = []
for i in monthlist:
    a = i * 31
    dates.append(a)
if dates[-1] > (numdays-1):
    dates[-1] = numdays - 3
else:
    null
#print(dates)

dates_list = []
for date in dates:
    a = datelist[date].strftime("%d/%m/%Y")
    dates_list.append(a)
#print(dates_list)

dates_list_reversed = dates_list[::-1]


# In[675]:


print(dates_list_reversed)


# In[676]:


histoday_per_dates_list = []
histoday_per_dates_list_real_raw = []
for k in monthlist:
    provacount = 0
    for i in historical_date_list:  
        if time.strptime(i, "%d/%m/%Y") < time.strptime(dates_list_reversed[k], "%d/%m/%Y"):
            provacount = provacount + 1
            pass
        else:
            #print(provacount)
            histoday_per_dates_list.append(historical_date[provacount-1])
            histoday_per_dates_list_real_raw.append(historical_date_list[provacount-1])   
            break
if time.strptime(historical_date_list[-1], "%d/%m/%Y") < time.strptime(dates_list_reversed[-1], "%d/%m/%Y"):
    histoday_per_dates_list.append(historical_date[-1])
    histoday_per_dates_list_real_raw.append(historical_date_list[-1])
else:
    pass
               
#print(histoday_per_dates_list)
#print(histoday_per_dates_list_real_raw)


# In[677]:


from datetime import datetime
histoday_per_dates_list_real = []

#index = historical_date_list.index(histoday_per_dates_list_real_raw[0])
#print(index)
#print(historical_date_list[index+1])
indexcount = 0

for i in monthlist:
    index = historical_date_list.index(histoday_per_dates_list_real_raw[i])
    try:
        if abs(datetime.strptime(histoday_per_dates_list_real_raw[i], "%d/%m/%Y") - datetime.strptime(dates_list_reversed[i], "%d/%m/%Y")) < abs(datetime.strptime(historical_date_list[index+1], "%d/%m/%Y") - datetime.strptime(dates_list_reversed[i], "%d/%m/%Y")):
            histoday_per_dates_list_real.append(histoday_per_dates_list_real_raw[i])
        else:
            histoday_per_dates_list_real.append(historical_date_list[index+1])
    except: 
        if abs(datetime.strptime(histoday_per_dates_list_real_raw[i], "%d/%m/%Y") - datetime.strptime(dates_list_reversed[i], "%d/%m/%Y")) < abs(datetime.strptime(historical_date_list[index], "%d/%m/%Y") - datetime.strptime(dates_list_reversed[i], "%d/%m/%Y")):
            histoday_per_dates_list_real.append(histoday_per_dates_list_real_raw[i])
        else:
            histoday_per_dates_list_real.append(historical_date_list[index]) 

#print(histoday_per_dates_list_real)


# In[678]:


print(histoday_per_dates_list_real)


# In[679]:


histoday_dic = dict(zip(dates_list_reversed, histoday_per_dates_list_real))


# In[680]:


print(histoday_dic)


# In[681]:


histoday_per_dates_list_real_mkt = []


for i in monthlist:
    x = histoday_per_dates_list_real[i][6:11] + histoday_per_dates_list_real[i][3:5] + histoday_per_dates_list_real[i][:2]
    histoday_per_dates_list_real_mkt.append(x)

#print(histoday_per_dates_list_real_mkt)


# In[682]:


initialdate_raw = initialdate[6:] + initialdate[3:5] + initialdate[:2]


# In[683]:


fsym = get_fsym_in_date(histoday_per_dates_list_real_mkt[0])
print('fsym in initialdate are', fsym)


# In[684]:


for n, i in enumerate(fsym):
    if i == 'MIOTA':
        fsym[n] = 'IOT'
    else:
        pass
for n, i in enumerate(fsym):
    if i == 'BCC':
        fsym[n] = 'BCCOIN'
    else:
        pass
for n, i in enumerate(fsym):
    if i == 'NANO':
        fsym[n] = 'XRB'
    else:
        pass
print(fsym)


# In[685]:


fsym_list_per_histoday = []
COUNTSS = 0
print('fsym_list_per_histoday loading:')
for i in monthlist: 
    x = get_fsym_in_date(histoday_per_dates_list_real_mkt[i])
    fsym_list_per_histoday.append(x)
    print(COUNTSS, 'of', monthlist[-1])
    COUNTSS = COUNTSS + 1
#print(fsym_list_per_histoday)


# In[686]:


fsym_dic_per_histoday = dict(zip(histoday_per_dates_list_real, fsym_list_per_histoday))
print('Fsym before each rebalance date are:', fsym_dic_per_histoday)


# In[687]:


count = []
count.append(0)
a = 0
for i in fsym:
    a = a + 1
    count.append(a) 
count = count[:-1]
#print(count)

# vs. 
tsym = 'USD'

count_fsym_dic = dict(zip(count, fsym))
#print(count_fsym_dic)


# In[688]:


fsym_list_total = []
for k in monthlist:
    for i in count:
        fsym_list_total.append(fsym_list_per_histoday[k][i])
#print(fsym_list_total)


# In[689]:


fsym_total = remove(fsym_list_total)


# In[690]:


for n, i in enumerate(fsym_total):
    if i == 'MIOTA':
        fsym_total[n] = 'IOT'
    else:
        pass

for n, i in enumerate(fsym_total):
    if i == 'BCC':
        fsym_total[n] = 'BCCOIN'
    else:
        pass
    
for n, i in enumerate(fsym_total):
    if i == 'NANO':
        fsym_total[n] = 'XRB'
    else:
        pass


# In[691]:


COUNTSSS = 0
COUNT = []
for i in fsym_total:
    COUNT.append(COUNTSSS)
    COUNTSSS = COUNTSSS + 1
#print(COUNT)

count_fsym_total_dic = dict(zip(COUNT, fsym_total))
print(count_fsym_total_dic)


# In[692]:


fsym_unit_counter = int(len(fsym_total) / 3)
fsym_total_unit = int(len(fsym_total) / fsym_unit_counter)
#fsym_total_unit = int(len(fsym_total) / 6)
print(fsym_unit_counter)
print(fsym_total_unit)


# In[696]:


datas = []
fsym_Counter = 0
from datetime import datetime
for f in range(0, fsym_unit_counter):
#for f in range(0, fsym_unit_counter+1):
    if f == 0:
        for e in enumerate(fsym_total[:fsym_total_unit]):
            print(fsym_Counter, e[1])
            fsym_Counter = fsym_Counter + 1
            if (e[0] == 0):
                data1 = fetchCryptoClose(e[1], tsym)
            else:
                data1 = data1.join(fetchCryptoClose(e[1], tsym))
        data1 = data1.astype(float)
        datas.append(data1)
    elif f == (fsym_unit_counter):
    #elif f == (fsym_unit_counter+1):
        for e in enumerate(fsym_total[(f-1)*(fsym_unit_counter):]):
        #for e in enumerate(fsym_total[(f-1)*(fsym_unit_counter+1):]):
            print(fsym_Counter, e[1])
            fsym_Counter = fsym_Counter + 1
            if (e[0] == 0):
                data = fetchCryptoClose(e[1], tsym)
            else:
                data1 = data1 = data1.join(fetchCryptoClose(e[1], tsym))
            data1 = data1.astype(float)
            datas.append(data1)
    else:
        for e in enumerate(fsym_total[f*fsym_total_unit:(f+1)*fsym_total_unit]):
            print(fsym_Counter, e[1])
            fsym_Counter = fsym_Counter + 1
            if (e[0] == 0):
                data1 = fetchCryptoClose(e[1], tsym)
            else:
                data1 = data1.join(fetchCryptoClose(e[1], tsym))
        data1 = data1.astype(float)
        datas.append(data1)  


# In[697]:


dfs = []
for i in range(0, len(datas)):
    deleting_list = []
    data = datas[i]
    print('datas', len(datas[i]))
    for k in range(0, len(data)):
        if k == (len(data)-1):
            pass
        else:
            if data.iloc[k].name == data.iloc[k+1].name:
                deleting_list.append(k)
            else:
                pass
    data = data.drop(data.iloc[deleting_list[0]:deleting_list[-1]].index)
    dfs.append(data)


# In[698]:


for i in range(0, len(dfs)):
    if i == 0:
        data = dfs[i]
    else:
        data = data.join(dfs[i])


# In[699]:


print(data)


# In[700]:


if (data.columns[-1]) == fsym_total[-1]:
    print('TUTTO OK')
else:
    print('RIVEDERE I CODICI, in particolare nel codice in cui si raccolgono i dati con gli fsym, mettere invece che "fsym_unit_counter", "fsym_unit_counter+1"')


# In[701]:


#for i in range(0, len(datas)):
#    if i == 0:
#        deleting_list = []
#        data = datas[i]
#        print('datas', len(datas[i]))
#        print('data', len(data))
#        for k in range(0, len(data)):
#            if k == (len(data)-1):
#                pass
#            else:
#                if data.iloc[k].name == data.iloc[k+1].name:
#                    deleting_list.append(k)
#                else:
#                    pass
#        data = data.drop(data.iloc[deleting_list[0]:deleting_list[-1]].index)
#    else:
#        deleting_list = []
#        data = data.join(datas[i])
#        print('datas', len(datas[i]))
#        print('data', len(data))
#        for k in range(0, len(data)):
#            if k == (len(data)-1):
#                pass
#            else:
#                if data.iloc[k].name == data.iloc[k+1].name:
#                    deleting_list.append(k)
#                else:
#                    pass
#        data = data.drop(data.iloc[deleting_list[0]:deleting_list[-1]].index)


# In[702]:


#deleting_list = []
#for k in range(0, len(data)):
#    if k == (len(data)-1):
#        pass
#    else:
#        if data.iloc[k].name == data.iloc[k+1].name:
#            #print('yes', k)
 #           deleting_list.append(k)
 #       else:
 #           #print('no', k)
 #           pass
#data = data.drop(data.iloc[deleting_list[0]:deleting_list[-1]].index)


# In[704]:


#from datetime import datetime
#for e in enumerate(fsym_total[:fsym_total_unit]):
#    print(e[0], e[1])
#    if(e[0] == 0):
#        data1 = fetchCryptoClose(e[1], tsym)
#    else:
#        data1 = data1.join(fetchCryptoClose(e[1], tsym))
# 
#data1 = data1.astype(float) # ensure values to be floats
# 
## save portfolio to a file (HDF5 file format)
#store = pd.HDFStore('portfolio1.h5')
#store['data1'] = data1
#store.close()
# 
# read in your portfolio from a file
#df1 = pd.read_hdf('portfolio1.h5', 'data1')
#print(df1)


# In[705]:


#deleting_list = []
#for k in range(0, len(data1)):
#    if k == (len(data1)-1):
#        pass
#    else:
#        if data1.iloc[k].name == data1.iloc[k+1].name:
#            #print('yes', k)
#            deleting_list.append(k)
#        else:
#            #print('no', k)
#            pass
#data1 = data1.drop(data1.iloc[deleting_list[0]:deleting_list[-1]].index)


# In[706]:


#from datetime import datetime
#for e in enumerate(fsym_total[fsym_total_unit:2*fsym_total_unit]):
#    print(e[0], e[1])
#    if(e[0] == 0):
#        data2 = fetchCryptoClose(e[1], tsym)
#    else:
#        data2 = data2.join(fetchCryptoClose(e[1], tsym))
#    #data = data.join(fetchCryptoClose(e[1], tsym))
#data2 = data2.astype(float) # ensure values to be floats
# 
## save portfolio to a file (HDF5 file format)
#store = pd.HDFStore('portfolio2.h5')
#store['data2'] = data2
#store.close()
# 
## read in your portfolio from a file
#df2 = pd.read_hdf('portfolio2.h5', 'data2')
#print(df2)


# In[707]:


#deleting_list = []
#for k in range(0, len(data2)):
#    if k == (len(data2)-1):
#        pass
#    else:
#        if data2.iloc[k].name == data2.iloc[k+1].name:
#            #print('yes', k)
#            deleting_list.append(k)
#        else:
#            #print('no', k)
#            pass
#data2 = data2.drop(data2.iloc[deleting_list[0]:deleting_list[-1]].index)


# In[708]:


#data = data1.join(data2)


# In[709]:


#from datetime import datetime
#for e in enumerate(fsym_total[2*fsym_total_unit:3*fsym_total_unit]):
#    print(e[0], e[1])
#    if(e[0] == 0):
#        data3 = fetchCryptoClose(e[1], tsym)
#    else:
#        data3 = data3.join(fetchCryptoClose(e[1], tsym))
#    #data = data.join(fetchCryptoClose(e[1], tsym))
#data3 = data3.astype(float) # ensure values to be floats
# 
## save portfolio to a file (HDF5 file format)
#store = pd.HDFStore('portfolio3.h5')
#store['data3'] = data3
#store.close()
# 
## read in your portfolio from a file
#df3 = pd.read_hdf('portfolio3.h5', 'data3')
#print(df3)


# In[710]:


#deleting_list = []
#for k in range(0, len(data3)):
#    if k == (len(data3)-1):
#        pass
#    else:
#        if data3.iloc[k].name == data3.iloc[k+1].name:
#            #print('yes', k)
#            deleting_list.append(k)
#        else:
#            #print('no', k)
#            pass
#data3 = data3.drop(data3.iloc[deleting_list[0]:deleting_list[-1]].index)


# In[711]:


#data = data.join(data3)


# In[712]:


store = pd.HDFStore('portfolio.h5')
store['data'] = data
store.close()
 
# read in your portfolio from a file
df = pd.read_hdf('portfolio.h5', 'data')
#print(df)


# In[713]:


print(histoday_dic)


# In[714]:


datesdic = dict(zip(monthlist, dates_list_reversed))


# In[722]:


initialdate = dates_list_reversed[0]


# In[723]:


import datetime
coininitialprice = []
for i, coin in enumerate(fsym):
    try:
        index = get_data_index(i, 0)
        coinname = data[coin][index]
        if str(coinname) == 'nan':
            coinname = get_initial_price(coin, initialdate)
            if coinname == 0:
                coinname = get_error_price(coin, histoday_dic.get(initialdate))
            else:
                pass
        else:
            pass
    except:
        print("can't get data index, refetching...")
        coinname = get_initial_price(coin, initialdate)
        if coinname == 0:
            coinname = get_error_price(coin, histoday_dic.get(initialdate))
        else:
            pass        
    coininitialprice.append(coinname)

for i in count:
    print(fsym[i] + ' starting price is ', coininitialprice[i])


# In[724]:


print(histoday_dic.get(initialdate))
print(histoday_dic)


# In[725]:


#import datetime
#coininitialprice = []
#for coin in fsym:
#    coinname = get_initial_price(coin, initialdate)
#    if coinname == 0:
#        coinname = get_error_price(coin, histoday_dic.get(initialdate))
#    else:
#        pass
#    coininitialprice.append(coinname)

#for i in count:
#    print(fsym[i] + ' starting price is ', coininitialprice[i])


# In[726]:


for i in enumerate(fsym_list_per_histoday):
    for e in enumerate(fsym_list_per_histoday[i[0]]):
        if e[1] == 'MIOTA':
        #if fsym_list_per_histoday[i[0]][e[0]] == 'MIOTA':
            fsym_list_per_histoday[i[0]][e[0]] = 'IOT'
        else:
            pass
for i in enumerate(fsym_list_per_histoday):
    for e in enumerate(fsym_list_per_histoday[i[0]]):
        if e[1] == 'NANO':
        #if fsym_list_per_histoday[i[0]][e[0]] == 'MIOTA':
            fsym_list_per_histoday[i[0]][e[0]] = 'XRB'
        else:
            pass
for i in enumerate(fsym_list_per_histoday):
    for e in enumerate(fsym_list_per_histoday[i[0]]):
        if e[1] == 'BCC':
        #if fsym_list_per_histoday[i[0]][e[0]] == 'MIOTA':
            fsym_list_per_histoday[i[0]][e[0]] = 'BCCOIN'
        else:
            pass


# In[727]:


#for e in enumerate(fsym_list_per_histoday):
#    for i in enumerate(fsym_list_per_histoday[e[0]]):
#        try:
#            t = get_error_price(fsym_list_per_histoday[e[0]][i[0]], dates_list_reversed[e[0]])
#        except:
#            print(e[0], i[0])


# In[728]:


import datetime
#non sono specificati gli fsym, ma dipendono dalla classifica, cioé da quelli presenti in 'fsym_list_per_histoday' in base agli histoday
coininitialprice_per_histoday = []
print('coininitialprice_per_histoday loading:')
for e in enumerate(fsym_list_per_histoday):
    lista = []
    for i in enumerate(fsym_list_per_histoday[e[0]]):
        try:
            index = get_data_index(i[0], e[0])
            print(index, i[0], i[1], e[0])
            t = data[i[1]][index]
            if str(t) == 'nan':
                print('data = nan, refetching...')
                t = get_initial_price(fsym_list_per_histoday[e[0]][i[0]], dates_list_reversed[e[0]]) 
                if t == 0:
                    try:
                        print('data = nan & 0, refetching...')
                        t = get_error_price(fsym_list_per_histoday[e[0]][i[0]], histoday_dic.get(dates_list_reversed[(e[0])]))
                    except:
                        print('error', e[0], i[0], i[1])
                else:
                    pass
            else:
                pass
        except:
            print('cant get index, refetching...')
            t = get_initial_price(fsym_list_per_histoday[e[0]][i[0]], dates_list_reversed[e[0]]) 
            if t == 0:
                try:
                    print('data = 0, refetching...')
                    t = get_error_price(fsym_list_per_histoday[e[0]][i[0]], histoday_dic.get(dates_list_reversed[(e[0])]))
                except:
                    print('error', e[0], i[0], i[1])
            else:
                 pass            
        lista.append(t)
    coininitialprice_per_histoday.append(lista)
    print(e[0], 'of', monthlist[-1])


# In[729]:


count_fsym_dic = dict(zip(count, fsym))


# In[730]:


#ES: pricecoin[0] = (data.BTC - coininitialprice[0]) / coininitialprice[0]

pricecoin = []
#for i in count:
#    if fsym_total.index(count_fsym_dic.get(i)) < (fsym_total_unit):
#        pricecoin.append(start)
#    elif fsym_total.index(count_fsym_dic.get(i)) < (2 * fsym_total_unit):
#        start = ((eval('data2.' + count_fsym_dic.get(i)) - coininitialprice[i]) / coininitialprice[i])
#        pricecoin.append(start)
#    else:
#        start = ((eval('data3.' + count_fsym_dic.get(i)) - coininitialprice[i]) / coininitialprice[i])
#        pricecoin.append(start)       

for i in count:
    #start = ((eval('data.' + count_fsym_dic.get(i)) - coininitialprice[i]) / coininitialprice[i])
    start = ((data[count_fsym_dic.get(i)] - coininitialprice[i]) / coininitialprice[i])
    pricecoin.append(start)       
        
equalweight = 1/len(fsym)

priceportfolio = []
for i in count:
    a = equalweight * pricecoin[i]
    priceportfolio.append(a)

    
#Mi sembra inutile(?)
priceportfolio_sum = []
for i in count:
    a = sum(priceportfolio[i])
    priceportfolio_sum.append(a)


# In[731]:


dflist_test = []
for i in monthlist:
    x = []
    for group in eval("data['BTC'].groupby([(df.index.year),(df.index.month)])"):
        x.append(group[1])
    dflist_test.append(x) 


# In[732]:


#non sono specificati gli fsym, ma dipendono dalla classifica, cioé da quelli presenti in 'fsym_list_per_histoday' in base agli histoday
pricecoin_per_histoday = []
#for e in enumerate(coininitialprice_per_histoday):
#    lista = []
#    for i in enumerate(coininitialprice_per_histoday[e[0]]):
#        if fsym_total.index(fsym_list_per_histoday[e[0]][i[0]]) < (fsym_total_unit):
#            Start = ((eval('data1.' + fsym_list_per_histoday[e[0]][i[0]]) - coininitialprice_per_histoday[e[0]][i[0]]) / coininitialprice_per_histoday[e[0]][i[0]])
#            lista.append(Start)
#        elif fsym_total.index(fsym_list_per_histoday[e[0]][i[0]]) < (2*fsym_total_unit):
#            Start = ((eval('data2.' + fsym_list_per_histoday[e[0]][i[0]]) - coininitialprice_per_histoday[e[0]][i[0]]) / coininitialprice_per_histoday[e[0]][i[0]])
#            lista.append(Start)
#        else:
#            Start = ((eval('data3.' + fsym_list_per_histoday[e[0]][i[0]]) - coininitialprice_per_histoday[e[0]][i[0]]) / coininitialprice_per_histoday[e[0]][i[0]])
#            lista.append(Start)
#    pricecoin_per_histoday.append(lista)
##print(pricecoin_per_histoday)

for e in enumerate(coininitialprice_per_histoday):
    lista = []
    for i in enumerate(coininitialprice_per_histoday[e[0]]):
        Start = (((data[fsym_list_per_histoday[e[0]][i[0]]]) - coininitialprice_per_histoday[e[0]][i[0]]) / coininitialprice_per_histoday[e[0]][i[0]])
        lista.append(Start)
    pricecoin_per_histoday.append(lista)
        



priceportfolio_per_histoday = []
for e in enumerate(coininitialprice_per_histoday):
    lista = []
    for i in enumerate(coininitialprice_per_histoday[e[0]]):
        A = equalweight * pricecoin_per_histoday[e[0]][i[0]]
        lista.append(A)
    priceportfolio_per_histoday.append(lista)
#print(priceportfolio_per_histoday[0])

priceportfolio_sum_per_histoday = []
for e in enumerate(coininitialprice_per_histoday):
    lista = []
    for i in enumerate(coininitialprice_per_histoday[e[0]]):
        A = sum(priceportfolio_per_histoday[e[0]][i[0]])
        lista.append(A)
    priceportfolio_sum_per_histoday.append(lista)
#print(priceportfolio_sum_per_histoday)


# In[733]:


for e in enumerate(coininitialprice_per_histoday):
    lista = []
    for i in enumerate(coininitialprice_per_histoday[e[0]]):
        Start = coininitialprice_per_histoday[e[0]][i[0]]
        break


# In[734]:


startinginvestment = 1
amount = []
leng = len(fsym)

for i in count:
    a = (startinginvestment / leng) / coininitialprice[i]
    amount.append(a)

amountdict = dict(zip(fsym, amount))
print('Your portfolio amount is :', amountdict)


# In[735]:


#non sono specificati gli fsym, ma dipendono dalla classifica, cioé da quelli presenti in 'fsym_list_per_histoday' in base agli histoday
amount_per_histoday = []
print('amount_per_histoday loading:')
for e in enumerate(coininitialprice_per_histoday):
    lista = []
    for i in enumerate(coininitialprice_per_histoday[e[0]]):
        if coininitialprice_per_histoday[e[0]][i[0]] != 0:
            Amount = (startinginvestment / leng) / coininitialprice_per_histoday[e[0]][i[0]]
        else:
            price = get_error_price(fsym_list_per_histoday[e[0]][i[0]], histoday_dic.get(dates_list_reversed[(e[0])]))
            Amount = ((startinginvestment / leng) / price)
            print('refetching price for:', e[0], i[0], i[1], price, coininitialprice_per_histoday[e[0]][i[0]], fsym_list_per_histoday[e[0]][i[0]])
        lista.append(Amount)
    amount_per_histoday.append(lista)
#print(amount_per_histoday)
print('done')


# In[736]:


value = []
#for i in count:
#    if fsym_total.index(count_fsym_dic.get(i)) < (fsym_total_unit):
#        a = amount[i] * eval('data1.' + count_fsym_dic[i])
#        value.append(a)
#    elif fsym_total.index(count_fsym_dic.get(i)) < (2*fsym_total_unit):
#        a = amount[i] * eval('data2.' + count_fsym_dic[i])
#        value.append(a)
#    else:
#        a = amount[i] * eval('data3.' + count_fsym_dic[i])
#        value.append(a)
        
for i in count:
    a = amount[i] * (data[count_fsym_dic[i]])
    value.append(a)


# In[737]:


value = []
#for i in count:
#    if fsym_total.index(count_fsym_dic.get(i)) < (fsym_total_unit):
#        a = amount[i] * eval('data1.' + count_fsym_dic[i])
#        value.append(a)
#    elif fsym_total.index(count_fsym_dic.get(i)) < (2*fsym_total_unit):
#        a = amount[i] * eval('data2.' + count_fsym_dic[i])
#        value.append(a)
#    else:
#        a = amount[i] * eval('data3.' + count_fsym_dic[i])
#        value.append(a)
        
for i in count:
    a = amount[i] * (data[count_fsym_dic[i]])
    value.append(a)

#Non riesco a fare le sommatorieeeeeee, edit: non riuscivo
#sumvalue = value[0] + value[1] + value[2] + value[3] + value[4] #+ value[5] + value[6] + value[7] + value[8] + value[9]


# In[738]:


for i in count:
    if i == 0:
        sumvalue = value[i]
    else:
        sumvalue = sumvalue + value[i]


# In[739]:


fsymvalues = []
fsymcount = 0
print('fsymvalues loading:')
for i in count:
    fsymvalue = get_coin_value(i, count_fsym_dic[i])
    fsymvalues.append(fsymvalue)
    print(fsymcount, 'of', len(count))
    fsymcount = fsymcount + 1
print(fsymcount, 'of', len(count))


# In[740]:


print(dates_list_reversed)
print(histoday_dic.get(dates_list_reversed[0+1]))


# In[741]:


import datetime
fsymvalues_per_histoday = []
print('fsymvalues_per_histoday loading:')
start_time = time.time()
for e in enumerate(fsym_list_per_histoday):
    lista = []
    for i in enumerate(fsym_list_per_histoday[e[0]]):
        Fsymvalue = get_coin_value_per_histoday_raw(i[0], i[1], e[0])
        if str(Fsymvalue) == 'nan':
            Fsymvalue = get_coin_value_per_histoday_real(i[0], i[1], e[0])
        else:
            pass
        lista.append(Fsymvalue)
        print(i[0], 'of', leng)
    print(e[0], 'of', monthlist[-1])
    elapsed_time = time.time() - start_time
    print('elapsed time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)), (str(int(((e[0])/monthlist[-1])*100)) + '%'))
    fsymvalues_per_histoday.append(lista)


# In[742]:


print(histoday_dic)


# In[743]:


def get_portfolio_value_percentage(fsymvalues_element):
    fsymvaluessum1raw = []
    for i in count:
        a = fsymvalues[i][fsymvalues_element] 
        fsymvaluessum1raw.append(a)
    fsymvaluessums = sum(fsymvaluessum1raw)
    return fsymvaluessums


# In[744]:


for e in monthlist:
    fsymvaluessum1raw = []
    for i in count:
        a = fsymvalues[i][e]
        fsymvaluessum1raw.append(a)
        #print(fsymvaluessum1raw)
    fsymvaluessums = sum(fsymvaluessum1raw)
    #print(fsymvaluessums)  


# In[745]:


lista3 = []
for e in monthlist:
    lista2 = []
    fsymvaluessum2raw = []
    for k in enumerate(fsym_list_per_histoday):
        lista = []
        for i in enumerate(fsym_list_per_histoday[k[0]]):
            A = fsymvalues_per_histoday[k[0]][i[0]][e]
            fsymvaluessum2raw.append(A)
        fsymvaluessums2 = sum(fsymvaluessum2raw)
        lista.append(fsymvaluessums2)
        lista2.append(lista)
    lista3.append(lista2[k[0]])
    #print(lista2[1]) 


# In[746]:


print(fsymvalues_per_histoday)


# In[747]:


portfoliovalues = []
for i in (monthlist[:2]):
    lista = []
    for k in count:
        pf = amount[k] * coininitialprice_per_histoday[i][k]
        lista.append(pf)
    portfoliovalues.append(lista)
#print(portfoliovalues)
#print(portfoliovalues[1]) #<--- questo equivale al valore degli fsym dopo il primo mese, necessari per calcolare il valore del portafoglio dopo il primo mese e infine i nuovi amount


# In[748]:


portfoliovalues_sum = sum(portfoliovalues[1])
#print(portfoliovalues_sum)
newamount_test = (portfoliovalues_sum / leng) / coininitialprice_per_histoday[1][0]
#print(newamount_test)

newamount = []
for i in enumerate(fsym_list_per_histoday[:2]):
    lista = []
    for k in enumerate(fsym_list_per_histoday[0]):
        newamount1 = (portfoliovalues_sum / leng) / coininitialprice_per_histoday[i[0]][k[0]]
        lista.append(newamount1)
    newamount.append(lista)
#print(newamount[1]) #<--- questo equivale ai nuovi amount che avremo dopo il primo mese
#print(newamount[1][1] * coininitialprice_per_histoday[1][1])  #<---- questi valori per ogni fsym devono essere uguali
#ora devo calcolare i nuovi valori degli fsym dopo questo mese,dopo fare la somma per trovare il valore del portafoglio e infine i nuovi amount del prossimo mese


# In[749]:


newamount_per_histoday = []
portfoliovalues_per_histoday = []
newamount_coin_per_histoday = []
nacounter = 2
if nacounter == 2:
    for k in (monthlist[2:]):
        test = []
        for i in count:
            x = newamount[1][i] * coininitialprice_per_histoday[nacounter][i]
            test.append(x)
        test_sum = sum(test)
        newamount_coin = []
        for i in count:
            if coininitialprice_per_histoday[nacounter][i] != 0:
                newamountcoin = (test_sum / leng) / coininitialprice_per_histoday[nacounter][i]
                newamount_coin.append(newamountcoin) 
            else:
                price = get_error_price(fsym_list_per_histoday[nacounter][i], histoday_dic.get(dates_list_reversed[nacounter]))
                newamountcoin = ((test_sum / leng) / price)
                newamount_coin.append(newamountcoin) 
                print('refetching price for:', nacounter, i, fsym_list_per_histoday[nacounter][i], price, coininitialprice_per_histoday[nacounter][i])
        newamount_coin_per_histoday.append(newamount_coin)
        newamount_per_histoday.append(test)
        portfoliovalues_per_histoday.append(test_sum)
        nacounter = nacounter + 1
else:
    for k in (monthlist[2:]):
        test = []
        for i in count:
            x = newamount_coin_per_histoday[k-2][i] * coininitialprice_per_histoday[nacounter][i]
            test.append(x)
        test_sum = sum(test)
        newamount_coin = []
        for i in count:
            if coininitialprice_per_histoday[nacounter][i] != 0:
                newamountcoin = (test_sum / leng) / coininitialprice_per_histoday[nacounter][i]
                newamount_coin.append(newamountcoin)
            else:
                price = get_error_price(fsym_list_per_histoday[nacounter][i], histoday_dic.get(dates_list_reversed[nacounter]))
                newamountcoin = ((test_sum / leng) / price)
                newamount_coin.append(newamountcoin)               
                print('refetching price for:', nacounter, i, fsym_list_per_histoday[nacounter][i], price, coininitialprice_per_histoday[nacounter][i])
        newamount_coin_per_histoday.append(newamount_coin)
        newamount_per_histoday.append(test)
        portfoliovalues_per_histoday.append(test_sum)
        nacounter = nacounter + 1
#print(newamount_coin_per_histoday)


# In[750]:


#Devo modificare gli 'error at'in modo date che prenda i prezzi da coinmarketcap

import datetime
#print(fsym_list_per_histoday)
newamount_per_histoday = []
portfoliovalues_per_histoday = []
new_amount_coin_per_histoday = []
test_0_per_histoday = []
test_per_histoday = []
nacounter = 2
new_amount_coin_0_per_histoday = []
print('rebalanced amount loading:')
for e in enumerate(fsym_list_per_histoday[:-1]):
    print(e[0], 'of', len(fsym_list_per_histoday[:-1]))
    test_0 = []
    newamount_coin_0 = []
    test = []
    newamount_coin = []
    for i in enumerate(fsym_list_per_histoday[e[0]]):
        if i[1] ==  fsym_list_per_histoday[(e[0] + 1)][i[0]]: #<---- vuol dire che gli fsym del mese successivo nello stesso index sono diversi
            if e[0] == 0:
                #print(e[0], i[1], 'ok')
                x = amount[i[0]] * coininitialprice_per_histoday[(e[0]+1)][i[0]]
                test_0.append(x)
                #print(x)
                #print(test_0)
            elif e[0] == 1:
                #print(e[0], i[1], 'ok')
                x = new_amount_coin_0_per_histoday[0][i[0]] * coininitialprice_per_histoday[(e[0]+1)][i[0]]
                test.append(x)
                #print(x)
                #print(test)   
            else:
                #print(e[0], i[1], 'ok')
                x = new_amount_coin_per_histoday[(e[0]-1)][i[0]] * coininitialprice_per_histoday[(e[0]+1)][i[0]]
                test.append(x)
                #print(x)
                #print(test)
        else:
            if e[0] == 0:
                #print(e[0], i[1], 'error')
                x = amount[i[0]] * get_initial_price(fsym_list_per_histoday[e[0]][i[0]], dates_list_reversed[(e[0]+1)])
                test_0.append(x)
                #print(x)
            elif e[0] == 1:
                #print(e[0], i[1], 'error')
                x = new_amount_coin_0_per_histoday[0][i[0]] * get_initial_price(fsym_list_per_histoday[e[0]][i[0]], dates_list_reversed[(e[0]+1)])
                test.append(x)                
            else:
                #print(e[0], i[1], 'error')
                x = new_amount_coin_per_histoday[(e[0]-1)][i[0]] * get_initial_price(fsym_list_per_histoday[e[0]][i[0]], dates_list_reversed[(e[0]+1)])
                test.append(x)
                #print(x)
                #print(test)
    test_0_per_histoday.append(test_0)
    test_sum_0 = sum(test_0_per_histoday[0])
    test_per_histoday.append(test)
    test_sum = sum(test_per_histoday[e[0]])
    #print('calcola new amount coin da qui')
    for i in enumerate(fsym_list_per_histoday[e[0]]):
        if i[1] ==  fsym_list_per_histoday[(e[0] + 1)][i[0]]:
            if e[0] == 0:
                #print(e[0], i[1], 'ok')
                if coininitialprice_per_histoday[(e[0]+1)][i[0]] != 0:
                    newamountcoin = (test_sum_0 / leng) / coininitialprice_per_histoday[(e[0]+1)][i[0]]
                    newamount_coin_0.append(newamountcoin)
                else:
                    price = get_error_price(fsym_list_per_histoday[e[0]+1][i[0]], histoday_dic.get(dates_list_reversed[(e[0]+1)]))
                    newamountcoin = ((test_sum_0 / leng) / price)
                    newamount_coin_0.append(newamountcoin)
                    print('refetching price for:', (e[0]+1), i[0], i[1], price, coininitialprice_per_histoday[(e[0]+1)][i[0]], dates_list_reversed[(e[0]+1)])
                #print(newamountcoin)
            elif e[0] == 1:
                #print(e[0], i[1], 'ok')
                if coininitialprice_per_histoday[(e[0]+1)][i[0]] != 0:
                    newamountcoin = ((test_sum / leng) / coininitialprice_per_histoday[(e[0]+1)][i[0]])
                    newamount_coin.append(newamountcoin)  
                else:
                    price = get_error_price(fsym_list_per_histoday[e[0]+1][i[0]], histoday_dic.get(dates_list_reversed[(e[0]+1)]))
                    newamountcoin = ((test_sum / leng) / price)
                    newamount_coin.append(newamountcoin)
                    print('refetching price for:', (e[0]+1), i[0], i[1], price, coininitialprice_per_histoday[(e[0]+1)][i[0]], dates_list_reversed[(e[0]+1)])
            else:
                #print(e[0], i[1], 'ok')
                if coininitialprice_per_histoday[(e[0]+1)][i[0]] != 0:
                    newamountcoin = ((test_sum / leng) / coininitialprice_per_histoday[(e[0]+1)][i[0]])
                    newamount_coin.append(newamountcoin)
                else:
                    price = get_error_price(fsym_list_per_histoday[e[0]+1][i[0]], histoday_dic.get(dates_list_reversed[(e[0]+1)]))
                    newamountcoin = ((test_sum / leng) / price)
                    newamount_coin.append(newamountcoin)
                    print('refetching price for:', (e[0]+1), i[0], i[1], price, coininitialprice_per_histoday[(e[0]+1)][i[0]], dates_list_reversed[(e[0]+1)])
                #print(newamountcoin)               
        else:
            if e[0] == 0:
                #print(e[0], i[1], 'error')
                if get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)]) != 0:
                    newamountcoin = ((test_sum_0 / leng) / get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)]))
                    #print(newamountcoin, e[0], i[0], i[1])
                    newamount_coin_0.append(newamountcoin)
                else:
                    price = get_error_price(fsym_list_per_histoday[e[0]+1][i[0]], histoday_dic.get(dates_list_reversed[(e[0]+1)]))
                    newamountcoin = ((test_sum_0 / leng) / price)
                    newamount_coin_0.append(newamountcoin)
                    print('refetching price for:', (e[0]+1), i[0], i[1], price, get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)]))
                #print(newamountcoin)
            elif e[0] == 1:
                #print(e[0], i[1], 'error')
                if get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)]) != 0:
                    newamountcoin = ((test_sum) / leng) / get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)])
                    newamount_coin.append(newamountcoin)
                else:
                    price = get_error_price(fsym_list_per_histoday[e[0]+1][i[0]], histoday_dic.get(dates_list_reversed[(e[0]+1)]))
                    newamountcoin = ((test_sum / leng) / price)
                    newamount_coin.append(newamountcoin)
                    print('refetching price for:', (e[0]+1), i[0], i[1], price, get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)]))
                #print(newamountcoin)
            else:
                #print(e[0], i[1], 'error')
                if get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)]) != 0:
                    newamountcoin = ((test_sum) / leng) / get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)])
                    newamount_coin.append(newamountcoin)
                else:
                    price = get_error_price(fsym_list_per_histoday[e[0]+1][i[0]], histoday_dic.get(dates_list_reversed[(e[0]+1)]))
                    newamountcoin = ((test_sum / leng) / price)
                    newamount_coin.append(newamountcoin)
                    print('refetching price for:', (e[0]+1), i[0], i[1], price, get_initial_price(fsym_list_per_histoday[e[0]+1][i[0]], dates_list_reversed[(e[0]+1)]))
                #print(newamountcoin)
    new_amount_coin_0_per_histoday.append(newamount_coin_0)
    new_amount_coin_per_histoday.append(newamount_coin)
    #print('ricomincia da capo')
#print(test_0_per_histoday[0])
#print(new_amount_coin_0_per_histoday[0])
#print(test_per_histoday)
#print(new_amount_coin_per_histoday)
print(len(fsym_list_per_histoday[:-1]), 'of', len(fsym_list_per_histoday[:-1]))


# In[751]:


coinvalues_per_histoday = [] #<--- serve per verificare che le percentuali dei coin siano tutte uguali
for k in (monthlist[2:]):
    lista = []
    for i in count:
        x = newamount_coin_per_histoday[k-2][i] * coininitialprice_per_histoday[k][i]
        lista.append(x)
    coinvalues_per_histoday.append(lista)
print(coinvalues_per_histoday)


# In[752]:


def get_portfolio_value_percentage_per_histoday(fsymvalues_element):
    lista2 = []
    fsymvaluessum1raw = []
    for e in enumerate(fsym_list_per_histoday):
        lista = []
        for i in enumerate(fsym_list_per_histoday[e[0]]):
            A = fsymvalues_per_histoday[e[0]][i[0]][fsymvalues_element]
            fsymvaluessum1raw.append(A)
        fsymvaluessums = sum(fsymvaluessum1raw)
        lista.append(fsymvaluessums)
        lista2.append(lista)
    return  lista2


# In[753]:


fsymvaluesum_per_histoday = []
for e in enumerate(fsym_list_per_histoday):
        lista = []
        for i in enumerate(fsym_list_per_histoday[e[0]]):
            A = get_portfolio_value_percentage_per_histoday(e[0])
            lista.append(A)
        fsymvaluesum_per_histoday.append(lista)
#print(fsymvaluesum_per_histoday[2][3][0])


# In[754]:


fsymvaluesum_per_histoday_real = []
for i in monthlist:
    Lista = []
    for k in monthlist:
        x = fsymvaluesum_per_histoday[k][0][i][0]
        Lista.append(x)
    fsymvaluesum_per_histoday_real.append(Lista)
#print(fsymvaluesum_per_histoday_real[2])


# In[755]:


fsymvaluesum_per_histoday_test = []
for i in monthlist:
    Y = fsymvaluesum_per_histoday_real[i][i]
    fsymvaluesum_per_histoday_test.append(Y)
print(fsymvaluesum_per_histoday_test) 


# In[756]:


fsymvaluesum = []
for i in monthlist:
    #a = get_portfolio_value_percentage(num_reversed_dic.get(i))
    a = get_portfolio_value_percentage(monthlist[i])
    fsymvaluesum.append(a)

fsymvaluessumlist = fsymvaluesum


#dates_list_reversed = dates_list[::-1]
#dictionary = dict(zip(dates_list_reversed, fsymvaluessumlist))
dictionary = dict(zip(dates_list_reversed, fsymvaluesum_per_histoday_test))

print('Your portfolio percentages performance are:', dictionary)


# In[757]:


coinvalues = []
for i in count:
    coinvalue = fsymvalues[i][::-1]
    coinvalues.append(coinvalue)
#print(coinvalues)

# DA MODIFICAREEEEEEEEEEEEEE
#fsym = ['BTC', 'ETH', 'XRP', 'LTC', 'DASH', 'XMR', 'ETC', 'MAID', 'XEM', 'REP', 'ICN', 'STEEM', 'FCT', 'ZEC', 'DOGE', 'GNT', 'WAVES', 'DGD', 'GAME']


count_fsym_dic = dict(zip(count, fsym))
#print(count_fsym_dic)

newamount = (fsymvaluessumlist[1]/leng) / (get_initial_price(count_fsym_dic.get(0), datesdic.get(0)))


# In[758]:


print(count_fsym_dic.get(0))
print(fsym_list_per_histoday[0][0])
print(datesdic.get(0))
print(histoday_dic.get(datesdic.get(0)))
print(histoday_dic)


# In[759]:


#date are from dates_list_reversed 
def get_amount_in_date(date):
    amounts = []
    for i in count:
        for k, v in datesdic.items():
            if get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))) != 0:
                newamount = (fsymvaluessumlist[date]/leng) / (get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))))
            else:
                price = get_error_price(count_fsym_dic.get(i), histoday_dic.get(datesdic.get(date)))
                newamount = (fsymvaluessumlist[date]/leng) / price
        print(i, ' of', len(count))
        amounts.append(newamount)
    return amounts


# In[760]:


#date are from dates_list_reversed 
def get_amount_in_date_new(date):
    amounts = []
    for i in count:
        try:
            index = get_data_index(i, date)
            if str(data[count_fsym_dic.get(i)][index]) != 'nan':  
                newamount = (fsymvaluessumlist[date]/leng) / data[count_fsym_dic.get(i)][index]
            elif get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))) != 0:
                print('data = nan, refetching...')
                newamount = (fsymvaluessumlist[date]/leng) / (get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))))       
            else:
                print('data = nan & data = 0, refetching...')
                price = get_error_price(count_fsym_dic.get(i), histoday_dic.get(datesdic.get(date)))
                newamount = (fsymvaluessumlist[date]/leng) / price
        except:
            print("error, can't find index, refetching...", i)
            if get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))) != 0:
                  newamount = (fsymvaluessumlist[date]/leng) / (get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))))
            else:
                print('data = 0, refetching...')
                price = get_error_price(count_fsym_dic.get(i), histoday_dic.get(datesdic.get(date)))
                newamount = (fsymvaluessumlist[date]/leng) / price              
        print(i, ' of', len(count))
        amounts.append(newamount)
    return amounts


# In[761]:


#date are from dates_list_reversed 
def get_amount_in_date_new_old(date):
    amounts = []
    for i in count:
        for k, v in datesdic.items():
            try:
                index = get_data_index(i, date)
                if str(data[count_fsym_dic.get(i)][index]) != 'nan':
                    newamount = (fsymvaluessumlist[date]/leng) / data[count_fsym_dic.get(i)][index]
                elif get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))) != 0:
                    print('data = nan, refetching...')
                    newamount = (fsymvaluessumlist[date]/leng) / (get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))))       
                else:
                    print('data = nan & data = 0, refetching...')
                    price = get_error_price(count_fsym_dic.get(i), histoday_dic.get(datesdic.get(date)))
                    newamount = (fsymvaluessumlist[date]/leng) / price
            except:
                print("error, can't find index, refetching...", i)
                if get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))) != 0:
                    newamount = (fsymvaluessumlist[date]/leng) / (get_initial_price(count_fsym_dic.get(i), str(datesdic.get(date))))
                else:
                    print('data = 0, refetching...')
                    price = get_error_price(count_fsym_dic.get(i), histoday_dic.get(datesdic.get(date)))
                    newamount = (fsymvaluessumlist[date]/leng) / price              
        print(i, ' of', len(count))
        amounts.append(newamount)
    return amounts


# In[762]:


#print(get_amount_in_date_new(1))


# In[763]:


import datetime
amountvalues = []
counter = 0
start_time = time.time()
print('amountvalues loading:')
for i in monthlist:
    try:
        a = get_amount_in_date_new(i)
    except:
        ending_loop_time = start_time + 3600
        rest_time = ending_loop_time - time.time()
        print('Reached Cryptocompare hours rate limit, waiting for:', time.strftime("%H:%M:%S", time.gmtime(rest_time)))
        #time.sleep(rest_time)
        continue
    amountvalues.append(a)
    counter = counter + 1
    elapsed_time = time.time() - start_time
    print('elapsed time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print(counter, 'of', len(monthlist))
#print(amountvalues) 


# In[764]:


for i in range(0, len(amountvalues)):
    print('Your amount in date', dates_list_reversed[i], 'is', amountvalues[i])


# In[765]:


#print(amountvalues[1][1])
import datetime
fsympercentages_list = []
for e in range(0, len(amountvalues)):
    amounts = amountvalues[e]
    fsympercentages = []
    for i in count:
        try:
            index = get_data_index(i, e)
            price = data[i][index]
            x =(amounts[i] * price) / fsymvaluessumlist[e]
            if str(price) == 'nan':               
                x = (amounts[i] * get_initial_price(count_fsym_dic.get(i), datesdic.get(e))) / fsymvaluessumlist[e]
            else:
                pass
        except:
            x = (amounts[i] * get_initial_price(count_fsym_dic.get(i), datesdic.get(e))) / fsymvaluessumlist[e]
        fsympercentages.append(x)
    fsympercentages_list.append(fsympercentages)

    
#PUOI CONTROLLAREE SE TUTTI I VALORI SONO UGUALIIIIIIIIIIIIIIIIIIIIIIIIIIII CHE BELLOOOOOOOOOOOOOOOOOO
print('printing fsym_percentages_list:')
print(fsympercentages_list)


#SE VUOI TROVA IL MODO DI FARE IL GRAFICO MA NON É NECESSARIO
#fsympercentages_dict_1 = dict(zip(fsym, fsympercentages_1))
#names = list(fsympercentages_dict.keys())
#values = list(fsympercentages_dict.values())

#tick_label does the some work as plt.xticks()
#plt.figure(figsize=(30,16))
#plt.bar(range(len(fsympercentages_dict)),values,tick_label=names)
#plt.title('Portofolio percentages in date ' + dates_list_reversed[1], fontsize=12)
#plt.ylabel('Percentages', fontsize=12)
#plt.show()


# In[766]:


import datetime
dflist = []
#for i in count:
#    x = []
#    if fsym_total.index(count_fsym_dic.get(i)) < (fsym_total_unit):
#        for group in eval('data1.' + count_fsym_dic.get(i) + '.groupby([(df1.index.year),(df1.index.month)])'):
#            x.append(group[1])
#        dflist.append(x)
#    elif fsym_total.index(count_fsym_dic.get(i)) < (2*fsym_total_unit):
#        for group in eval('data2.' + count_fsym_dic.get(i) + '.groupby([(df2.index.year),(df2.index.month)])'):
#            x.append(group[1])
#        dflist.append(x)
#    else:
#        for group in eval('data3.' + count_fsym_dic.get(i) + '.groupby([(df3.index.year),(df3.index.month)])'):
#            x.append(group[1])
#        dflist.append(x)
##print(dflist)

for i in count:
    x = []
    #for group in eval('data.' + count_fsym_dic.get(i) + '.groupby([(df.index.year),(df.index.month)])'):
    for group in (data[count_fsym_dic.get(i)].groupby([(df.index.year),(df.index.month)])):
        x.append(group[1])
    dflist.append(x)


# In[767]:


import datetime
dflist_total = []
#for i in enumerate(fsym_total):
#    x = []
#    if fsym_total.index(i[1]) < (fsym_total_unit):
#        for group in eval('data1.' + i[1] + '.groupby([(df1.index.year),(df1.index.month)])'):
#            x.append(group[1])
#        dflist_total.append(x)
#    elif fsym_total.index(i[1]) < (2*fsym_total_unit):
#        for group in eval('data2.' + i[1] + '.groupby([(df2.index.year),(df2.index.month)])'):
#            x.append(group[1])
#        dflist_total.append(x)
#    else:
#        for group in eval('data3.' + i[1] + '.groupby([(df3.index.year),(df3.index.month)])'):
#            x.append(group[1])
#        dflist_total.append(x)
##print(dflist_total)

for i in enumerate(fsym_total):
    x = []
    #for group in eval('data.' + i[1] + '.groupby([(df.index.year),(df.index.month)])'):
    for group in (data[i[1]].groupby([(df.index.year),(df.index.month)])):
        x.append(group[1])
    dflist_total.append(x)


# In[768]:


from datetime import datetime

currentSecond= datetime.now().second
currentMinute = datetime.now().minute
currentHour = datetime.now().hour

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year
#print(type(currentMonth))
#print(currentDay)


# In[769]:


amountvalues_dic_list = []
for i in range(0, len(amountvalues)):
    a = dict(zip(fsym, amountvalues[i]))
    amountvalues_dic_list.append(a)

# Ottieni la percentuale di BTC = (count_fsym_dic.get(0), nella data 0 = fsympercentages_dic_list[0]   


# In[770]:


# i = monthlist
Rebalancing_Monthy_Date_Coin = (amount_per_histoday[11][1]) * dflist_total[fsym_total.index(fsym_list_per_histoday[11][4])][11]
#print(Rebalancing_Monthy_Date_Coin)


# In[771]:


buynhold_monthly = []
for e in count:
    lista = []
    for i in monthlist:
        #x = fsym_total.index(fsym_list_per_histoday[i][e])
        #y = amount[e] * dflist_total[x][i]
        y = amount[e] * dflist[e][i]
        lista.append(y)
    buynhold_monthly.append(lista)
#print(buynhold_monthly)


# In[772]:


#cointinua a funzionare finché BTC rimane sempre primo in fsym_total e in dflist_total
def get_nan_series(num_fsym_total):
    if dflist_total[num_fsym_total][0].index.year[0] == dflist_total[0][0].index.year[0]:
        if dflist_total[num_fsym_total][0].index.month[0] == dflist_total[0][0].index.month[0]:
            #fare quello che faceva prima
            pass
        else:
            diff_month = dflist_total[num_fsym_total][0].index.month[0] - dflist_total[0][0].index.month[0]
            #print('diff_month', diff_month)
            if diff_month > 0:
                month = dflist_total[num_fsym_total][0].index.month[0] - diff_month
            else:
                month = dflist_total[num_fsym_total][0].index.month[0] + diff_month
            #print('month', month)  
            dates = []
            for i in range(dflist_total[0][0].index.day[0], dflist_total[0][0].index.day[0] + len(dflist_total[0][0].index.day)):
                x = str(dflist_total[0][0].index.year[0]) + '-' + str(month) + '-' + str(i)
                dates.append(x)
            #print('dates', dates)
            firstday = int(dflist_total[0][0].index.day[0])
            lenday = int(len(dflist_total[0][0].index.day))
            lastday = int(firstday+lenday)
            values = [i for i in range(firstday, lastday)]
            #print(firstday, lenday, lastday)
            #print(values)
            data_x = data = {'Date': dates, 'Value': values}
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            ts = pd.Series(df['Value'], index=df['Date'])
            #print(ts)
            lendays = []
            for i in range(0, diff_month):
                le = len(dflist_total[0][i].index.day)
                lendays.append(le)
                if lendays[i] > 31:
                    if lendays[i-1] == 30:
                        lendays[i] = 31
                    else:
                        lendays[i] = 30
                else:
                    pass
            #print('lendays', lendays)
            dates1 = []
            for e in range(0, diff_month):
                dates2 = []
                if e == 0:
                    for i in range(dflist_total[0][0].index.day[0], dflist_total[0][0].index.day[0] + len(dflist_total[0][0].index.day)):
                        x = str(dflist_total[0][0].index.year[0]) + '-' + str(month) + '-' + str(i)
                        dates2.append(x)
                    month = month + 1
                else:
                    for i in range(dflist_total[0][1].index.day[0], lendays[e]+1):
                        x = str(dflist_total[0][0].index.year[0]) + '-' + str(month) + '-' + str(i)
                        dates2.append(x)
                    month = month + 1
                dates1.append(dates2)
            #print('dates1', dates1)
            firstdays = int(dflist_total[0][1].index.day[0])
            values1 = []
            for i in range(0, diff_month):
                values2 = [i for i in range(firstdays, lendays[i]+1)]
                values1.append(values2)
            #print('values1', values1)
            ts_test = []
            for i in range(0, diff_month):
                datas_x = datas = {'Date': dates1[i], fsym_total[num_fsym_total]: values1[i]}
                dfs = pd.DataFrame(datas)
                ts1 = pd.Series(dfs[fsym_total[num_fsym_total]], index=dfs['Date'])  
                ts_test.append(ts1)
            #print('ts_test', ts_test)
            dflist_total_x = []
            for i in range(0, diff_month):
                dflist_total_x.append(ts_test[i])
            for i in range(0, len(dflist_total[num_fsym_total])):
                dflist_total_x.append(dflist_total[num_fsym_total][i])
            #print(dflist_total_x)
            
    else:
        diff_year = dflist_total[36][0].index.year[0] - dflist_total[0][0].index.year[0]
        if diff_year > 0:
            year = dflist_total[36][0].index.year[0] - diff_year
        else:
            year = dflist_total[36][0].index.year[0] + diff_year
        print([36], [0], 'anno sbagliato, controlla il codice: "get_nan_series"')
        
    return dflist_total_x
    


# In[773]:


rebalancing_monthly = []
for e in count:
    lista = []
    for i in monthlist:
        x = fsym_total.index(fsym_list_per_histoday[i][e])
        if i == 0:
            if len(dflist_total[x]) == len(monthlist):
                y = amount[e] * dflist_total[x][i]
            elif len(dflist_total[x]) < len(monthlist):
                y = amount[e] * get_nan_series(x)[i]
            else:
                print('error rb, len(dflist_total[x] > len(monthlist), check the code)')
        elif i == 1:
            if len(dflist_total[x]) == len(monthlist):
                y = new_amount_coin_0_per_histoday[0][e] * dflist_total[x][i]
            elif len(dflist_total[x]) < len(monthlist):
                y = new_amount_coin_0_per_histoday[i-1][e] * get_nan_series(x)[i]
            else:
                print('error rb, len(dflist_total[x] > len(monthlist), check the code)')
        else:
            if len(dflist_total[x]) == len(monthlist):
                y = new_amount_coin_per_histoday[i-1][e] * dflist_total[x][i]
            elif len(dflist_total[x]) < len(monthlist):
                y = new_amount_coin_per_histoday[i-1][e] * get_nan_series(x)[i]
            else:
                print('error rb, len(dflist_total[x] > len(monthlist), check the code)')
        lista.append(y)
    rebalancing_monthly.append(lista)
#print(rebalancing_monthly[17])


# In[774]:


FixedWeight_Monthly = []
for e in enumerate(fsym):
    x = []
    try:
        for i in monthlist:
            FixedWeight_Monthly_Date_Coin = ((amountvalues[i][e[0]])) * (dflist[e[0]][i])
            x.append(FixedWeight_Monthly_Date_Coin)
        FixedWeight_Monthly.append(x)
    except:
        for i in (monthlist[:-1]):
            FixedWeight_Monthly_Date_Coin = ((amountvalues[i][e[0]])) * (dflist[e[0]][i])
            x.append(FixedWeight_Monthly_Date_Coin)
        FixedWeight_Monthly.append(x)
#print(FixedWeight_Monthly)


# In[775]:


bh_monthly = []
for i in count:
    y = []
    #for e in (monthlist[:-1]):
    for e in monthlist:
        y.append(buynhold_monthly[i][e])
    bh_monthly.append(y)
#print(bh_monthly[2])


# In[776]:


for i in count:
    for e in monthlist:
        print(len(bh_monthly[i][e]), i , e)


# In[777]:


rb_monthly = []
for i in count:
    y = []
    #for e in (monthlist[:-1]):
    for e in monthlist:
        y.append(rebalancing_monthly[i][e])
    rb_monthly.append(y)
#print(rb_monthly[2])


# In[778]:


for i in count:
    for e in monthlist:
        for k in range(0, len(rb_monthly[i][e])):
            if str(rb_monthly[i][e][k]) == 'nan':
                print(i, e, k)


# In[779]:


print(len(monthlist))


# In[780]:


print(rb_monthly[0])


# In[781]:


error_list = []
for i in count:
    deleting_list = []
    for e in monthlist:
        if len(rb_monthly[i][e]) > 31:
            for k in enumerate(rb_monthly[i][e]):
                if k[0] == (len(rb_monthly[i][e])-1):
                    pass
                else:
                    if str(rb_monthly[i][e][k[0]]) == str(rb_monthly[i][e][k[0]+1]):
                        if k[0] > 31:
                            pass
                        else:
                            deleting_list.append(k[0])
                    else:
                        pass
            x = str(i) + '--' + str(e)
            error_list.append(x)
            rb_monthly[i][e] = rb_monthly[i][e].drop(rb_monthly[i][e][deleting_list].index)
        else:
            pass


# In[782]:


FW_Monthly = []
for i in count:
    y = []
    for e in monthlist:
        y.append(FixedWeight_Monthly[i][e])
    FW_Monthly.append(y)
#print(FW_Monthly[1])


# In[783]:


error_list = []
for i in count:
    deleting_list = []
    for e in monthlist:
        if len(FW_Monthly[i][e]) > 31:
            for k in enumerate(FW_Monthly[i][e]):
                if k[0] == (len(FW_Monthly[i][e])-1):
                    pass
                else:
                    if str(FW_Monthly[i][e][k[0]]) == str(FW_Monthly[i][e][k[0]+1]):
                        if k[0] > 31:
                            pass
                        else:
                            deleting_list.append(k[0])
                    else:
                        pass
            x = str(i) + '--' + str(e)
            error_list.append(x)
            FW_Monthly[i][e] =FW_Monthly[i][e].drop(FW_Monthly[i][e][deleting_list].index)
        else:
            pass


# In[784]:


error_list = []
for i in count:
    deleting_list = []
    for e in monthlist:
        if len(bh_monthly[i][e]) > 31:
            for k in enumerate(bh_monthly[i][e]):
                if k[0] == (len(bh_monthly[i][e])-1):
                    pass
                else:
                    if str(bh_monthly[i][e][k[0]]) == str(bh_monthly[i][e][k[0]+1]):
                        if k[0] > 31:
                            pass
                        else:
                            deleting_list.append(k[0])
                    else:
                        pass
            x = str(i) + '--' + str(e)
            error_list.append(x)
            bh_monthly[i][e] = bh_monthly[i][e].drop(bh_monthly[i][e][deleting_list].index)
        else:
            pass


# In[785]:


bh_monthly_concat = []
for i in count:
    z = pd.concat(bh_monthly[i])
    bh_monthly_concat.append(z)
#print(bh_monthly_concat[0])


# In[786]:


rb_monthly_concat = []
for i in count:
    z = pd.concat(rb_monthly[i])
    #print(i, 'done')
    rb_monthly_concat.append(z)
#print(rb_monthly_concat[0])


# In[787]:


FW_Monthly_concat = []
for i in count:
    z = pd.concat(FW_Monthly[i])
    FW_Monthly_concat.append(z)
#print(FW_Monthly_concat[0])


# In[788]:


bhc = 0
while bhc < (len(count)):
    if bhc == 0:
        buynhold_monthly_tot = bh_monthly_concat[bhc]
    else:
        buynhold_monthly_tot = buynhold_monthly_tot + bh_monthly_concat[bhc]
    bhc = bhc + 1


# In[789]:


#bhc = 0
#while bhc < (len(count))/2:
#    if bhc == 0:
#        buynhold_monthly_tot0 = bh_monthly_concat[bhc]
#    else:
#        buynhold_monthly_tot0 = buynhold_monthly_tot0 + bh_monthly_concat[bhc]
#    bhc = bhc + 1


# In[790]:


#while bhc < (len(count)):
#    if bhc == (len(count))/2:
#        buynhold_monthly_tot1 = bh_monthly_concat[bhc]
#    else:
#        print(bhc)
#        buynhold_monthly_tot1 = buynhold_monthly_tot1 + bh_monthly_concat[bhc]
#    bhc = bhc + 1


# In[791]:


rbc = 0
while rbc < len(count):
    if rbc == 0:
        rebalancing_monthly_tot = rb_monthly_concat[rbc]
    else:
        rebalancing_monthly_tot = rebalancing_monthly_tot + rb_monthly_concat[rbc]
    rbc = rbc + 1


# In[792]:


#rbc = 0
#while rbc < (len(count))/2:
#    if rbc == 0:
#        rebalancing_monthly_tot0 = rb_monthly_concat[rbc]
#    else:
#        rebalancing_monthly_tot0 = rebalancing_monthly_tot0 + rb_monthly_concat[rbc]
#    rbc = rbc + 1


# In[793]:


#while rbc < (len(count)):
#    if rbc == (len(count))/2:
#        rebalancing_monthly_tot1 = rb_monthly_concat[rbc]
#    else:
#        print(rbc)
#        rebalancing_monthly_tot1 = rebalancing_monthly_tot1 + rb_monthly_concat[rbc]
#    rbc = rbc + 1


# In[794]:


fwc = 0
while fwc < len(count):
    if fwc == 0:
        FixedWeight_Monthly_Tot = FW_Monthly_concat[fwc]
    else:
        FixedWeight_Monthly_Tot = FixedWeight_Monthly_Tot + FW_Monthly_concat[fwc]
    fwc = fwc + 1


# In[795]:


#fwc = 0
#while fwc < (len(count))/2:
#    if fwc == 0:
#        FixedWeight_Monthly_Tot0 = FW_Monthly_concat[fwc]
#    else:
#        FixedWeight_Monthly_Tot0 = FixedWeight_Monthly_Tot0 + FW_Monthly_concat[fwc]
#    fwc = fwc + 1


# In[796]:


#while fwc < len(count):
#    if fwc == (len(count))/2:
#        FixedWeight_Monthly_Tot1 = FW_Monthly_concat[fwc]
#    else:
#        FixedWeight_Monthly_Tot1 = FixedWeight_Monthly_Tot1 + FW_Monthly_concat[fwc]
#    fwc = fwc + 1


# In[797]:


globaldata_df = pd.read_csv('GlobalData.csv', index_col=0, header=0, sep=';')
globaldata_df = globaldata_df.astype(float)


# In[798]:


globaldata_series = pd.Series.from_csv('GlobalData.csv', index_col=0, header=0, sep=';')
globaldata_series = globaldata_series.astype(float)


# In[799]:


for i in range(0, len(globaldata_series)):  
    if rebalancing_monthly_tot.index[0] == globaldata_series.index[i]:
        globaldata_real = globaldata_series[105:]
    else:
        pass


# In[800]:


globaldata = (globaldata_real - globaldata_real.iloc[0]) / globaldata_real.iloc[0]


# In[801]:


end_time = time.time() - initial_time
print('Total elapsed time:', time.strftime("%H:%M:%S", time.gmtime(end_time)))


# In[802]:


rb_max = 0
for i in range(0, len(rebalancing_monthly_tot)):
    if i == 0:
        pass
    else:
        if str(rebalancing_monthly_tot[i]) == 'nan':
            pass
        else:            
            if rebalancing_monthly_tot[i] > rb_max:
                rb_max = rebalancing_monthly_tot[i]
            else:
                pass
print('Rebalance max performance:', rb_max)

bh_max = 0
for i in range(0, len(buynhold_monthly_tot)):
    if i == 0:
        pass
    else:
        if str(buynhold_monthly_tot[i]) == 'nan':
            pass
        else:            
            if buynhold_monthly_tot[i] > bh_max:
                bh_max = buynhold_monthly_tot[i]
            else:
                pass
print('Buy and Hold max performance:', bh_max)

FW_max = 0
for i in range(0, len(FixedWeight_Monthly_Tot)):
    if i == 0:
        pass
    else:
        if str(FixedWeight_Monthly_Tot[i]) == 'nan':
            pass
        else:            
            if FixedWeight_Monthly_Tot[i] > FW_max:
                FW_max = FixedWeight_Monthly_Tot[i]
            else:
                pass
print('Fixed Weight max performance:', FW_max)

global_max = 0
for i in range(0, len(globaldata)):
    if i == 0:
        pass
    else:
        if str(globaldata[i]) == 'nan':
            pass
        else:            
            if globaldata[i] > global_max:
                global_max = globaldata[i]
            else:
                pass
print('Marketcap max performance:', global_max)

BTC_max = 0
for i in range(0, len(pricecoin[0])):
    if i == 0:
        pass
    else:
        if str(pricecoin[0][i]) == 'nan':
            pass
        else:            
            if pricecoin[0][i] > BTC_max:
                BTC_max = pricecoin[0][i]
            else:
                pass
print('BTC max performance:', BTC_max)


# In[803]:


print('Fixed Weight Monthly performance:', FixedWeight_Monthly_Tot[-1])
print('Buy and Hold performance:', buynhold_monthly_tot[-1])
print('Rebalance Monthly performance:', rebalancing_monthly_tot[-1])
print('BTC performance:', pricecoin[0][-1])
print('Marketcap performance:', globaldata[-1])
print('RB - MKT performance:', (rebalancing_monthly_tot[-1] - globaldata[-1]))

print('Fixed Weight max performance:', FW_max)
print('Buy and Hold max performance:', bh_max)
print('Rebalance max performance:', rb_max)
print('Marketcap max performance:', global_max)
print('BTC max performance:', BTC_max)

plt.figure(figsize=(30,16))
#for i in count:
#    plt.plot(pricecoin[i], label=(count_fsym_dic.get(i)))
plt.plot(FixedWeight_Monthly_Tot, label='Fixed Weight Monthly', linewidth=2)
#plt.plot(portfolioreal2, label='Buy and Hold', linewidth=5)
plt.plot(buynhold_monthly_tot, label='Buy and Hold', linewidth=2)
plt.plot(rebalancing_monthly_tot, label='Rebalance Monthly', linewidth=2)
plt.plot(pricecoin[0], label='BTC', linewidth=2)
plt.plot(globaldata, label='MarketCap', linewidth=2)
plt.legend(loc='upper left', prop={'size': 17})
plt.title('Portfolios - ' + str(count[-1]+1) + ' crypto', fontsize=12)
plt.ylabel('Perfomance', fontsize=12)
plt.yscale('linear')

