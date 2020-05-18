# -*- coding: utf-8 -*-
#  核心服务
import os
import socketserver
import subprocess
from os.path import getsize, join

from conf.settings import Message_FILE, Shared_PATH, LIMIT_SIZE
from modules.MysqlHelper import MysqlHelper
from modules.auth import Auth
from modules.log import Logger


class MyServer(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            while True:
                auth_info = self.request.recv(1024).decode()
                # auth_type, user, pwd, email
                n = auth_info.count(':')
                if n == 2:
                    auth_type, user, pwd = auth_info.split(':')
                    auth_user = Auth(user, pwd)
                else:
                    auth_type, user, pwd, email = auth_info.split(':')
                    auth_user = Auth(user, pwd, email)
                if auth_type == 'register':
                    status_code = auth_user.register()
                    self.request.sendall(status_code.encode())
                elif auth_type == 'login':
                    user_dict = auth_user.login()
                    if user_dict:
                        self.request.sendall(b'200')
                        self.user_name = user_dict[0]
                        self.user_current_path = user_dict[2]
                        self.user_home_path = user_dict[2]
                        self.user_limit_size = int(user_dict[3])
                        while True:
                            opt = self.request.recv(1024).decode()
                            if opt == '1':
                                self.chat()
                            elif opt == '2':
                                email= self.getmail(self.user_name)
                                self.request.sendall(email.encode())
                            elif opt == '3':
                                email = self.getmail(self.user_name)
                                print(self.user_name)
                                print(email)
                                self.request.sendall(email.encode())
                            elif opt == '4':
                                receiver = self.request.recv(1024).decode()
                                file = self.request.recv(1024).decode()
                                self.recvfile(receiver,file)
                            elif opt == '5':
                                self.user_current_path = Shared_PATH
                                self.user_home_path = Shared_PATH
                                self.user_limit_size = LIMIT_SIZE
                                while True:
                                    command = self.request.recv(1024).decode()
                                    print(command)
                                    command_str = command.split()[0]
                                    if hasattr(self, command_str):
                                        func = getattr(self, command_str)
                                        func(command)
                            elif opt == '6':
                                while True:
                                    command = self.request.recv(1024).decode()
                                    print(command)
                                    command_str = command.split()[0]
                                    if hasattr(self, command_str):
                                        func = getattr(self, command_str)
                                        func(command)
                            else:
                                pass
                    else:
                        self.request.sendall(b'400')
        except ConnectionResetError as e:
            print('Error:', e)

    def chat(self):
        op = self.request.recv(1024).decode()
        if op == '0101':
            content = self.request.recv(1024).decode()
            msg = '[来自' + self.user_name + ':]' + content
            print(msg)
            MyServer.file_oper(Message_FILE, 'wt', msg)
        elif op == '0202':
            msg = MyServer.file_oper(Message_FILE, 'r')
            if msg is None:
                msg = '无消息！'
            self.request.sendall(msg.encode())

    def dir(self, command):
        if len(command.split()) == 1:
            Logger.info('[%s] 执行成功.' % command)
            self.request.sendall(b'202')
            response = self.request.recv(1024)
            cmd_res = subprocess.Popen('dir %s' % self.user_current_path, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, shell=True)
            stdout = cmd_res.stdout.read()
            stderr = cmd_res.stderr.read()
            result = stdout if stdout else stderr
            self.request.sendall(result)
        else:
            Logger.warning('[%s] 命令格式错误.' % command)
            self.request.sendall(b'402')

    def pwd(self, command):
        if len(command.split()) == 1:
            self.request.sendall(b'202')
            Logger.info('[%s] 执行成功.' % command)
            response = self.request.recv(1024)
            self.request.sendall(self.user_current_path.encode())
        else:
            Logger.warning('[%s] 命令格式错误.' % command)
            self.request.sendall(b'402')

    def mkdir(self, command):
        if len(command.split()) > 1:
            dir_name = command.split()[1]
            dir_path = os.path.join(self.user_current_path, dir_name)
            if not os.path.isdir(dir_path):
                Logger.info('[%s] 执行成功.' % command)
                self.request.sendall(b'202')
                response = self.request.recv(1024)
                os.makedirs(dir_path)
            else:
                Logger.warning('[%s] 命令格式错误.' % command)
                self.request.sendall(b'402')

    def cd(self, command):
        if len(command.split()) > 1:
            dir_name = command.split()[1]
            dir_path = os.path.join(self.user_current_path, dir_name)
            if dir_name == '..' and len(self.user_current_path) > len(self.user_home_path):
                self.request.sendall(b'202')
                response = self.request.recv(1024)
                self.user_current_path = os.path.dirname(self.user_current_path)
            elif os.path.isdir(dir_path):
                self.request.sendall(b'202')
                response = self.request.recv(1024)
                if dir_name != '.' and dir_name != '..':
                    self.user_current_path = dir_path
            else:
                self.request.sendall(b'403')
        else:
            Logger.warning('[%s] 命令格式错误.' % command)
            self.request.sendall(b'402')

    def put(self, command):
        filename = command.split()[1]
        file_path = os.path.join(self.user_current_path, filename)
        response = self.request.sendall(b'000')
        file_size = self.request.recv(1024).decode()
        file_size = int(file_size)
        used_size = self.getdirsize(self.user_home_path)
        if self.user_limit_size > file_size + used_size:
            self.request.sendall(b'202')
            Logger.info('[%s] 执行成功.' % command)
            recv_size = 0
            Logger.info('[%s] 文件开始上传.' % file_path)
            with open(file_path, 'wb') as f:
                while recv_size != file_size:
                    data = self.request.recv(1024)
                    recv_size += len(data)
                    f.write(data)
            Logger.info('[%s] 文件上传完成.' % file_path)
        else:
            self.request.sendall(b'403')

    def getdirsize(self, user_home_path):
        size = 0
        for root, dirs, files in os.walk(user_home_path):
            size += sum([getsize(join(root, name)) for name in files])
        return size

    def get(self, command):
        if len(command.split()) > 1:
            filename = command.split()[1]
            file_path = os.path.join(self.user_current_path, filename)
            if os.path.isfile(file_path):
                self.request.sendall(b'202')
                file_size = os.path.getsize(file_path)
                status_code = self.request.recv(1024).decode()
                if status_code == '406':
                    self.request.sendall(b'000')
                    recv_size = int(self.request.recv(1024).decode())
                    if file_size > recv_size:
                        self.request.sendall(b'405')
                        respon = self.request.recv(1024)
                    elif file_size == recv_size:
                        self.request.sendall(b'203')
                        print('一致.')
                        return
                else:
                    recv_size = 0

                self.request.sendall(str(file_size).encode())
                resonse = self.request.recv(1024)
                with open(file_path, 'rb') as f:
                    f.seek(recv_size)
                    while True:
                        data = f.read(1024)
                        if not data: break
                        self.request.sendall(data)
        else:
            self.request.sendall(b'402')

    def recvfile(self, reciever, file):
        size = int(self.request.recv(1024).decode())
        sql = 'select home_path from userinfos where user = %s'
        params = [reciever]
        helper = MysqlHelper()
        resualt = helper.fetchone(sql, params)
        if resualt[0] is not None:
            path = resualt[0]+'\\'+file
       # file_size = os.path.getsize(path)
        recv_size = 0
        with open(path, 'wb') as f:
            while recv_size != size:
                data = self.request.recv(1024)
                recv_size += len(data)
                f.write(data)

    def getmail(self, user):
        sql = 'select email from userinfos where user = %s'
        params = [user]
        helper = MysqlHelper()
        result = helper.fetchone(sql,params)
        if result[0] is not None:
            email = result[0]
            return email

    @staticmethod
    def file_oper(file, mode, *args):
        if mode == 'w' or mode == 'wt':
            data = args[0]
            with open(file, mode) as f:
                f.write(data)
        elif mode == 'r' or mode == 'rb':
            with open(file, mode) as f:
                data = f.read()
                return data
