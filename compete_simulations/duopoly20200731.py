from typing import Any, Optional, Tuple, Union
import math
import numpy as np

MAX_PRICE = 100
MIN_PRICE = 0
WINDOW_MOVING_AVG = 5 # 5 days look back on competitor price
MAX_WINDOW = 100
PERIODS_IN_A_SEASON = 100
SEATS_IN_PLANE = 80
FAKE_BOTTOM_PRICE = 0.1
DISCOUNT_PERC = -20
MARK_UP_PERC = 10 # inverse of discount
FREAKY_OUTLIERS = [13, 66] # throw 2 failures so copycats and average copiers are screwed
FREAKY_OUTLIER_PRICE = 999
PRICE_FOOL_THEM_WHEN_WE_ARE_DONE = MAX_PRICE + 0.31 #100.xx where xx is the day in the month of the upload of my code (e.g. 31July->100.31)

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
        price = MAX_PRICE

    elif selling_period_in_current_season in FREAKY_OUTLIERS:
        #throw off anyone doing a moving average without proper bracketing :-)
        return FREAKY_OUTLIER_PRICE, information_dump

    elif 0 is free_seats_after(demand_historical_in_current_season):
        return PRICE_FOOL_THEM_WHEN_WE_ARE_DONE, information_dump

    else:
        target = sales_target_today(demand_historical_in_current_season)
        yesterdays_sales = demand_historical_in_current_season[-1]

        price = my_previous_real_price(prices_historical_in_current_season)
        dm = discount_multiplier(target, yesterdays_sales)
        if yesterdays_sales < target:
            #discount!
            price = price_adjust(DISCOUNT_PERC, price )
        elif yesterdays_sales > (1.1* target):
            # up the rate, selling more than we need.
            price = price_adjust(MARK_UP_PERC * dm, price )

    return min(MAX_PRICE, round(price, 2)), information_dump


def discount_multiplier( target, yesterdays_sales ):
    oversell = target - yesterdays_sales
    try:
        mult = abs(oversell / target)
    except ZeroDivisionError:
        mult = 1
    return mult


def my_previous_real_price(prices_historical_in_current_season):
    '''returns the previous price, looking back further if we set a FREAKY_OUTLIER price last'''
    idx = -1 # last of array
    while prices_historical_in_current_season[0, idx] == FREAKY_OUTLIER_PRICE:
        idx = idx -1 #go back one further
    return prices_historical_in_current_season[0, idx]

def sales_target_today(demand_historical_in_current_season):
    '''given prior demand -> calculate free seats -> deduce sales per day remaining target to sell out on last day.'''
    free = free_seats_after(demand_historical_in_current_season)
    periods_left = PERIODS_IN_A_SEASON - len(demand_historical_in_current_season)
    target = free / periods_left
    return target

def free_seats_after(demand_historical_in_current_season):
    '''returns the number of free seats so far.'''
    return max(0,SEATS_IN_PLANE - demand_historical_in_current_season.sum())

def highest_sale_price( prices, demand, window=MAX_WINDOW ):
    '''the highest sale price I set in the recent [WINDOW] that sold at least 1 unit, returns MAX_PRICE otherwise'''
    mx = -1
    for i in range(min(window, len(demand))):
        if i<len(demand) and demand[-i-1] > 0:
            mx = max(mx, prices[0, -i-1])
    if mx < MIN_PRICE:
        mx = MIN_PRICE
    return mx

def moving_avg_competitor( window, prices, sold_out ):
    ''' provide moving avg of competitor last [window] prices, if they are not sold out yet.
    If they are sold_out, return MIN_PRICE'''
    if sold_out:
        return MIN_PRICE
    # not sold out...
    avg = 0
    for i in range(window):
        try:
            avg = avg + prices[1,-i-1]
        except:
            pass # will yield too low result in the early startup, but will be fast
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
