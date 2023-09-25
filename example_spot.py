import json
import os
from pprint import pprint
import pandas as pd
from dotenv import load_dotenv
from tabulate import tabulate
import bitget.spot.account_api as account
import bitget.spot.market_api as market
import bitget.spot.order_api as order
import bitget.spot.plan_api as plan
import bitget.spot.public_api as public

load_dotenv()
if __name__ == "__main__":
    api_key = os.environ.get("BITGET_API_KEY")
    secret_key = os.environ.get("BITGET_SECRET_KEY")
    passphrase = os.environ.get("BITGET_PASSPHRASE")

    print(api_key, secret_key, passphrase)

    # symbol = 'btcusdt_spbl'

    # spot Get currency information
    publicApi = public.PublicApi(api_key, secret_key, passphrase, use_server_time=True, first=False)
    # result = publicApi.currencies()
    # pprint(result)

    # spot Obtain transaction pair information
    # result = publicApi.products()
    # print(len(result["data"]))
    # for i in result["data"][:240]:
    #     if i["status"] == "online":
    #         print(f"SubscribeReq('SP', 'ticker', '{i['symbolName']}'),")

    # df = pd.DataFrame(result["data"])
    # print(tabulate(df, headers="keys", tablefmt="fancy_grid"))
    # df.to_csv("products.csv", index=False)

    # # spot Get single transaction pair information
    # try:
    #     result = publicApi.product("btcusdt_spbl")
    #     # if result["data"]["status"] == "online":
    #     # exists = True
    # except Exception as e:
    #     pass

    marketApi = market.MarketApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
    # result = marketApi.fills(symbol, limit=50)
    # print(result)

    # result = marketApi.depth(symbol, limit=50, type='step0')
    # print(result)

    # result = marketApi.ticker(symbol)
    # print(result)

    result = marketApi.tickers()
    data = result["data"]
    
    # Convert usdtVol into float, then sort by usdtVol, then save to csv
    df = pd.DataFrame(data)
    df["usdtVol"] = df["usdtVol"].astype(float)
    df = df.sort_values(by="usdtVol", ascending=False)
    df.to_csv("tickers.csv", index=False)

    # result = marketApi.candles(symbol, period='1min', after='1624352586', before='1624356186', limit=100)
    # print(result)

    # accountApi = account.AccountApi(api_key, secret_key, passphrase, use_server_time=False, first=False)

    # result = accountApi.assets()
    # print(result)

    # result = accountApi.bills()
    # print(result)

    # orderApi = order.OrderApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
    # result = orderApi.orders(symbol='bftusdt_spbl', price='2.30222', quantity='1', side='buy', orderType='limit', force='normal', clientOrderId='spot#29028939ss')
    # print(result)

    order_data = [
        {
            "price": "2.30222",
            "quantity": "1",
            "side": "buy",
            "orderType": "limit",
            "force": "normal",
            "client_oid": "spot#jidhuu19399",
        },
        {
            "price": "2.30111",
            "quantity": "1",
            "side": "buy",
            "orderType": "limit",
            "force": "normal",
            "client_oid": "spot#akncnai8821",
        },
    ]
    # result = orderApi.batch_orders(symbol="bftusdt_spbl", order_data=order_data)
    # print(result)

    # result = orderApi.cancel_orders(symbol='bftusdt_spbl', orderId='791171749756964864')
    # print(result)

    # result = orderApi.cancel_batch_orders(symbol='bftusdt_spbl', orderId=[''])
    # print(result)

    # result = orderApi.open_order(symbol='bftusdt_spbl')
    # print(result)

    # result = orderApi.history(symbol='bftusdt_spbl')
    # print(result)

    # result = orderApi.fills(symbol='bftusdt_spbl')
    # print(result)

    # planApi = plan.PlanApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
#     result = planApi.placePlan(symbol='BTCUSDT_SPBL', side='buy', triggerPrice='22031', executePrice='22031', size='50', triggerType='market_price', orderType='market', timeInForceValue='normal')
#     print(result)

#     result = planApi.modifyPlan(orderId='987136018723487744', triggerPrice='22031', executePrice='22031', size='50', orderType='market')
#     print(result)

#     result = planApi.cancelPlan(orderId='987136018723487744')
#     print(result)

# result = planApi.currentPlan(symbol='BTCUSDT_SPBL', pageSize='5')
# print(result)
#
# result = planApi.historyPlan(symbol='BTCUSDT_SPBL', pageSize='5', startTime='1671005531000', endTime='1671085652000')
# print(result)
