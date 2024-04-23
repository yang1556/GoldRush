from grtrader.webserve import GrtMonSvr

#如果要配置在线回测，则必须要配置WtDtServo
from grtrader import GrtDtServo
dtServo = GrtDtServo()
dtServo.setBasefiles("C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/common/")
dtServo.setStorage("C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/storage/")
dtServo.commitConfig()

# 创建监控服务，deploy_dir是策略组合部署的根目录
svr = GrtMonSvr(deploy_dir="./deploy")

#开启令牌访问，这样适合一些跨域访问的场景
#svr.enable_token(seckey="UM1kbkmdfpRdkBAt")

#将回测管理模块提交给GrtBtMon
from grtrader.webserve import GrtBtMon
btMon = GrtBtMon(deploy_folder="C:/Users/Twhp/PycharmProjects/GoldRushTrader/example/test_websvr/bt_deploy", logger=svr.logger) # 创建回测管理器
svr.set_bt_mon(btMon) # 设置回测管理器
svr.set_dt_servo(dtServo) # 设置dtservo

# 启动服务
svr.run(port=8099, bSync=False)
input("press enter key to exit\n")

# PC版控制台入口地址： http://127.0.0.1:8099/console
# 移动版控制台入口地址： http://127.0.0.1:8099/mobile