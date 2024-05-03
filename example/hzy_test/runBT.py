from grtrader import GrtBtEngine, EngineType
from grtrader import GrtBtAnalyst

import sys
import time
import psutil


# 运行你的程序代码


sys.path.append('../Strategies')
from DualThrust import StraDualThrust
from RBreaker import StraRBreaker
if __name__ == "__main__":
    # 创建一个运行环境，并加入策略
    engine = GrtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(201501020930,201512311500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()

    '''
    创建DualThrust策略的一个实例
    name    策略实例名称
    code    回测使用的合约代码
    barCnt  要拉取的K线条数
    period  要使用的K线周期，m表示分钟线
    days    策略算法参数，算法引用的历史数据条数
    k1      策略算法参数，上边界系数
    k2      策略算法参数，下边界系数
    isForStk    DualThrust策略用于控制交易品种的代码
    '''
    # 主力合约回测
    # straInfo = StraDualThrust(name='DualTrust_analyst', code="CFFEX.IF.HOT", barCnt=50, period="m5", days=30, k1=0.5, k2=0.3,
    #                          isForStk=False)
    straInfo = StraDualThrust(name='pyIF_CFFEX.IC', code="CFFEX.IC.HOT", barCnt=30, period="d", days=5, k1=0.5, k2=0.3,
                              isForStk=False)
    # straInfo = StraRBreaker(name='RBreaker_analyst', code="CFFEX.IF.HOT", barCnt=50, period="m5", N=30, a=0.35, b=1.07, c=0.07,
    #                         d=0.25, cleartimes=[[1455, 1515]])
    '''
    @slippage       滑点大小
    @isRatioSlp     滑点是否是比例, 默认为False, 如果为True, 则slippage为万分比
    '''
    engine.set_cta_strategy(straInfo, slippage=0, isRatioSlp=False)

    # 开始运行回测
    start_time = time.process_time()
    engine.run_backtest(bAsync=False)
    # end_time = time.process_time()
    # cpu_time = end_time - start_time
    # print("程序的处理器时间为：", cpu_time)
    # process = psutil.Process()
    # memory_info = process.memory_info()
    # memory_usage = memory_info.rss / 1024 / 1024  # 转换为MB
    # print("程序的内存使用率为：", memory_usage, "MB")
    #
    # # 测试处理器使用率
    # cpu_usage = psutil.cpu_percent()
    # print("程序的处理器使用率为：", cpu_usage, "%")
    if True:
        # 创建绩效分析模块
        analyst = GrtBtAnalyst()
        # 将仿真的输出数据目录传递给绩效分析模块
        analyst.add_strategy("pyIF_CFFEX.IC", folder="./outputs_bt/", init_capital=500000, rf=0.02, annual_trading_days=240)
        # 运行绩效模块
        analyst.run_new()

    kw = input('press any key to exit ， this is fut\n')
    engine.release_backtest()
