from grtrader.webserve import GrtSimMon, GrtBtMon
from grtrader import GrtDtServo

def testSimMon():

    dtServo = GrtDtServo()
    # 这里配置的是基础数据文件目录
    dtServo.setBasefiles(folder="C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/common/",commfile="stk_comms.json", contractfile="stocks.json")

    # 这里配置的是数据目录
    dtServo.setStorage(path='C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/storage/')

    Mon = GrtSimMon(dtServo)
    btMon = GrtBtMon(deploy_folder="C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/test_websvr/bt_deploy",
                     logger=Mon.logger)  # 创建回测管理器
    Mon.set_bt_mon(btMon)  # 设置回测管理器
    Mon.run_as_server(port=18000, host="0.0.0.0")

testSimMon()
# 运行了服务以后，在浏览器打开以下网址即可使用
# http://127.0.0.1:18000/backtest/backtest.html
