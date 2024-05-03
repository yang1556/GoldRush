from grtrader import GrtDtServo
# dtServo = GrtDtServo()
# dtServo.setBasefiles("C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/common/")
# dtServo.setStorage("C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/storage/")
# dtServo.commitConfig()
#
#
# from wtpy import WtDtServo

dtServo = GrtDtServo()
dtServo.setBasefiles(folder="../common/", commfile="stk_comms.json", contractfile="stocks.json")
dtServo.setStorage(path='C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/storage/')

# 读取IF主力合约的前复权数据
# bars = dtServo.get_bars("SSE.ETF.510300", "m5", fromTime=2018010010930, endTime=201810021500)
# print(bars[0])
# print(bars.bartimes)
bars1 = dtServo.get_bars("SZSE.IDX.399660", "d", fromTime=202307140900, endTime=202307160900)
print(bars1)