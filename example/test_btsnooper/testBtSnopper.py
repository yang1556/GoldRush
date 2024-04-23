from grtrader.webserve import GrtBtSnooper
from grtrader import GrtDtServo

def testBtSnooper():    

    dtServo = GrtDtServo()
    # 这里配置的是基础数据文件目录
    dtServo.setBasefiles(folder="C:/Users/Twhp/Desktop/wtpy/demos/common/")

    # 这里配置的是datakit落地的数据目录
    dtServo.setStorage(path='C:/Users/Twhp/Desktop/wtpy/demos/storage/')

    snooper = GrtBtSnooper(dtServo)
    snooper.run_as_server(port=8082, host="0.0.0.0")

testBtSnooper()
# 运行了服务以后，在浏览器打开以下网址即可使用
# http://127.0.0.1:8082/backtest/backtest.html
