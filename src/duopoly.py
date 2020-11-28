from typing import Any, Optional, Tuple, Union
import math
import numpy as np
import pandas as pd
import logging

log = logging.getLogger("duopoly")

TOP_X_PRICES = 3
DAY_ONE_PRICE = 76
MAX_PRICE = 100
MIN_PRICE = 0
WINDOW_MOVING_AVG = 3 # 5 days look back on competitor price
MAX_WINDOW = 100
PERIODS_IN_A_SEASON = 100
SEATS_IN_PLANE = 80
FAKE_BOTTOM_PRICE = 0.1
DISCOUNT_PERC = -20
MARK_UP_PERC = 10 # inverse of discount
PRICE_WHEN_WE_ARE_DONE = MAX_PRICE + 0.06 #100.xx where xx is the day in the month of the upload of my code (e.g. 31July->100.31)

def p(
    current_selling_season: int,
    selling_period_in_current_season: int,
    prices_historical_in_current_season: Union[np.ndarray, None],
    demand_historical_in_current_season: Union[np.ndarray, None],
    competitor_has_capacity_current_period_in_current_season: bool,
    information_dump=Optional[Any],
) -> Tuple[float, Any]:
    """Determine which price to set for the next period.

    Parameters
    ----------
    current_selling_season : int
        The current selling season (1, 2, 3, ...).
    selling_period_in_current_season : int
        The period in the current season (1, 2, ..., 1000).
    prices_historical_in_current_season : Union[np.ndarray, None]
        A two-dimensional array of historical prices. The rows index the competitors and the columns
        index the historical selling periods. Equal to `None` if
        `selling_period_in_current_season == 1`.
    demand_historical_in_current_season : Union[np.ndarray, None]
        A one-dimensional array of historical (own) demand. Equal to `None` if
        `selling_period_in_current_season == 1`.
    competitor_has_capacity_current_period_in_current_season : bool
        `False` if competitor is out of stock
    information_dump : Any, optional
        To keep a state (e.g., a trained model), by default None

    Examples
    --------

    >>> prices_historical_in_current_season.shape == (2, selling_period_in_current_season - 1)
    True

    >>> demand_historical_in_current_season.shape == (selling_period_in_current_season - 1, )
    True

    Returns
    -------
    Tuple[float, Any]
        The price and a the information dump (with, e.g., a state of the model).
    """



    if selling_period_in_current_season == 1:
        # Randomize in the first period of the season
        information_dump = {'competitor_sold_out_at': None}
        price = DAY_ONE_PRICE

    elif 0 is free_seats_after(demand_historical_in_current_season):
        return PRICE_WHEN_WE_ARE_DONE, information_dump

    elif 30 < free_seats_after(demand_historical_in_current_season) < 70:
        target = sales_target_today(demand_historical_in_current_season)
        my_past_prices = prices_historical_in_current_season[0]

        c_raises = competitor_price_raises(prices_historical_in_current_season[1])
        c_demand_at_raises = [1] * len(c_raises)
        merged_demand = np.append(demand_historical_in_current_season, c_demand_at_raises)
        merged_prices = np.append(my_past_prices,c_raises)
        price = avg_top_3_price_of_at_least_target(target, merged_demand, merged_prices)

    else:
        #Explore and close with fire-sale
        target = sales_target_today(demand_historical_in_current_season)
        yesterdays_sales = demand_historical_in_current_season[-1]

        price = my_previous_real_price(prices_historical_in_current_season)
        um = uplift_multiplier(target, yesterdays_sales)
        if yesterdays_sales < 1.3* target:
            #discount!
            price = price_adjust(DISCOUNT_PERC, price )
        elif yesterdays_sales > (1.1* target):
            # increase the price, we're selling more than we need to.
            price = price_adjust(MARK_UP_PERC * um, price )

    return np.clip(round(price, 2), MIN_PRICE, MAX_PRICE), information_dump


def competitor_price_raises( prices_trace ):
    '''returns the prices after which the competitor raised their price,
    so they must have sold at least 1 item at that price.'''
    raises = []
    idx = 1 #skip the item zero
    while idx < len(prices_trace):
        if (prices_trace[idx-1] < prices_trace[idx]):
            raises.append(prices_trace[idx-1])
        idx = idx + 1

    return raises


def uplift_multiplier( target, yesterdays_sales ):
    oversell = target - yesterdays_sales
    try:
        mult = abs(oversell / target)
    except ZeroDivisionError:
        mult = 1
    return mult

def avg_top_3_price_of_at_least_target(target, demand_trace , price_of_demand):
    '''returns the avg of top 3 prices that had <target> sales.'''
    #construct dataframe from demand and my prices
    dems = pd.DataFrame(pd.Series(demand_trace), columns=['demand'])
    pris = pd.DataFrame(pd.Series(price_of_demand), columns=['price'])

    df = pd.concat([dems, pris], axis=1)
    top = pd.DataFrame()
    log.info(df)
    # keep the rows where we sold at least the TARGET number of seats
    while 0 < target and 3 < len(df):
        top = df[ df['demand'] > target ]
        log.info(top)
        target = target - 1
    top = df[ df['demand'] > target ]
    sort_top = top.sort_values('price', ascending=False)
    log.info(sort_top)
    top3 = sort_top.head(TOP_X_PRICES)['price']
    log.info(top3)
    return top3.mean()


def my_previous_real_price(prices_historical_in_current_season):
    '''returns the previous price, looking back further if we set a
    FREAKY_OUTLIER price last'''
    idx = -1 # last of array
    return prices_historical_in_current_season[0, idx]

def sales_target_today(demand_historical_in_current_season):
    '''given prior demand -> calculate free seats -> deduce sales per
    day remaining target to sell out on last day.'''
    free = free_seats_after(demand_historical_in_current_season)
    periods_left = PERIODS_IN_A_SEASON - len(demand_historical_in_current_season)
    target = free / periods_left
    return target

def free_seats_after(demand_historical_in_current_season):
    '''returns the number of free seats so far.'''
    return max(0,SEATS_IN_PLANE - demand_historical_in_current_season.sum())

def highest_sale_price( prices, demand, window=MAX_WINDOW ):
    '''the highest sale price I set in the recent [WINDOW] that sold at
    least 1 unit, returns MAX_PRICE otherwise'''
    mx = -1
    for i in range(min(window, len(demand))):
        if i<len(demand) and demand[-i-1] > 0:
            mx = max(mx, prices[0, -i-1])
    if mx < MIN_PRICE:
        mx = MIN_PRICE
    return mx


def moving_avg_competitor( window, prices, sold_out ):
    ''' provide moving avg of competitor last [window] prices, if they
    are not sold out yet.
    If they are sold_out, return MAX_PRICE'''
    if sold_out:
        return MAX_PRICE
    # not sold out...
    avg = 0
    for i in range(window):
        try:
            avg = avg + prices[1,-i-1]
        except:
            pass # will yield too low result in early startup, but it's fast
    return avg / window


def price_adjust( percentage, base_price ):
    '''returns adjusted (valid) price from applying percentage to base_price
    NOTE: NEGATIVE percentage => discount'''
    return min(MAX_PRICE, ((100 + percentage) * base_price) / 100)

def middle(low, high):
    '''return the middle price between two prices, having lower bound low'''
    if low >= high:
        return min(low, MAX_PRICE)
    return min(MAX_PRICE,(low+high) / 2)
