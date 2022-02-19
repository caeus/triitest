import argparse
from enum import Enum
import requests

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
        return False



def optimize(amount:float):
    prices= {stock.name:get_price_safe(stock) for stock in list(Stock)}
    prices = {k:v for k,v in prices.items() if v!=False}
    min_price = min([v for k,v in prices.items()])
    nrmlzd_prices = {k:(v/min_price) for k,v in prices.items()}
    capacity = amount/min_price
    if(capacity<1):
        raise Exception("Not enough money")
    print(nrmlzd_prices)


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
    optimize(args.amount)
elif(args.option == 'all'):
    print(all(args.stock))
