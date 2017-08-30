# -*- coding: utf-8 -*-
import paramiko
# --------------------------------------命令行使用-------------------------------------------------------------
print("\033[32;1m****开始配置目标机器信息*****\033[0m")
#ips = input("主机IP:")
#user = input("主机账号:")
#password = getpass.getpass("主机密码:")
#port = 22
user = "root"
ips = "10.10.10.10"
password = ""
port = 22

class Tools(object):
    def __init__(self, user, password, port, ips):
        self.user = user
        self.password = password
        self.port = port
        self.ip = ips
    def connect(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ip, self.port, self.user, self.password)
            print("连接已建立")
        except Exception as e:
            print("未能连接到主机")
    def cmd(self):
        cmd = input("请输入要执行的命令:>>")
        stdout, stdin, stderr = self.ssh.exec_command(cmd)
        #print(sys.stdout.read())
    def input(self):
        self.local_file_abs = input("本地文件的绝对路径:>>")
        self.remote_file_abs = input("远程文件的绝对路径:>>")
    def put(self):
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        sftp = self.ssh.open_sftp()
        self.input()
        sftp.put(self.local_file_abs,self.remote_file_abs)
    def get(self):
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        sftp = self.ssh.open_sftp()
        self.input()
        sftp.get(self.remote_file_abs,self.local_file_abs)
    def close(self):
        self.ssh.close()
        print("连接关闭")
obj = Tools(user, password, port, ips)
if __name__ == "__main__":
    msg = '''\033[32;1m
    执行命令 >>输入cmd
    上传文件 >>输入put
    下载文件 >>输入get
    退出     >>输入q\033[0m
    '''
    getattr(obj, "connect")()
    while True:
        print(msg)
        inp = input("action:>>")
        if hasattr(obj,inp):
            getattr(obj,inp)()
        if inp == "q":
            getattr(obj,"close")()
            exit()
        else:print("没有该选项，请重新输入:>>")

# --------------------------------------当方法使用-------------------------------------------------------------

class Tools(object):
    def __init__(self, user, password, port, ips):
        self.user = user
        self.password = password
        self.port = port
        self.ip = ips
    def connect(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ip, self.port, self.user, self.password)
            print "remote server connect success"
        except Exception as e:
            print "can not remote connect: {e}".format(e)
    def put(self, local_file_abs, remote_file_abs):
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        sftp = self.ssh.open_sftp()
        sftp.put(local_file_abs,remote_file_abs)
        print "put {file} to remote success".format(file=local_file_abs)
    def get(self, local_file_abs, remote_file_abs):
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        sftp = self.ssh.open_sftp()
        sftp.get(remote_file_abs,local_file_abs)
        print "get {file} to remote success".format(file=local_file_abs)
    def close(self):
        self.ssh.close()
        print("remote connect close")

if __name__ == '__main__':
    tbls = ['crm_sysales_citypost_v']
    obj = Tools(user, password, port, ips)
    obj.connect()
    for tbl in tbls:
        filename = tbl + '.txt'
        obj.put(filename, '/home/xinpengdev/{filename}'.format(filename=filename))
    obj.close()