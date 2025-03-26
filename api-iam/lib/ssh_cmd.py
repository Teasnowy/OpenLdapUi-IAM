import time
import paramiko
import logging
import datetime
import json
# from .lite3 import *


# 执行ssh远程命令的函数
def ssh_shell(config_cmd):

    host = config_cmd['host']
    port = config_cmd['port']
    user = config_cmd['user']
    passwd = config_cmd['passwd']
    cmd = config_cmd['cmd']
    # 实例化ssh客户端
    ssh = paramiko.SSHClient()
    # 创建默认的白名单
    policy = paramiko.AutoAddPolicy()
    # 设置白名单, 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(policy)
    logging.info("发起对{}的ssh连接".format(host))
    # 链接服务器
    ssh.connect(
        hostname=host,
        port=port,
        username=user,
        password=passwd
    )
    # 远程执行命令
    logging.info("在主机{}执行命令:'{}'".format(host, cmd))
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    # exec_command 返回的对象都是类文件对象
    # stdin 标准输入 用于向远程服务器提交参数，通常用write方法提交
    # stdout 标准输出 服务器执行命令成功，返回的结果  通常用read方法查看
    # stderr 标准错误 服务器执行命令错误返回的错误值  通常也用read方法
    # 查看结果，注意在Python3 字符串分为了：字符串和字节两种格式，文件返回的是字节

    # 按字节返回结果
    res_acc = stdout.read().decode()
    res_err = stderr.read().decode()
    res_status = stdout.channel.recv_exit_status()
    ssh.close()
    return res_acc, res_err, res_status


def ssh_scp(config_cmd):
    """
    实现linux的scp命令
    """

    host = config_cmd['host']
    port = config_cmd['port']
    user = config_cmd['user']
    passwd = config_cmd['passwd']
    local_file_path = config_cmd['local_file_path']
    remote_file_path = config_cmd['remote_file_path']

    # 创建一个 SSH 传输对象
    transport = paramiko.Transport((host, port))
    # 连接到远程主机
    transport.connect(username=user, password=passwd)

    # 使用 SFTP 协议创建一个 SFTP 客户端对象
    sftp = paramiko.SFTPClient.from_transport(transport)
    # 从本地上传文件到远程服务器
    sftp.put(local_file_path, remote_file_path)

    # 关闭 SFTP 客户端连接
    sftp.close()
    # 关闭 SSH 传输连接
    transport.close()


# 查找日志文件的函数
def log_find(file_name, config_host):
    cmd_isfile = '[[ -f "{}" ]] && echo acc || echo err'.format(file_name)
    config_host['cmd'] = cmd_isfile
    cmd_isfile_acc, cmd_isfile_err, res_status = ssh_shell(config_host)
    if not cmd_isfile_err and cmd_isfile_acc == 'acc':
        logging.info('文件"{}"存在'.format(file_name))
        state_mountdir_find = 0
    else:
        logging.info('文件"{}"不在主机"{}"上'.format(file_name, config_host['host']))
        state_mountdir_find = 1
    return state_mountdir_find


def data_init(data=None, ok=None, err=None):

    if err and not ok:
        # 如果有异常信息且没定义状态, 则赋值no
        ok = 'no'
    elif not ok:
        # 如果仅没定义状态, 则赋值ok
        ok = 'ok'

    data_return = {
        "ok": ok,
        "message_err": err,
        "data": data,
        "time": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    }

    return json.dumps(data_return, default=str)


def test_sleep(n):
    logging.info("开始睡眠")
    time.sleep(n)
    logging.info("结束睡眠")
