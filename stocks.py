import argparse
from enum import Enum
import requests
import pprint 

pp = pprint.PrettyPrinter(indent=4)
##Commons

class Stock(Enum):
    AAPL = 'AAPL'
    GOOGL='GOOGL'
    AMZN='AMZN'
    TSLA='TSLA'
    FB='FB'
    TWTR='TWTR'
    UBER='UBER'
    LYFT='LYFT'
    SNAP='SNAP'
    SHOP='SHOP'


def get_stock_data(stock:Stock):
    response=requests.get(f'https://financialmodelingprep.com/api/v3/quote-short/{stock.name}?apikey=c13a5d2ecf7cc6b8c50c06d7e1dfce22')
    return response.json()[0]

## For optimization stuff
def get_price_safe(stock:Stock):
    try:
        return get_stock_data(stock)['price']
    except:
        ##return 123.5
        raise Exception(f'No stock price for {stock}')



## for dynamic programming
example_item = {
    "value": 100, ## The higher, the better
    "diversification":{'AAPL':1,'GOOGL':0} ## ETC
}
## every item here should be of the previous structure
cache = {}

def optimize_aux(prices, i, amount, cache):
    '''
        Basically I used the 0/1 knapsack problem with a tweak to transform it 
        into a unbounded knapsack problem
    '''
    key = f'{i}:{amount}' 
    ##print(key)
    if key in cache:
        return cache[key]
    if i == -1 or amount == 0:
        result =  {'value':0, 'diversification':{}}
    elif prices[i]['price'] > amount:
        result = optimize_aux(prices, i-1, amount, cache)
    else:
        dont_take_it = optimize_aux(prices, i-1, amount,cache)
        '''
        As you can see, here I don't subtract from i, allowing the algorithm to choose the same stock 
        more than once
        '''
        take_it = optimize_aux(prices, i, amount-prices[i]['price'], cache)
        if(take_it['value']+ prices[i]['price'] > dont_take_it['value']):
            diversification = take_it['diversification'].copy()
            diversification[prices[i]['stock']] = diversification.get(prices[i]['stock'],0)+1
            result = {
                'value': take_it['value']+ prices[i]['price'],
                'diversification': diversification
            }
        else:
            result = dont_take_it
    cache[key] = result
    return result

def optimize(amount:float):
    prices= [{'stock':stock.name,'price':get_price_safe(stock)} for stock in list(Stock)]
    prices = [price for price in prices if price['price']!=False]
    min_amount_allowed = sum([price['price'] for price in prices])
    '''
    I do this, given the fact that I have to choose all stock at least once,
    so I buy one of every, and then do the optimization with the rest of the money
    '''
    if(amount<min_amount_allowed):
        raise Exception(f"Not enough money, it needs to be greated or equal than {min_amount_allowed}")
    
    result= optimize_aux(prices,len(prices)-1,amount-min_amount_allowed,{})
    
    return {
        'prices': prices,
        'remaining':amount-result['value']-min_amount_allowed,
        'diversification':{ 
            price['stock']:result['diversification'].get(price['stock'],0)+1 for price in prices
            }}



## For price of acquiring it all

def all(stock:Stock):
    data = get_stock_data(stock)
    volume = data['volume']
    unit_price = data['price']
    return volume*unit_price

parser = argparse.ArgumentParser(description='Some stuff with stocks')
subparsers = parser.add_subparsers(dest='option')
parser_all = subparsers.add_parser('all', help='to know price of acquiring it all')
parser_all.add_argument('--stock',help= 'which stock to acquire?',required=True,type=Stock,choices=list(Stock))
parser_optimize = subparsers.add_parser('optimize', help = 'to know best way of distributing your investments')
parser_optimize.add_argument('--amount', help = 'how much money to invest', required=True,type=float)
args= parser.parse_args()


if(args.option == 'optimize'):
    pp.pprint(optimize(args.amount))
elif(args.option == 'all'):
    pp.pprint(all(args.stock))
