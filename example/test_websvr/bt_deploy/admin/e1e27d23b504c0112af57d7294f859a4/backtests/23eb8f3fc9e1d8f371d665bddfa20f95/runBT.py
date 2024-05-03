from grtrader import BaseCtaStrategy
import MyStrategy

from grtrader import GrtBtEngine,EngineType
from grtrader import GrtBtAnalyst

def getStrategy():
    attrs = dir(MyStrategy)
    for symbol in attrs:
        tp = getattr(MyStrategy, symbol)
        if issubclass(tp, BaseCtaStrategy) and tp is not BaseCtaStrategy:
            return tp

    return None

def run_bt(code:str, fromTime:int, endTime:int, straid:str, init_capital:int=500000, slippage:int=0):
    StrategyType = getStrategy()
    if StrategyType is None:
        raise Exception("Module has no subtype of BaseCtaStrategy")
        return

    #创建一个运行环境，并加入策略
    engine = GrtBtEngine(EngineType.ET_CTA)
    engine.init('C:\\Users\\Twhp\\PycharmProjects\\GoldRushTrader\\example/common/', "configbt.yaml",
                commfile="stk_comms.json", contractfile="stocks.json")
    engine.configBacktest(fromTime, endTime)
    engine.configBTStorage(mode="csv", path="C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/storage")
    engine.commitBTConfig()

    straInfo = StrategyType(name=straid,code=code, barCnt=25, period="d", days=10, k1=0.1, k2=0.1, isForStk=False)
    engine.set_cta_strategy(straInfo, slippage)

    engine.run_backtest()
    print("engine回测完毕")
    analyst = GrtBtAnalyst()
    analyst.add_strategy(straid, folder="./outputs_bt/", init_capital=init_capital, rf=0.02, annual_trading_days=240)
    analyst.run_new()
    analyst.run_simple()

    engine.release_backtest()

if __name__ == "__main__":
    print("子进程开始运行")
    run_bt("SZSE.IDX.399660", 202305080900, 202307111515, "23eb8f3fc9e1d8f371d665bddfa20f95", 100000, 0)


# from wtpy import BaseCtaStrategy
# import MyStrategy
#
# from wtpy import WtBtEngine,EngineType
# from wtpy.apps import WtBtAnalyst
#
# def getStrategy():
#     attrs = dir(MyStrategy)
#     for symbol in attrs:
#         tp = getattr(MyStrategy, symbol)
#         if issubclass(tp, BaseCtaStrategy) and tp is not BaseCtaStrategy:
#             return tp
#
#     return None
#
# def run_bt(fromTime:int, endTime:int, straid:str, init_capital:int=500000, slippage:int=0):
#     StrategyType = getStrategy()
#     if StrategyType is None:
#         raise Exception("Module has no subtype of BaseCtaStrategy")
#         return
#
#     #创建一个运行环境，并加入策略
#     engine = WtBtEngine(EngineType.ET_CTA)
#     engine.init('../common/', "configbt.yaml")
#     engine.configBacktest(fromTime, endTime)
#     engine.configBTStorage(mode="csv", path="C:/Users/Twhp/Desktop/wtpy/demos/storage")
#     engine.commitBTConfig()
#
#     straInfo = StrategyType(name=straid,code="CFFEX.IF.HOT", barCnt=50, period="m5", days=30, k1=0.1, k2=0.1, isForStk=False)
#     engine.set_cta_strategy(straInfo, slippage)
#
#     engine.run_backtest()
#     print("engine回测完毕")
#     analyst = WtBtAnalyst()
#     analyst.add_strategy(straid, folder="./outputs_bt/", init_capital=init_capital, rf=0.02, annual_trading_days=240)
#     analyst.run_new()
#     analyst.run_simple()
#
#     engine.release_backtest()
#
# if __name__ == "__main__":
#     print("子进程开始运行")
#     run_bt(201812050900, 201903061515, "c0eff3b14a139f5707b90d68b97c18c3", 500000, 0)