import sqlite3
from .GrtLogger import GrtLogger

class UserMgr:
    def __init__(self, datafile:str="mondata.db", logger:GrtLogger=None):
        self.__grp_cache__ = dict()
        self.__logger__ = logger

        self.__db_conn__ = sqlite3.connect(datafile, check_same_thread=False)
        self.__check_db__()

        #加载组合列表
        cur = self.__db_conn__.cursor()
        self.__config__ = {
            "groups":{},
            "users":{}
        }

    def __check_db__(self):
        if self.__db_conn__ is None:
            return

        cur = self.__db_conn__.cursor()
        tables = []
        for row in cur.execute("select name from sqlite_master where type='table' order by name"):
            tables.append(row[0])

        if "actions" not in tables:
            sql = "CREATE TABLE [actions] (\n"
            sql += "[id] INTEGER PRIMARY KEY autoincrement, \n"
            sql += "[loginid] VARCHAR(20) NOT NULL DEFAULT '', \n"
            sql += "[actiontime] DATETIME default (datetime('now', 'localtime')), \n"
            sql += "[actionip] VARCHAR(30) NOT NULL DEFAULT '', \n"
            sql += "[actiontype] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[remark] TEXT default '');"
            cur.execute(sql)
            cur.execute("CREATE INDEX [idx_actions_loginid] ON [actions] ([loginid]);")
            cur.execute("CREATE INDEX [idx_actions_actiontime] ON [actions] ([actiontime]);")
            self.__db_conn__.commit()

        if "users" not in tables:
            sql = "CREATE TABLE [users] (\n"
            sql += "[id] INTEGER PRIMARY KEY autoincrement,\n"
            sql += "[loginid] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[name] VARCHAR(30) NOT NULL DEFAULT '',\n"
            sql += "[role] VARCHAR(10) NOT NULL DEFAULT '',\n"
            sql += "[passwd] VARCHAR(30) NOT NULL DEFAULT 'cta',\n"
            sql += "[iplist] VARCHAR(100) NOT NULL DEFAULT 'mannual',\n"
            sql += "[products] VARCHAR(256) NOT NULL DEFAULT 'mannual',\n"
            sql += "[remark] VARCHAR(256) NOT NULL DEFAULT '',\n"
            sql += "[createby] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[createtime] DATETIME default (datetime('now', 'localtime')),\n"
            sql += "[modifyby] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[modifytime] DATETIME default (datetime('now', 'localtime')));"
            cur.execute(sql)
            cur.execute("CREATE UNIQUE INDEX [idx_loginid] ON [users] ([loginid]);")

    def get_users(self):
        ret = []
        for loginid in self.__config__["users"]:
            usrInfo = self.__config__["users"][loginid]
            ret.append(usrInfo.copy())

        return ret

    def log_action(self, adminInfo, atype, remark):
        cur = self.__db_conn__.cursor()
        sql = "INSERT INTO actions(loginid,actiontime,actionip,actiontype,remark) VALUES('%s',datetime('now','localtime'),'%s','%s','%s');" % (
                adminInfo["loginid"], adminInfo["loginip"], atype, remark)
        cur.execute(sql)
        self.__db_conn__.commit()

    def get_user(self, loginid:str):
        if loginid in self.__config__["users"]:
            return self.__config__["users"][loginid].copy()
        elif loginid == 'superman':
            return {
                "loginid":loginid,
                "name":"超管",
                "role":"superman",
                "passwd":"25ed305a56504e95fd1ca9900a1da174",
                "iplist":"",
                "remark":"内置超管账号",
                'builtin':True,
                'products':''
            }
        else:
            return None