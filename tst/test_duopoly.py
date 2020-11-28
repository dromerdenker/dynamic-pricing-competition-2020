# Felix Ogg, 12 July 2020
# test code to figure out the p() function provided by the organizers

import sys, os
import logging

parent = os.path.dirname(os.path.abspath(__file__))
dpc_folder = os.path.join(parent, "../src")
sys.path.append(dpc_folder)
import numpy as np
import duopoly


def test_p_can_be_called():
    p, carry_over = duopoly.p(1, 1, None, None, True, None)
    #assert isinstance(p, numbers.Number)
    assert not carry_over or isinstance(carry_over, dict)


# let's implement a real one!
def test_p_starts_at_maxprice():
    p, carry_over = duopoly.p(1, 1, None, None, True, None)
    assert p == 76, "we start at max price always"


def test_highest_price_in_history():
    prices_history = np.array([[100], [1]])
    demand_history = np.array([1])
    assert 100, duopoly.highest_sale_price(season, period_in_season, False)

    demand_history = np.array([0])
    assert 50, duopoly.highest_sale_price(season, period_in_season, False)


def test_competitor_moving_avg():
    prices_were = np.array([[100], [1]])
    not_sold_out = False
    assert 1 == duopoly.moving_avg_competitor(1, prices_were, not_sold_out)
    prices_were_2 = np.array([[100, 100], [2, 10]])
    assert 6 == duopoly.moving_avg_competitor(2, prices_were_2, not_sold_out)
    prices_were_3 = np.array([[100, 100, 100, 100, 100, 100], [1, 6, 6, 6, 6, 6]])
    assert 6 == duopoly.moving_avg_competitor(1, prices_were_3, not_sold_out)


def test_free_seats():
    demand_history = np.array([1])
    assert 79 == duopoly.free_seats_after(demand_history)
    demand_history = np.array([80])
    assert 0 == duopoly.free_seats_after(demand_history)
    demand_history = np.array([1, 1, 5, 13])  # 20 sold
    assert 80 - 20 == duopoly.free_seats_after(demand_history)


def test_sales_target():
    demand_history = np.array([80])  # sold out!
    assert 0 == duopoly.sales_target_today(demand_history)
    demand_history = np.array([40])  # 40 sold on day 1
    assert 40/99 == duopoly.sales_target_today(demand_history)
    demand_history = np.array([0]*99)
    assert 80 == duopoly.sales_target_today(demand_history)


def test_price_discount_markup():
    base = 50
    assert duopoly.DISCOUNT_PERC == -20  # 20% discount
    assert 50 == duopoly.price_adjust(0, base)
    assert 40 == duopoly.price_adjust(-20, base)
    assert 40 == duopoly.price_adjust(duopoly.DISCOUNT_PERC, base)
    assert 55 == duopoly.price_adjust(10, base)
    assert 55 == duopoly.price_adjust(duopoly.MARK_UP_PERC, base)
    assert 100 == duopoly.price_adjust(duopoly.MARK_UP_PERC, 100)


def test_exploit_phase(caplog):
    caplog.set_level(logging.INFO)

    demand_trace    = [ 1, 2, 1, 1]
    price_of_demand = [20,40,50,30]

    assert 40 == duopoly.avg_top_3_price_of_at_least_target(1, demand_trace , price_of_demand)
    assert 40 == duopoly.avg_top_3_price_of_at_least_target(2, demand_trace, price_of_demand)
    assert 40 == duopoly.avg_top_3_price_of_at_least_target(3, demand_trace, price_of_demand), "for excessive target fall back to lower target"

def test_exploit_competitor(caplog):
    #caplog.set_level(logging.INFO)
    prices_without_demand_by_competitor = [1,3,2,4,5,6,5.5,5.2]
    rises = [1,2,4,5]
    assert rises == duopoly.competitor_price_raises(prices_without_demand_by_competitor)

def test_sales_target_today():
    # it's period 50 of 100 today
    demand_history = np.array([1] * 50) # 50 of 80 sold
    today_you_must_sell_this_many = duopoly.sales_target_today(demand_history)
    assert today_you_must_sell_this_many == 0.6
