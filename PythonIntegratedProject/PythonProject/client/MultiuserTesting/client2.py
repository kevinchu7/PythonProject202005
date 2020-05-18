# -*- coding: utf-8 -*-
# 客户端程序
import os, sys
import socket
import smtplib
from email.mime.text import MIMEText
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib

class MyClient:
    def __init__(self, ip_port):
        self.client = socket.socket()
        self.ip_port = ip_port

    def connect(self):
        self.client.connect(self.ip_port)

    def start(self):
        self.connect()
        while True:
            print('********welcome!********\n注册(register)\n登录(login)')
            auth_type = input('>>>').strip()
            if not auth_type: continue
            if auth_type == 'register':
                user = input('用户名:').strip()
                pwd = input('密码:').strip()
                email = input('邮箱：').strip()
                auth_info = '%s:%s:%s:%s' % (auth_type, user, pwd, email)
                self.client.sendall(auth_info.encode())
                status_code = self.client.recv(1024).decode()
                if status_code == '201':
                    print('\033[32;1m注册成功.\033[0m')
                elif status_code == '401':
                    print('\033[31;1m注册用户名已存在.\033[0m')
                else:
                    print('[%s]Error!' % status_code)
            elif auth_type == 'login':
                user = input('用户名:').strip()
                pwd = input('密码:').strip()
                auth_info = '%s:%s:%s' % (auth_type, user, pwd)
                self.client.sendall(auth_info.encode())
                status_code = self.client.recv(1024).decode()
                if status_code == '200':
                    print('\033[32;1m登录成功.\033[0m')
                    self.option()
                elif status_code == '400':
                    print('\033[31;1m用户名或密码错误.\033[0m')
                else:
                    print('[%s]Error!' % status_code)
            else:
                print('\033[31;1m输入错误，请重新输入.\033[0m')

    # 功能菜单
    def option(self):
        while True:

            opt = int(input('1.聊天 2.发送email 3.查收email 4.传文件 5.访问共享空间 6.访问个人空间\n请选择>>>'))
            if not opt: continue
            if opt == 1:
                self.client.sendall(b'1')
                self.chat()
            elif opt == 2:
                self.client.sendall(b'2')
                email = self.client.recv(1024).decode()
                self.sendemail(email)
            elif opt == 3:
                self.client.sendall(b'3')
                email = self.client.recv(1024).decode()
                self.recvemail(email)

            elif opt == 4:
                self.client.sendall(b'4')
                receiver = input('请输入接收方用户名>>>').strip()
                file = input('请输入要发送的文件名>>>').strip()
                self.client.send(receiver.encode())
                self.client.send(file.encode())
                self.sendfile(file)
            elif opt == 5:
                self.client.sendall(b'5')
                print('\033[32;1m您已经进入共享空间.\033[0m')
                self.interactive()
            elif opt == 6:
                self.client.sendall(b'6')
                self.interactive()
            else:
                print('\033[31;1m输入错误，请重新输入.\033[0m')

    def sendmsg(self):
        msg = input('请输入要发送的内容>>>').strip()
        self.client.sendall(msg.encode())
        print('\033[32;1m已发送.\033[0m')

    def recvmsg(self):
        msg = self.client.recv(1024).decode()
        print(msg)

    # 聊天
    def chat(self):
        op = int(input('1.发消息  2.看消息  请选择>>>'))
        if op == 1:
            self.client.send(b'0101')
            self.sendmsg()
        if op == 2:
            self.client.send(b'0202')
            self.recvmsg()

    # ftp
    def interactive(self):
        while True:
            command = input('请输入命令>>>').strip()
            if not command:
                continue
            command_str = command.split()[0]
            if hasattr(self, command_str):
                func = getattr(self, command_str)
                func(command)

    def dir(self, command):
        self.__universal_method_data(command)

    def pwd(self, command):
        self.__universal_method_data(command)

    def mkdir(self, command):
        self.__universal_method_none(command)

    def cd(self, command):
        self.__universal_method_none(command)

    def __universal_method_none(self, command):
        self.client.sendall(command.encode())
        status_code = self.client.recv(1024).decode()
        if status_code == '202':
            self.client.sendall(b'000')
        else:
            print('[%s]Error!' % status_code)

    def __universal_method_data(self, command):
        self.client.sendall(command.encode())
        status_code = self.client.recv(1024).decode()
        if status_code == '202':
            self.client.sendall(b'000')
            result = self.client.recv(4096)
            print(result.decode('gbk'))
        else:
            print('[%s]Error!' % status_code)

    def put(self, command):
        if len(command.split()) > 1:
            filename = command.split()[1]
            if os.path.isfile(filename):
                self.client.sendall(command.encode())
                file_size = os.path.getsize(filename)
                response = self.client.recv(1024)
                self.client.sendall(str(file_size).encode())
                status_code = self.client.recv(1024).decode()
                if status_code == '202':
                    with open(filename, 'rb') as f:
                        while True:
                            data = f.read(1024)
                            send_size = f.tell()
                            if not data: break
                            self.client.sendall(data)
                            self.__progress(send_size, file_size, '上传中')
                else:
                    print('\033[31;1m[%s]空间不足.\033[0m' % status_code)

            else:
                print('\033[31;1m[%s]文件不存在.\033[0m' % filename)

        else:
            print('\033[31;1m命令格式错误.\033[0m')

    # 进度条
    def __progress(self, trans_size, file_size, mode):
        bar_length = 100
        percent = float(trans_size) / float(file_size)
        hashes = '=' * int(percent * bar_length)
        spaces = ' ' * int(bar_length - len(hashes))
        sys.stdout.write('\r%s %.2fM/%.2fM %d%% [%s]'
                         % (mode, trans_size / 1048576, file_size / 1048576, percent * 100, hashes + spaces))

    def get(self, command):
        self.client.sendall(command.encode())
        status_code = self.client.recv(1024).decode()
        if status_code == '202':
            filename = command.split()[1]
            if os.path.isfile(filename):
                self.client.sendall(b'406')
                response = self.client.recv(1024)
                has_send_data = os.path.getsize(filename)
                self.client.sendall(str(has_send_data).encode())
                status_code = self.client.recv(1024).decode()
                if status_code == '405':
                    print('续传.')
                    response = self.client.sendall(b'000')
                elif status_code == '203':
                    print('文件一致.')
                    return
            else:
                self.client.sendall(b'202')
                has_send_data = 0

            file_size = int(self.client.recv(1024).decode())
            self.client.sendall(b'000')
            with open(filename, 'ab') as f:
                while has_send_data != file_size:
                    data = self.client.recv(1024)
                    has_send_data += len(data)
                    f.write(data)
                    self.__progress(has_send_data, file_size, '下载中')

        else:
            print('[%s]Error!' % status_code)

    # 传文件
    def sendfile(self, filename):
        file_size = os.path.getsize(filename)
        self.client.sendall(str(file_size).encode())
        with open(filename, 'rb') as f:
            while True:
                data = f.read(1024)
                send_size = f.tell()
                if not data: break
                self.client.sendall(data)
                self.__progress(send_size, file_size, '上传中')
        print('成功！')

    # 发邮件
    def sendemail(self,msg_from):
        password = input('请输入您的邮箱授权码:')
        msg_to = input('请输入收件人邮箱：')
        subject = input('请输入邮件主题：')
        content = input('请输入正文内容：')
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = msg_from
        msg['To'] = msg_to
        print(msg_from)
        try:
            client = smtplib.SMTP_SSL('smtp.163.com', smtplib.SMTP_SSL_PORT)
            # print("连接到邮件服务器成功")
            client.login(msg_from, password)
            # print("登录成功")
            client.sendmail(msg_from, msg_to, msg.as_string())
            print('\033[32;1m邮件发送成功！\033[0m')
        except smtplib.SMTPException as e:
            print('\033[31;1邮件发送失败！\033[0m')

    # 收邮件
    def recvemail(self, email):
        password = input('请输入您的邮箱授权码:')
        pop3_server = 'pop3.163.com'
        # 连接到POP3服务器:
        server = poplib.POP3_SSL(pop3_server, port=995)
        # 可以打开或关闭调试信息:
        server.set_debuglevel(1)
        # 可选:打印POP3服务器的欢迎文字:
        print(server.getwelcome().decode('utf-8'))
        # 身份认证:
        server.user(email)
        server.pass_(password)
        # stat()返回邮件数量和占用空间:
        print('Messages: %s. Size: %s' % server.stat())
        # list()返回所有邮件的编号:
        resp, mails, octets = server.list()
        # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
        print(mails)
        # 获取最新一封邮件, 注意索引号从1开始:
        index = len(mails)
        resp, lines, octets = server.retr(index)
        # lines存储了邮件的原始文本的每一行,
        # 可以获得整个邮件的原始文本:
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        # 稍后解析出邮件:
        msg = Parser().parsestr(msg_content)
        # 获取编码类型
        def guess_charset(msg):
            charset = msg.get_charset()
            if charset is None:
                content_type = msg.get('Content-Type', '').lower()
                pos = content_type.find('charset=')
                if pos >= 0:
                    charset = content_type[pos + 8:].strip()
            return charset

        # 解码
        def decode_str(s):
            value, charset = decode_header(s)[0]
            if charset:
                value = value.decode(charset)
            return value

        # 信息处理
        def print_info(msg, indent=0):
            if indent == 0:
                for header in ['From', 'To', 'Subject']:
                    value = msg.get(header, '')
                    if value:
                        if header == 'Subject':
                            value = decode_str(value)
                        else:
                            hdr, addr = parseaddr(value)
                            name = decode_str(hdr)
                            value = u'%s <%s>' % (name, addr)
                    print('%s%s: %s' % ('  ' * indent, header, value))
            if (msg.is_multipart()):
                parts = msg.get_payload()
                for n, part in enumerate(parts):
                    print('%spart %s' % ('  ' * indent, n))
                    print('%s--------------------' % ('  ' * indent))
                    print_info(part, indent + 1)
            else:
                content_type = msg.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    content = msg.get_payload(decode=True)
                    charset = guess_charset(msg)
                    if charset:
                        content = content.decode(charset)
                    print('%sText: %s' % ('  ' * indent, content + '...'))
                else:
                    print('%sAttachment: %s' % ('  ' * indent, content_type))
        print_info(msg)

if __name__ == '__main__':
    ftp_client = MyClient(('localhost', 8080))
    ftp_client.start()

ftp_client.py
