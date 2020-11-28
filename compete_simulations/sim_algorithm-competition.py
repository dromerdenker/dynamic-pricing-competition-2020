import numpy as np
import sys
import importlib
import traceback
import time
import copy
import pandas as pd
import numbers

import logging, os
#fancy progress bar
from tqdm import tqdm

logging.basicConfig(format="%(asctime)s %(name)s %(levelname)-10s %(message)s")
log = logging.getLogger("test_algorithm")
log.setLevel(int(os.environ.get("LOG_LEVEL", logging.WARNING)))

sys.path.append('../src')

### Request Functions for Duopoly, Oligopoly and Dynamic

def get_random_duopoly_demands(price, c_price):
    #both sell a ticket
    player_demand, competitor_demand = 1,1
    #if one has 10% lower price than other, they can sell more
    if(price < 0.9*c_price):
        player_demand = np.random.randint(1,6)
    if(c_price < 0.9*price):
        competitor_demand = np.random.randint(1,6)
    if(price > 75):
        player_demand = 0
    if(c_price > 75):
        competitor_demand = 0
    return player_demand, competitor_demand

def duopoly_request(t,s,
                    prices_self,price,
                    prices_competitor,
                    c_price,
                    demand,
                    demand2,
                    competitor_capacity,
                    player_capacity,
                    information_dump):
    if t==1 :
        prices_historical = None
        prices2_historical = None
        demand_historical = None
        demand2_historical = None
        competitor_has_capacity_current_period_in_current_season = True
        player_has_capacity_current_period_in_current_season = True
    else:
        prices_self.append(price)
        #c_price = np.random.randint(20,80);
        c_price = np.round(max(0.1, 0.95*prices_self[-1]+np.random.uniform(0.1,0.5)),1);
        c_price = np.round(np.clip(c_price, 0.1, 99),1)
        prices_competitor.append(c_price)
        #prices_competitor.append(c_price)
        prices_historical = [ prices_self, prices_competitor ]
        prices2_historical = [ prices_competitor, prices_self ]

        random_demand, random_demand2 = get_random_duopoly_demands(price, c_price)

        demand.append(random_demand)
        demand2.append(random_demand2)
        demand_historical = copy.deepcopy(demand)
        demand2_historical = copy.deepcopy(demand2)

        #competitor_has_capacity_current_period_in_current_season = competitor_capacity

        competitor_has_capacity_current_period_in_current_season = 80 < sum(demand2_historical)
        player_has_capacity_current_period_in_current_season = 80 < sum(demand_historical)
        if competitor_has_capacity_current_period_in_current_season == False:
            competitor_has_capacity_current_period_in_current_season = False
        else:
            competitor_has_capacity_current_period_in_current_season = False if (t>80 and np.random.rand()>0.9) else True

        if player_has_capacity_current_period_in_current_season == False:
            player_has_capacity_current_period_in_current_season = False
        else:
            player_has_capacity_current_period_in_current_season = False if (t>80 and np.random.rand()>0.9) else True


        demand_historical  = np.array(demand_historical)
        prices_historical  = np.array(prices_historical)
        demand2_historical = np.array(demand2_historical)
        prices2_historical = np.array(prices2_historical)

    if t == 1 and s == 1:
        request_input = {
            "current_selling_season" : s,
            "selling_period_in_current_season" : t,
            "prices_historical_in_current_season" : prices_historical,
            "demand_historical_in_current_season" : demand_historical,
            "competitor_has_capacity_current_period_in_current_season" : competitor_has_capacity_current_period_in_current_season,
            "information_dump": None
        }
        request_input2 = {
            "current_selling_season" : s,
            "selling_period_in_current_season" : t,
            "prices_historical_in_current_season" : prices2_historical,
            "demand_historical_in_current_season" : demand2_historical,
            "competitor_has_capacity_current_period_in_current_season" : player_has_capacity_current_period_in_current_season,
            "information_dump": None
        }
    else:
        request_input = {
            "current_selling_season" : s,
            "selling_period_in_current_season" : t,
            "prices_historical_in_current_season" : prices_historical,
            "demand_historical_in_current_season" : demand_historical,
            "competitor_has_capacity_current_period_in_current_season" : competitor_has_capacity_current_period_in_current_season,
            "information_dump": information_dump
        }
        request_input2 = {
            "current_selling_season" : s,
            "selling_period_in_current_season" : t,
            "prices_historical_in_current_season" : prices2_historical,
            "demand_historical_in_current_season" : demand2_historical,
            "competitor_has_capacity_current_period_in_current_season" : player_has_capacity_current_period_in_current_season,
            "information_dump": information_dump
        }
    return request_input, request_input2, competitor_has_capacity_current_period_in_current_season, player_has_capacity_current_period_in_current_season





