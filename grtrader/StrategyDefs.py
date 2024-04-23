from grtrader import CtaContext

class BaseCtaStrategy:
    '''
    CTA策略基础类，所有的策略都从该类派生
    包含了策略的基本开发框架
    '''
    def __init__(self, name:str):
        self.__name__ = name
        
    
    def name(self) -> str:
        return self.__name__


    def on_init(self, context:CtaContext):
        '''
        策略初始化，启动的时候调用
        用于加载自定义数据

        @context    策略运行上下文
        '''
        return

    def on_session_begin(self, context:CtaContext, curTDate:int):
        '''
        交易日开始事件

        @curTDate   交易日，格式为20210220
        '''
        return

    def on_session_end(self, context:CtaContext, curTDate:int):
        '''
        交易日结束事件

        @curTDate   交易日，格式为20210220
        '''
        return
    
    def on_calculate(self, context:CtaContext):
        '''
        K线闭合时调用，一般作为策略的核心计算模块

        @context    策略运行上下文
        '''
        return

    def on_calculate_done(self, context:CtaContext):
        '''
        K线闭合时调用，一般作为策略的核心计算模块

        @context    策略运行上下文
        '''
        return


    def on_tick(self, context:CtaContext, stdCode:str, newTick:dict):
        '''
        逐笔数据进来时调用
        生产环境中，每笔行情进来就直接调用
        回测环境中，是模拟的逐笔数据

        @context    策略运行上下文
        @stdCode    合约代码
        @newTick    最新逐笔
        '''
        return

    def on_bar(self, context:CtaContext, stdCode:str, period:str, newBar:dict):
        '''
        K线闭合时回调

        @context    策略上下文
        @stdCode    合约代码
        @period     K线周期
        @newBar     最新闭合的K线
        '''
        return

    def on_backtest_end(self, context:CtaContext):
        '''
        回测结束时回调，只在回测框架下会触发

        @context    策略上下文
        '''
        return

    def on_condition_triggered(self, context:CtaContext, stdCode:str, target:float, price:float, usertag:str):
        '''
        条件单触发回调

        @context    策略上下文
        @stdCode    合约代码
        @target     触发以后的最终目标仓位
        @price      触发价格
        @usertag    用户标记
        '''
        return

