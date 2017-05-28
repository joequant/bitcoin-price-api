#!/bin/python3
import requests
import grequests
import multiprocessing

assets = ['USD', 'USDT', 'EUR', 'BTC', 'XRP', 'ETH', 'HKD', 'LTC', 'RUR',
          'CNY', 'DASH', 'ZEC']

#btce
def btc_e(assets):
    retval = []
    r = requests.get('https://btc-e.com/api/3/info').json()
    urls=[]
    pairs = []
    for k, v in r['pairs'].items():
        k1, k2 = k.upper().split("_")
        if k1 in assets and k2 in assets:
            pairs.append(k)
            urls.append('https://btc-e.com/api/3/ticker/' + k)
    rs = [grequests.get(u) for u in urls]
    for i in zip(pairs, grequests.map(rs)):
        r = i[1].json()
        k = i[0]
        k1, k2 = k.upper().split("_")
        retval.append({'from': k1,
                       'to': k2,
                       'bid': r[k]['buy'],
                       'ask': r[k]['sell']})
    return retval


def gatecoin(assets):
    retval = []
    r = requests.get('https://api.gatecoin.com/Public/LiveTickers').json()
    for k in r['tickers']:
        s = k['currencyPair']
        k1 = s[0:3].upper()
        k2 = s[3:].upper()
        if k1 in assets and k2 in assets:
            retval.append({'from': k1,
                           'to': k2,
                           'bid': k['bid'],
                           'ask': k['ask']})
    return retval

def poloniex(assets):
    """Poloniex assets"""
    retval = []
    r = requests.get('https://poloniex.com/public?command=returnTicker')
    d = r.json()
    for k, v in d.items():
        k1, k2 = k.split("_")
        if k1 in assets and k2 in assets:
            retval.append({'from': k2,
                           'to': k1,
                           'bid': v['highestBid'],
                           'ask': v['lowestAsk']})
    return retval

def bitfinex(assets):
    """Bitfinex assets"""
    retval = []
    urls = []
    pairs = []
    bitfinex_url = 'https://api.bitfinex.com/v1'
    symbols = requests.get(bitfinex_url + '/symbols').json()
    for s in symbols:
        k1 = s[0:3].upper()
        k2 = s[3:].upper()
        if k1 == "DSH":
            k1 = "DASH"
        if k2 == "DSH":
            k1 = "DASH"
        if k1 in assets and k2 in assets:
            pairs.append(s)
            urls.append(bitfinex_url + '/pubticker/' + s)
    rs = [grequests.get(u) for u in urls]
    for i in zip(symbols, grequests.map(rs)):
        r = i[1].json()
        k = i[0]
        k1 = k[0:3].upper()
        k2 = k[3:].upper()
        retval.append({'from': k1,
                       'to': k2,
                       'bid': r['bid'],
                       'ask': r['ask']})
    return retval

def bitstamp(assets):
    """Bitstamp assets"""
    retval = []
    bitstamp_url = 'https://www.bitstamp.net/api/v2/ticker/'
    for s in ['btcusd', 'btceur',
              'eurusd', 'xrpusd', 'xrpeur',
              'xrpbtc']:
        d = requests.get(bitstamp_url + s +"/").json()
        k1 = s[0:3].upper()
        k2 = s[3:].upper()
        if k1 in assets and k2 in assets:
            retval.append({'from': k1,
                           'to': k2,
                           'bid': d['bid'],
                           'ask': d['ask']})
    return retval

def bitcashout(assets):
    retval = []
    resp = requests.get('https://www.bitcashout.com/ticker.json').json()
    for i in resp:
        retval.append({'from':'BTC',
                       'to': i['currency'].upper(),
                       'bid': i['buy'],
                       'ask': i['sell']})
    return retval

def anx(assets):
    retval = []
    urls = []
    pairs = []
    resp = requests.get('https://anxpro.com/api/3/currencyStatic').json()
    for k, v in resp['currencyStatic']['currencyPairs'].items():
        k1 = v['tradedCcy']
        k2 = v['settlementCcy']
        if k1 in assets and k2 in assets:
            pairs.append([k1, k2])
            urls.append('https://anxpro.com/api/2/%s/money/ticker' % k)
        rs = [grequests.get(u) for u in urls]
    for i in zip(pairs, grequests.map(rs)):
        r = i[1].json()
        k = i[0]
        k1 = k[0]
        k2 = k[1]
        retval.append({'from': k1,
                       'to': k2,
                       'bid': float(r['data']['buy']['value']),
                       'ask': float(r['data']['sell']['value'])})
    return retval
    
#add tag
def add_tag(d, tag):
    d['from'] = d['from'] + ":" + tag
    d['to'] = d['to'] + ":" + tag
    return d
 
tasks = [
    ['anx', anx],
    ['bitcashout', bitcashout],
    ['bitfinex', bitfinex],
    ['btce', btc_e],
    ['gatecoin', gatecoin],
    ['poloniex', poloniex],
    ['bitstamp', bitstamp]
    ]

def func(i):
    return [i[0], i[1](assets)]

p = multiprocessing.Pool()
for k, v in p.imap_unordered(func, tasks):
    for j in v:
        if j['from'] not in assets or j['to'] not in assets:
            continue
        j = add_tag(j,k)
        print(','.join(['bid-ask', j['from'], j['to'], str(j['bid']), str(j['ask'])]))