###########################################################
###########################################################

### Test Run Functions

def test_run_duopoly(user_code, competer_code, n_selling_seasons, n_selling_periods, print_output = False):

    test_run_times = []
    test_run_times2 = []
    test_run_erros = set()
    test_run_erros2 = set()

    competitor_capacity = True
    player_capacity = True

    information_dump = None
    information_dump2 = None

    user_results = pd.DataFrame(columns=["Selling_Season", "Selling_Period", "Price", "Competitor_has_capacity", "Demand", "Revenue", "Error", "Runtime_ms"])
    competer_results = pd.DataFrame(columns=["Selling_Season", "Selling_Period", "Price", "Player_has_capacity", "Demand", "Revenue", "Error", "Runtime_ms"])

    for selling_season in tqdm(range(1, n_selling_seasons + 1)):

        # print("Currently in Selling Season: " + str(selling_season))
        # print("-" * 30)

        prices_self = []
        prices_competitor = []
        demand = []
        demand2 = []
        price = 1
        c_price = 1
        for selling_period_in_current_season in range(1, n_selling_periods + 1):

            # if selling_period_in_current_season % 50 == 0:
                # print("Currently in Selling Period: " + str(selling_period_in_current_season))
                # print("-" * 30)


            demand_competitor = demand2
            request_input, request_input2, competitor_capacity, player_capacity = duopoly_request(selling_period_in_current_season,selling_season, prices_self, price, prices_competitor, c_price, demand, demand_competitor, competitor_capacity, player_capacity, information_dump)

