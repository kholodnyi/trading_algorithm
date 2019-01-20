'''
Test of trading strategy using a ccxt library on bittrex exchange
'''

import ccxt
import time

bittrex = ccxt.bittrex({
    'apiKey': 'YOUR API KEY', # input your API key
    'secret': 'YOUR API SECRET', # input your API secret
})
markets = bittrex.load_markets()

'''following functions market_instant_buy and market_instant_sell
   created for exchanges that not support a market trades (only limit)
   like bittrex that was tested'''

def market_instant_buy(exchange_name, currency_name, trade_amount_BTC): # bittrex doesn't support market sell!
    try:
        asks = exchange_name.fetch_order_book(currency_name + '/BTC')['asks']
        actual_rate = 0
        sum = 0
        for ask in asks:
            if ask[0] * ask[1] + sum >= trade_amount_BTC:
                actual_rate = ask[0]
                break
            else:
                sum = ask[0] * ask[1]
        buy = exchange_name.create_limit_buy_order(currency_name + '/BTC', (trade_amount_BTC / actual_rate), actual_rate)
        last_order_id = buy['id']
        amount_of_alt = round(exchange_name.fetch_order(last_order_id)['amount'], 3) # round need to be replaced, probably by math.ceil
        return(actual_rate, last_order_id, amount_of_alt)
        '''it not real actual rate,
           actual can be taken from an order by it's ID
           but for this kind of strategy would be enought'''
    except:
        return False

def market_instant_sell(exchange_name, currency_name, amount_of_alt): # bittrex doesn't support market sell!
    try:
        bids = exchange_name.fetch_order_book(currency_name + '/BTC')['bids']
        actual_rate = 0
        sum = 0
        for ask in asks:
            if bid[0] * bid[1] + sum >= amount_of_alt:
                actual_rate = bid[0]
                break
            else:
                sum = bid[0] * bid[1]
        sell = exchange_name.create_limit_sell_order(currency_name + '/BTC', amount_of_alts, actual_rate)
        last_order_id = sell['id']
        return(actual_rate, last_order_id)
        '''it not real actual rate,
           actual can be taken from an order by it's ID
           but for this kind of strategy would be enought'''
    except:
        return False

def strategy_1_precent_BTC(exchange_name, currency_name, trade_amount_BTC):

    if (exchange_name.fetch_balance()['free']['BTC']) < trade_amount_BTC:
        return print('not enough funds!')
    initial_buy = market_instant_buy(exchange_name, currency_name, trade_amount_BTC) # initial buy
    if not(initial_buy): # condition true when market buy function not working (return False)
        return print('problem with initial buy')
    actual_rate = initial_buy[0]
    amount_of_alt = round(initial_buy[2], 3)
    print('\n', initial_buy)

    i = 0
    while i < 4320: # can be changed to True for endless cycle or to reaching min / max values of depo
        if exchange_name.fetch_order_book(currency_name + '/BTC')['bids'][0][0] / 1.005 >= actual_rate: # take profit - 0.5%
            sell_with_profit = market_instant_sell(exchange_name, currency_name, amount_of_alt)
            if not(sell_with_profit): # condition true when market sell function not working (return False)
                return print('problem with sell with profit!')
            print('\nsell with profit! details:\n')
            print(sell_with_profit)
            buy = market_instant_buy(exchange_name, currency_name, trade_amount_BTC)
            actual_rate = buy[0]
            amount_of_alt = round(buy[2], 3)
        elif exchange_name.fetch_order_book(currency_name + '/BTC')['bids'][0][0] <= actual_rate * 0.98: # stop loss - 2%
            stop_loss = market_instant_sell(exchange_name, currency_name, amount_of_alt)
            if not(stop_loss): # condition true when market sell function not working (return False)
                return print('problem with stop loss sell!')
            print('\nstop loss! details:\n')
            print(stop_loss)
            buy = market_instant_buy(exchange_name, currency_name, trade_amount_BTC)
            actual_rate = buy[0]
            amount_of_alt = amount_of_alt = round(buy[2], 3)
        else:
            print('>', end='')
            time.sleep(5)
        i += 1

if __name__ == '__main__':
    strategy_1_precent_BTC(bittrex, 'WAVES', 0.001) # amount should be no less than 0.001 and bittrex exscange is mandatory
