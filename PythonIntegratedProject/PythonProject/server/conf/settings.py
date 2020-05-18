# -*- coding: utf-8 -*-
# 配置
import os

BASE_DIR = os.path.dirname(os.getcwd())

HOME_PATH = os.path.join(BASE_DIR, 'home')    # 服务端用户文件目录
LOG_PATH = os.path.join(BASE_DIR, 'logs')     # 日志文件目录
Shared_PATH = os.path.join(BASE_DIR, 'sharedspace')  # 共享空间目录
Message_FILE = os.path.join(BASE_DIR, 'Records', 'MessageRecord.txt')  # 聊天消息缓存


LOG_SIZE = 102400
LOG_NUM = 100

LIMIT_SIZE = 10240000000  # 每个用户默认空间限额约10M,可手动修改

IP_PORT = ('localhost', 8080)