#             request_input2, competitor_capacity2 = duopoly_request(selling_period_in_current_season,selling_season, prices_competitor, c_price, prices_self, demand_competitor, demand, competitor_capacity2, information_dump2)

            if selling_period_in_current_season > 1:
                user_results.at[len(user_results)-1, "Demand"] = request_input["demand_historical_in_current_season"][-1]
                last_sell = min(user_results.Demand[len(user_results)-1], max(80-sum(user_results.Demand[:len(user_results)-1]),0))
                user_results.at[len(user_results)-1, "Revenue"] = last_sell * price

                competer_results.at[len(competer_results)-1, "Demand"] = request_input2["demand_historical_in_current_season"][-1]
                last_sell2 = min(competer_results.Demand[len(competer_results)-1], max(80-sum(competer_results.Demand[:len(competer_results)-1]),0))
                competer_results.at[len(competer_results)-1, "Revenue"] = last_sell2 * c_price
            start_time = time.time()
            error_this_period = False
            error_this_period2 = False
            try:
                price, information_dump = user_code.p(**request_input)
                if isinstance(price, numbers.Number):
                    if price >= 0.1 and price <= 999:
                        pass
                    else:
                        raise Exception('price output ' + str(price) + ' is not a valid number in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
                else:
                    raise Exception('price output ' + str(price) + ' is not a valid number in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
            except:
                error = traceback.format_exc()
                test_run_erros.add(error)
                price = np.random.randint(20,80)
                error_this_period = True
            end_time = time.time()

            user_results.loc[len(user_results)] = [selling_season, selling_period_in_current_season, price, request_input["competitor_has_capacity_current_period_in_current_season"], None, None, error_this_period, (end_time-start_time)*1000]

            test_run_times.append((end_time-start_time)*1000)

            try:
                c_price, information_dump2 = competer_code.p(**request_input2)
                if isinstance(c_price, numbers.Number):
                    if c_price >= 0.1 and c_price <= 999:
                        pass
                    else:
                        raise Exception('competitors price output ' + str(c_price) + ' is not a valid number in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
                else:
                    raise Exception('competitors price output ' + str(c_price) + ' is not a valid number in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
            except:
                error2 = traceback.format_exc()
                test_run_erros2.add(error2)
                c_price = np.random.randint(20,80)
                error_this_period2 = True
            end_time2 = time.time()


            competer_results.loc[len(competer_results)] = [selling_season, selling_period_in_current_season, c_price, request_input2["competitor_has_capacity_current_period_in_current_season"], None, None, error_this_period2, (end_time2-end_time)*1000]

        test_run_times2.append((end_time2-end_time)*1000)

        last_random_demand, last_random_demand2 = get_random_duopoly_demands(price, c_price)

        last_sell = min(last_random_demand, max(80-sum(user_results.Demand[:-1]),0))
        user_results.at[len(user_results) - 1, "Demand"] = last_random_demand
        user_results.at[len(user_results) - 1, "Revenue"] = last_sell * price

        #last_random_demand2 = np.random.randint(1,10)
        last_sell2 = min(last_random_demand2, max(80-sum(competer_results.Demand[:-1]), 0))
        competer_results.at[len(user_results) - 1, "Demand"] = last_random_demand2
        competer_results.at[len(user_results) - 1, "Revenue"] = last_sell2 * c_price

        # print("Finished with Selling Season: " +  str(selling_season))
        # print("-" * 30)
        # print("-" * 30)
        # print("-" * 30)


    df_errors = pd.DataFrame(columns = ["Error_Num", "Error_Code"])
    df_errors2 = pd.DataFrame(columns = ["Error_Num", "Error_Code"])

    df_times = pd.DataFrame(columns = ["Time Statistic", "Time Value (in ms)"])
    df_times.loc[len(df_times)] = ["Average Time", np.mean(test_run_times)]
    df_times.loc[len(df_times)] = ["Minimum Time", np.min(test_run_times)]
    df_times.loc[len(df_times)] = ["Maximum Time", np.max(test_run_times)]


    df_times2 = pd.DataFrame(columns = ["Time Statistic", "Time Value (in ms)"])
    df_times2.loc[len(df_times)] = ["Average Time", np.mean(test_run_times2)]
    df_times2.loc[len(df_times)] = ["Minimum Time", np.min(test_run_times2)]
    df_times2.loc[len(df_times)] = ["Maximum Time", np.max(test_run_times2)]

    counter = 1
    for error in list(test_run_erros):
        df_errors.loc[len(df_errors)] = [counter, error]
        counter += 1
    counter2 = 1
    for error2 in list(test_run_erros2):
        df_errors2.loc[len(df_errors2)] = [counter2, error2]
        counter2 += 1

    writer = pd.ExcelWriter('../local_simruns/duopoly_results.xlsx')
    user_results.to_excel(writer,'user_results')
    competer_results.to_excel(writer,'competer_results.csv')
    df_errors.to_excel(writer,'errors')
    df_times.to_excel(writer,'runtimes')
    df_errors2.to_excel(writer,'competer_errors')
    writer.save()

    you_won = competer_results.Revenue.sum() < user_results.Revenue.sum()
    print(f"{'WON' if you_won else 'LOST'}  Revenues: {user_results.Revenue.sum()} | {competer_results.Revenue.sum()}")
    return you_won



if __name__ == "__main__":

    scenario = "duopoly"
    competing_algo = sys.argv[1]
    seed = sys.argv[2]
    np.random.seed(int(seed))

    try:
        log.info("Importing the function for the " + str(scenario) + " pricing scenario.")
        user_code = importlib.import_module(str(scenario))
        log.info("Importing the function for the " + str(competing_algo) + " pricing scenario.")
        competer_code = importlib.import_module(str(competing_algo))
    except:
        log.exception(
            "Could not import the relevant function from module for " + str(scenario) + " pricing scenario or competing scenario "+ str(competing_algo) +" Can not perform testing"
        )
        ex_type, ex_value, ex_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(ex_traceback)
        stack_trace = list()
        for trace in trace_back:
            stack_trace.append(
                "File : %s , Line : %d, Func.Name : %s, Message : %s"
                % (trace[0], trace[1], trace[2], trace[3])
            )
        sys.exit()

    try:
        log.info("Running evaluation for the " + str(scenario) + " pricing scenario.")
        if scenario == "duopoly":
            success = test_run_duopoly(user_code, competer_code, 5, 100)

        else:
            log.exception(
                "Selected scenario: " + str(scenario) + " not supported. Stop testing!"
            )
            sys.exit()
    except:
        log.exception(
            "Error when running the " + str(scenario) + " pricing scenario. Stop testing!"
        )
        sys.exit()
