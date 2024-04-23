import sys
import time
from grtrader.ExtModuleDefs import BaseExtDataLoader
from ctypes import POINTER
from grtrader.GrtCoreDefs import GRTSBarStruct, GRTSTickStruct

import pandas as pd

import random

from grtrader import GrtBtEngine,EngineType
from grtrader import GrtBtAnalyst

sys.path.append('../Strategies')

from DualThrust import StraDualThrust

class MyDataLoader(BaseExtDataLoader):
    
    def load_final_his_bars(self, stdCode:str, period:str, feeder) -> bool:
        '''
        加载历史K线（回测、实盘）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @period     周期，m1/m5/d1
        @feeder     回调函数，feed_raw_bars(bars:POINTER(WTSBarStruct), count:int, factor:double)
        '''
        print("loading %s bars of %s from extended loader" % (period, stdCode))

        df = pd.read_csv('../storage/csv/CFFEX.IF.HOT_m5.csv')
        df = df.rename(columns={
            '<Date>':'date',
            ' <Time>':'time',
            ' <Open>':'open',
            ' <High>':'high',
            ' <Low>':'low',
            ' <Close>':'close',
            ' <Volume>':'vol',
            })
        df['date'] = df['date'].astype('datetime64[s]').dt.strftime('%Y%m%d').astype('int64')
        df['time'] = (df['date']-19900000)*10000 + df['time'].str.replace(':', '').str[:-2].astype('int')

        BUFFER = GRTSBarStruct*len(df)
        buffer = BUFFER()

        def assign(procession, buffer):
            tuple(map(lambda x: setattr(buffer[x[0]], procession.name, x[1]), enumerate(procession)))


        df.apply(assign, buffer=buffer)
        print(df)
        print(buffer[0].to_dict)
        print(buffer[-1].to_dict)

        feeder(buffer, len(df))
        return True


def test_in_bt():
    engine = GrtBtEngine(EngineType.ET_CTA)

    # 初始化之前，向回测框架注册加载器
    engine.set_extended_data_loader(loader=MyDataLoader(), bAutoTrans=False)

    engine.init('../common/', "configbt.yaml")

    engine.configBacktest(201909100930,201912011500)
    #engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()

    straInfo = StraDualThrust(name='pydt_IF', code="CFFEX.IF.HOT", barCnt=50, period="m5", days=30, k1=0.1, k2=0.1, isForStk=False)
    engine.set_cta_strategy(straInfo)

    engine.run_backtest()

    analyst = GrtBtAnalyst()
    analyst.add_strategy("pydt_IF", folder="./outputs_bt/", init_capital=500000, rf=0.02, annual_trading_days=240)
    analyst.run()

    kw = input('press any key to exit\n')
    engine.release_backtest()


test_in_bt()