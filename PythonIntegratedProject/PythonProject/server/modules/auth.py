# -*- coding: utf-8 -*-
# 注册与登陆
import os
from conf import settings
from modules.log import Logger
from modules.MysqlHelper import MysqlHelper


class Auth:
    def __init__(self, user, pwd, *email):
        self.user = user
        self.pwd = pwd
        if email is not None:
            self.email = email

    def register(self):
        sql = "SELECT user from userinfos where user = %s "
        params = [self.user]
        helper = MysqlHelper()
        result = helper.fetchone(sql, params)
        if result == None:
            user_home_path = os.path.join(settings.HOME_PATH, self.user)
            if not os.path.isdir(user_home_path):
                os.makedirs(user_home_path)
            sql = 'insert into userinfos(user, pwd, email, home_path, limit_size) values(%s,%s,%s,%s,%s)'
            params = [self.user, self.pwd, self.email, user_home_path, settings.LIMIT_SIZE]
            helper = MysqlHelper()
            row = helper.insert(sql, params)
            # print(row)
            Logger.info('[%s]注册成功。' % self.user)
            return '201'
        else:
            Logger.warning('[%s]注册用户名已存在。' % self.user)
            return '401'

    def login(self):
        sql = "SELECT user,pwd from userinfos where user = %s "
        params = [self.user]
        helper = MysqlHelper()
        result = helper.fetchone(sql, params)
        if result[0] is not None:
            if self.pwd == result[1]:
                sql = 'select user, email, home_path, limit_size from userinfos where user = %s'
                helper = MysqlHelper()
                user_dict = helper.fetchone(sql, params)
                Logger.info('[%s]登录成功.' % self.user)
                return user_dict
            else:
                Logger.error('[%s]用户名或密码错误.' % self.user)

        else:
            Logger.warning('[%s]登录用户不存在.' % self.user)


