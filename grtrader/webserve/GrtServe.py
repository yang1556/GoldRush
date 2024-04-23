from fastapi import FastAPI, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, FileResponse
import uvicorn

import json
import yaml
import datetime
import os
import hashlib
import sys
import chardet
import pytz
import base64

from .GrtLogger import GrtLogger
from .UserMgr import UserMgr #backup_file
# from .PushSvr import PushServer
# from .WatchDog import WatchDog, WatcherSink
from .GrtBtSer import GrtBtMon
from grtrader import GrtDtServo
import signal
import platform
from pydantic import BaseModel
class Userlog(BaseModel):
    loginid: str
    passwd : str

def get_session(request: Request, key: str):
    if key not in request["session"]:
        return None
    return request["session"][key]

def set_session(request: Request, key: str, val):
    request["session"][key] = val

def pop_session(request: Request, key: str):
    if key not in request["session"]:
        return
    request["session"].pop(key)

# def AES_Encrypt(key:str, data:str):
#     from Crypto.Cipher import AES # pip install pycryptodome
#     vi = '0102030405060708'
#     pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
#     data = pad(data)
#     # 字符串补位
#     cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
#     encryptedbytes = cipher.encrypt(data.encode('utf8'))
#     # 加密后得到的是bytes类型的数据
#     encodestrs = base64.b64encode(encryptedbytes)
#     # 使用Base64进行编码,返回byte字符串
#     enctext = encodestrs.decode('utf8')
#     # 对byte字符串按utf-8进行解码
#     return enctext
#
# def AES_Decrypt(key:str, data:str):
#     from Crypto.Cipher import AES # pip install pycryptodome
#     vi = '0102030405060708'
#     data = data.encode('utf8')
#     encodebytes = base64.decodebytes(data)
#     # 将加密数据转换位bytes类型数据
#     cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
#     text_decrypted = cipher.decrypt(encodebytes)
#     unpad = lambda s: s[0:-s[-1]]
#     text_decrypted = unpad(text_decrypted)
#     # 去补位
#     text_decrypted = text_decrypted.decode('utf8')
#     return text_decrypted


# 获取文件最后N行的函数
def get_tail(filename, N: int = 100, encoding="GBK"):
    filesize = os.path.getsize(filename)
    blocksize = 10240
    dat_file = open(filename, 'r', encoding=encoding)
    last_line = ""
    if filesize > blocksize:
        maxseekpoint = (filesize // blocksize)
        dat_file.seek((maxseekpoint - 1) * blocksize)
    elif filesize:
        dat_file.seek(0, 0)
    lines = dat_file.readlines()
    if lines:
        last_line = lines[-N:]
    dat_file.close()
    return ''.join(last_line), len(last_line)

def check_auth(request: Request, token:str = None, seckey:str = None):
    if token is None:
        tokeninfo = get_session(request, "tokeninfo")
        # session里没有用户信息
        if tokeninfo is None:
            return False, {
                "result": -999,
                "message": "请先登录"
            }

        # session里有用户信息，则要读取
        exptime = tokeninfo["expiretime"]
        now = datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC')).strftime("%Y.%m.%d %H:%M:%S")
        if now > exptime:
            return False, {
                "result": -999,
                "message": "登录已超时，请重新登录"
            }

        return True, tokeninfo
    else:
        tokeninfo = AES_Decrypt(seckey, token)
        # session里没有用户信息
        if tokeninfo is None:
            return False, {
                "result": -999,
                "message": "请先登录"
            }

        # session里有用户信息，则要读取
        exptime = tokeninfo["expiretime"]
        now = datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC')).strftime("%Y.%m.%d %H:%M:%S")
        if now > exptime:
            return False, {
                "result": -999,
                "message": "登录已超时，请重新登录"
            }

        return True, tokeninfo


from fastapi.middleware.cors import CORSMiddleware

class GrtMonSvr():

    def __init__(self, static_folder: str = "static/", deploy_dir="C:/", #sink: GrtMonSink = None,
                 notifyTimeout: bool = True):
        '''
        GrtMonSvr构造函数

        @static_folder      静态文件根目录
        @static_url_path    静态文件访问路径
        @deploy_dir         实盘部署目录
        '''

        self.logger = GrtLogger(__name__, "GrtServe.log")
        #self._sink_ = sink

        # 数据管理器，主要用于缓存各组合的数据
        self.__user_data__ = UserMgr('data.db', logger=self.logger)

        self.__bt_mon__: GrtBtMon = None
        self.__dt_servo__: GrtDtServo = None

        # 秘钥和开启token访问，单独控制，减少依赖项
        self.__sec_key__ = ""
        self.__token_enabled__ = False

        # 看门狗模块，主要用于调度各个组合启动关闭
        #self._dog = WatchDog(sink=self, db=self.__data_mgr__.get_db(), logger=self.logger)

        app = FastAPI(title="GrtMonSvr", description="A http api of GrtMonSvr", redoc_url=None, version="1.0.0")
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        app.add_middleware(SessionMiddleware, secret_key='!@#$%^&*()', max_age=25200, session_cookie='GrtMonSvr_sid')
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"])

        script_dir = os.path.dirname(__file__)
        static_folder = os.path.join(script_dir, static_folder)
        target_dir = os.path.join(static_folder, "console")
        print("path:", target_dir)
        app.mount("/console", StaticFiles(directory=target_dir), name="console")

        self.app = app
        self.worker = None
        self.deploy_dir = deploy_dir
        self.deploy_tree = None
        self.static_folder = static_folder
        self.notifyTimeout = notifyTimeout

        #self.push_svr = PushServer(app, self.__data_mgr__, self.logger)

        self.init_mgr_apis(app)
        self.init_comm_apis(app)

    def enable_token(self, seckey: str = "WtMonSvr@2021"):
        '''
        启用访问令牌, 默认通过session方式验证
        注意: 这里如果启用令牌访问的话, 需要安装pycryptodome, 所以改成单独控制
        '''

        self.__sec_key__ = seckey
        self.__token_enabled__ = True

    def set_bt_mon(self, btMon: GrtBtMon):
        '''
        设置回测管理器

        @btMon      回测管理器WtBtMon实例
        '''
        self.__bt_mon__ = btMon
        self.init_bt_apis(self.app)

    def set_dt_servo(self, dtServo: GrtDtServo):
        '''
        设置DtServo

        @dtServo    本地数据伺服WtDtServo实例
        '''
        self.__dt_servo__ = dtServo

    def init_bt_apis(self, app: FastAPI):

        # 拉取K线数据
        @app.post("/bt/qrybars", tags=["回测管理接口"])
        async def qry_bt_bars(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                code: str = Body(..., title="合约代码", embed=True),
                period: str = Body(..., title="K线周期", embed=True),
                stime: int = Body(None, title="开始时间", embed=True),
                etime: int = Body(..., title="结束时间", embed=True),
                count: int = Body(None, title="数据条数", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if self.__dt_servo__ is None:
                ret = {
                    "result": -2,
                    "message": "没有配置数据伺服"
                }
                return ret

            stdCode = code
            fromTime = stime
            dataCount = count
            endTime = etime

            bars = self.__dt_servo__.get_bars(stdCode=stdCode, period=period, fromTime=fromTime, dataCount=dataCount,
                                              endTime=endTime)
            #print(type(bars[0]))
            # print(bars[0])
            # print(bars[1])
            if bars is None:
                ret = {
                    "result": -2,
                    "message": "Data not found"
                }
            else:
                bar_list = list()
                for realBar in bars:
                    bar = dict()

                    bar["date"] = int(realBar[0])
                    bar["time"] = int(realBar[2])
                    # print(type(realBar[0]))
                    bar["open"] = float(realBar[3])
                    bar["high"] = float(realBar[4])
                    bar["low"] = float(realBar[5])
                    bar["close"] = float(realBar[6])
                    bar["volume"] = float(realBar[9])
                    # bar["turnover"] = float(realBar[2])
                    bar_list.append(bar)
                # bar_list = [curBar.to_dict for curBar in bars]

                ret = {
                    "result": 0,
                    "message": "Ok",
                    "bars": bar_list
                }

            return ret

        # 拉取用户策略列表
        @app.post("/bt/qrystras", tags=["回测管理接口"])
        @app.get("/bt/qrystras", tags=["回测管理接口"])
        async def qry_my_stras(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            ret = {
                "result": 0,
                "message": "OK",
                "strategies": self.__bt_mon__.get_strategies(user)
            }

            return ret

        # 拉取策略代码
        @app.post("/bt/qrycode", tags=["回测管理接口"])
        async def qry_stra_code(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略代码不存在"
                    }
                else:
                    content = self.__bt_mon__.get_strategy_code(user, straid)
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "content": content
                    }

            return ret

        # 提交策略代码
        @app.post("/bt/setcode", tags=["回测管理接口"])
        def set_stra_code(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                content: str = Body(..., title="策略代码", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(content) == 0 or len(straid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和代码不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = self.__bt_mon__.set_strategy_code(user, straid, content)
                    if ret:
                        ret = {
                            "result": 0,
                            "message": "OK"
                        }
                    else:
                        ret = {
                            "result": -3,
                            "message": "保存策略代码失败"
                        }

            return ret

        # 添加用户策略
        @app.post("/bt/addstra", tags=["回测管理接口"])
        async def cmd_add_stra(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                name: str = Body(..., title="策略名称", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(name) == 0:
                ret = {
                    "result": -2,
                    "message": "策略名称不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -3,
                    "message": "回测管理器未配置"
                }
                return ret
            #user = "admin"
            straInfo = self.__bt_mon__.add_strategy(user, name)
            if straInfo is None:
                ret = {
                    "result": -4,
                    "message": "策略添加失败"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "OK",
                    "strategy": straInfo
                }

            return ret

        # 删除用户策略
        @app.post("/bt/delstra", tags=["回测管理接口"])
        async def cmd_del_stra(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = self.__bt_mon__.del_strategy(user, straid)
                    if ret:
                        ret = {
                            "result": 0,
                            "message": "OK"
                        }
                    else:
                        ret = {
                            "result": -3,
                            "message": "保存策略代码失败"
                        }

            return ret

        # 获取策略回测列表
        @app.post("/bt/qrystrabts", tags=["回测管理接口"])
        async def qry_stra_bts(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "backtests": self.__bt_mon__.get_backtests(user, straid)
                    }

            return ret

        # 获取策略回测信号
        @app.post("/bt/qrybtsigs", tags=["回测管理接口"])
        async def qry_stra_bt_signals(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0 or len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "signals": self.__bt_mon__.get_bt_signals(user, straid, btid)
                    }

            return ret

        # 删除策略回测列表
        @app.post("/bt/delstrabt", tags=["回测管理接口"])
        async def cmd_del_stra_bt(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                self.__bt_mon__.del_backtest(user, btid)
                ret = {
                    "result": 0,
                    "message": "OK"
                }

            return ret

        # 获取策略回测成交
        @app.post("/bt/qrybttrds", tags=["回测管理接口"])
        async def qry_stra_bt_trades(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0 or len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "trades": self.__bt_mon__.get_bt_trades(user, straid, btid)
                    }

            return ret

        # 获取策略回测资金
        @app.post("/bt/qrybtfunds", tags=["回测管理接口"])
        async def qry_stra_bt_funds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0 or len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "funds": self.__bt_mon__.get_bt_funds(user, straid, btid)
                    }

            return ret

        # 获取策略回测回合
        @app.post("/bt/qrybtrnds", tags=["回测管理接口"])
        async def qry_stra_bt_rounds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0 or len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "rounds": self.__bt_mon__.get_bt_rounds(user, straid, btid)
                    }

            return ret

        # 启动策略回测
        @app.post("/bt/runstrabt", tags=["回测管理接口"])
        def cmd_run_stra_bt(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                stime: int = Body(None, title="开始时间", embed=True),
                etime: int = Body(None, title="结束时间", embed=True),
                capital: int = Body(500000, title="本金", embed=True),
                slippage: int = Body(0, title="滑点", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            curDt = int(datetime.datetime.now().strftime("%Y%m%d"))
            fromtime = stime
            endtime = etime

            if len(straid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID不能为空"
                }
                return ret

            if fromtime > endtime:
                fromtime, endtime = endtime, fromtime

            fromtime = fromtime * 10000 + 900
            endtime = endtime * 10000 + 1515

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    btInfo = self.__bt_mon__.run_backtest(user, straid, fromtime, endtime, capital, slippage)
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "backtest": btInfo
                    }

            return ret

    def init_mgr_apis(self, app: FastAPI):

        '''下面是API接口的编写'''

        @app.post("/mgr/login", tags=["用户接口"])
        async def cmd_login(
                request: Request,
                loginid: str = Body(..., title="用户名", embed=True),
                passwd: str = Body(..., title="用户密码", embed=True)
        ):
            if True:
                user = loginid
                pwd = passwd
                print("收到消息")
                print(user,pwd)
                if len(user) == 0 or len(pwd) == 0:
                    ret = {
                        "result": -1,
                        "message": "用户名和密码不能为空"
                    }
                else:
                    encpwd = hashlib.md5((user + pwd).encode("utf-8")).hexdigest()
                    now = datetime.datetime.now()
                    usrInf = self.__user_data__.get_user(user)
                    if usrInf is None or encpwd != usrInf["passwd"]:
                        ret = {
                            "result": -1,
                            "message": "用户名或密码错误"
                        }
                    else:
                        usrInf.pop("passwd")
                        usrInf["loginip"] = request.client.host
                        usrInf["logintime"] = now.strftime("%Y/%m/%d %H:%M:%S")
                        products = usrInf["products"]

                        exptime = now + datetime.timedelta(minutes=360)  # 360分钟令牌超时
                        tokenInfo = {
                            "loginid": user,
                            "role": usrInf["role"],
                            "logintime": now.strftime("%Y/%m/%d %H:%M:%S"),
                            "expiretime": exptime.replace(tzinfo=pytz.timezone('UTC')).strftime("%Y.%m.%d %H:%M:%S"),
                            "products": products,
                            "loginip": request.client.host
                        }
                        set_session(request, "tokeninfo", tokenInfo)

                        if self.__token_enabled__:
                            token = AES_Encrypt(self.__sec_key__, json.dumps(tokenInfo))
                            ret = {
                                "result": 0,
                                "message": "Ok",
                                "userinfo": usrInf,
                                "token": token
                            }
                        else:
                            ret = {
                                "result": 0,
                                "message": "Ok",
                                "userinfo": usrInf
                            }

                        self.__user_data__.log_action(usrInf, "login", json.dumps(request.headers.get('User-Agent')))
            else:
                ret = {
                    "result": -1,
                    "message": "请求处理出现异常",
                }
                if get_session(request, "userinfo") is not None:
                    pop_session("userinfo")

            return ret

        # 修改密码
        # 修改密码
        @app.post("/mgr/modpwd", tags=["用户接口"])
        async def mod_pwd(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                oldpwd: str = Body(..., title="旧密码", embed=True),
                newpwd: str = Body(..., title="新密码", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            if len(oldpwd) == 0 or len(newpwd) == 0:
                ret = {
                    "result": -1,
                    "message": "新旧密码都不能为空"
                }
            else:
                user = adminInfo["loginid"]
                oldencpwd = hashlib.md5((user + oldpwd).encode("utf-8")).hexdigest()
                usrInf = self.__data_mgr__.get_user(user)
                if usrInf is None:
                    ret = {
                        "result": -1,
                        "message": "用户不存在"
                    }
                else:
                    if oldencpwd != usrInf["passwd"]:
                        ret = {
                            "result": -1,
                            "message": "旧密码错误"
                        }
                    else:
                        if 'builtin' in usrInf and usrInf["builtin"]:
                            # 如果是内建账号要改密码，则先添加用户
                            usrInf["passwd"] = oldpwd
                            self.__data_mgr__.add_user(usrInf, user)
                            print("%s是内建账户，自动添加到数据库中" % user)

                        newencpwd = hashlib.md5((user + newpwd).encode("utf-8")).hexdigest()
                        self.__data_mgr__.mod_user_pwd(user, newencpwd, user)

                        ret = {
                            "result": 0,
                            "message": "Ok"
                        }

            return ret

        # 查询用户列表
        @app.post("/mgr/qryusers", tags=["系统管理接口"])
        @app.get("/mgr/qryusers", tags=["系统管理接口"])
        async def qry_users(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            users = self.__data_mgr__.get_users()
            for usrInfo in users:
                usrInfo.pop("passwd")

            ret = {
                "result": 0,
                "message": "",
                "users": users
            }

            return ret

        # 提交用户信息
        @app.post("/mgr/cmtuser", tags=["系统管理接口"])
        async def cmd_commit_user(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                loginid: str = Body(..., title="登录名", embed=True),
                name: str = Body(..., title="用户姓名", embed=True),
                passwd: str = Body("", title="登录密码", embed=True),
                role: str = Body("", title="用户角色", embed=True),
                iplist: str = Body("", title="限定ip", embed=True),
                products: list = Body([], title="产品列表", embed=True),
                remark: str = Body("", title="备注信息", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            userinfo = {
                "loginid": loginid,
                "name": name,
                "passwd": passwd,
                "role": role,
                "iplist": iplist,
                "products": ",".join(products),
                "remark": remark
            }

            self.__data_mgr__.add_user(userinfo, adminInfo["loginid"])
            ret = {
                "result": 0,
                "message": "Ok"
            }

            self.__data_mgr__.log_action(adminInfo, "cmtuser", json.dumps(userinfo))

            return ret

        # 删除用户
        @app.post("/mgr/deluser", tags=["系统管理接口"])
        async def cmd_delete_user(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                loginid: str = Body(..., title="用户名", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            if self.__data_mgr__.del_user(loginid, adminInfo["loginid"]):
                self.__data_mgr__.log_action(adminInfo, "delusr", loginid)
            ret = {
                "result": 0,
                "message": "Ok"
            }

            return ret

        # 修改密码
        @app.post("/mgr/resetpwd", tags=["系统管理接口"])
        async def reset_pwd(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                loginid: str = Body(..., title="用户名", embed=True),
                passwd: str = Body(..., title="新密码", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            user = loginid
            pwd = passwd

            if len(pwd) == 0 or len(user) == 0:
                ret = {
                    "result": -1,
                    "message": "密码都不能为空"
                }
            else:
                encpwd = hashlib.md5((user + pwd).encode("utf-8")).hexdigest()
                usrInf = self.__data_mgr__.get_user(user)
                if usrInf is None:
                    ret = {
                        "result": -1,
                        "message": "用户不存在"
                    }
                else:
                    self.__data_mgr__.mod_user_pwd(user, encpwd, adminInfo["loginid"])
                    self.__data_mgr__.log_action(adminInfo, "resetpwd", loginid)
                    ret = {
                        "result": 0,
                        "message": "Ok"
                    }

            return ret


    def init_comm_apis(self, app: FastAPI):
        @app.get("/console")
        async def console_entry():
            return RedirectResponse("/console/index.html")

        @app.get("/favicon.ico")
        async def favicon_entry():
            return FileResponse(os.path.join(self.static_folder, "favicon.ico"))

        @app.get("/hasbt")
        @app.post("/hasbt")
        async def check_btmon():
            if self.__bt_mon__ is None:
                return {
                    "result": -1,
                    "message": "不支持在线回测"
                }
            else:
                return {
                    "result": 0,
                    "message": "Ok"
                }

    def __run_impl__(self, port: int, host: str):
        # TODO
        #self._dog.run()
        #self.push_svr.run()
        uvicorn.run(self.app, port=port, host=host)

    def run(self, port: int = 8080, host="0.0.0.0", bSync: bool = True):
        # TODO
        # 仅linux生效，在linux中，子进程会一直等待父进程处理其结束信号才能释放，如果不加这一句忽略子进程的结束信号，子进程就无法结束
        # if not isWindows():
        #     signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        if bSync:
            self.__run_impl__(port, host)
        else:
            import threading
            self.worker = threading.Thread(target=self.__run_impl__, args=(port, host,))
            self.worker.setDaemon(True)
            self.worker.start()

    def init_logging(self):
        pass

    def on_start(self, grpid: str):
        if self.__data_mgr__.has_group(grpid):
            self.push_svr.notifyGrpEvt(grpid, 'start')

    def on_stop(self, grpid: str, isErr: bool):
        if self.__data_mgr__.has_group(grpid):
            self.push_svr.notifyGrpEvt(grpid, 'stop')

        # 如果是错误，要通知管理员
        if isErr and self._sink_:
            grpInfo = self.__data_mgr__.get_group(grpid)
            self._sink_.notify("fatal", "检测到 %s[%s] 意外停止, 请及时处理!!!" % (grpInfo["name"], grpid))

    def on_output(self, grpid: str, tag: str, time: int, message: str):
        if self.__data_mgr__.has_group(grpid):
            self.push_svr.notifyGrpLog(grpid, tag, time, message)

    def on_order(self, grpid: str, chnl: str, ordInfo: dict):
        self.push_svr.notifyGrpChnlEvt(grpid, chnl, 'order', ordInfo)

    def on_trade(self, grpid: str, chnl: str, trdInfo: dict):
        self.push_svr.notifyGrpChnlEvt(grpid, chnl, 'trade', trdInfo)

    def on_notify(self, grpid: str, chnl: str, message: str):
        self.push_svr.notifyGrpChnlEvt(grpid, chnl, 'notify', message)

    def on_timeout(self, grpid: str):
        if not self.notifyTimeout:
            return

        if self._sink_:
            grpInfo = self.__data_mgr__.get_group(grpid)
            self._sink_.notify("fatal", f'检测到 {grpInfo["name"]}[{grpid}]的MQ消息超时，请及时检查并处理!!!')