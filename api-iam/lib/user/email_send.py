import logging
from lib.db.db_select import kvdb
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import os


# text 邮件内容
# un 目标邮箱地址
# to_addr 目标邮箱地址
# fns 附件文件名列表
def send_email(to_addr, title, text, fns: list = None):
    """
    发送邮件
    :param to_addr: 对方邮箱地址
    :param title: 邮件标题
    :param text: 正文文本
    :param fns: 列表, 里面是文件路径, 用来发送附件
    :return:
    """

    # 提取配置中的邮件服务器
    kv = kvdb()
    cf_mail = kv.read()["email"]

    # 是否启用ssl
    use_ssl = cf_mail["use_ssl"]

    # 发信方的信息：发信邮箱，QQ 邮箱授权码
    from_addr = cf_mail["from_addr"]
    password = cf_mail["from_passwd"]
    # 收信方邮箱
    to_addr = to_addr
    # 发信服务器,阿里企业邮箱：smtp.mxhichina.com，QQ：smtp.qq.com
    smtp_server = cf_mail["smtp_server"]
    smtp_port = cf_mail["smtp_port"]

    # 构建可以发送附件的对象
    msg = MIMEMultipart()
    # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码，正文支持html格式
    body = text
    # 这里添加的是普通文本格式
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 邮件头信息
    # 这里最好填写发信人邮箱, 不然可能被退回
    msg['From'] = Header(from_addr)  # 发送者
    # 这里最好填写收信人邮箱, 不然可能被退回
    msg['To'] = Header(to_addr)  # 接收者
    subject = title
    msg['Subject'] = Header(subject, 'utf-8')  # 邮件主题

    # 添加附件，这里是用循环添加多个附件,如果是图片，要用MIMEImage
    if fns:
        for fn in fns:
            att_tmp = MIMEApplication(open(fn, 'rb').read())
            att_tmp.add_header('Content-Disposition', 'attachment', filename=fn)
            msg.attach(att_tmp)

    if use_ssl == 'yes':
        smtpobj = smtplib.SMTP_SSL(smtp_server)
    else:
        smtpobj = smtplib.SMTP(smtp_server)
    try:
        # smtpobj = smtplib.SMTP_SSL(smtp_server)
        # 建立连接--qq邮箱服务和端口号（可百度查询）
        smtpobj.connect(smtp_server, smtp_port)
        # 登录--发送者账号和口令
        smtpobj.login(from_addr, password)
        # 发送邮件
        smtpobj.sendmail(from_addr, to_addr, msg.as_string())
        logging.info("邮箱{}邮件发送成功".format(to_addr))
    except smtplib.SMTPException as el:
        logging.error("邮箱{}无法发送邮件".format(to_addr))
        # webh_dd(to_addr)
        logging.exception(el)
    finally:
        # 关闭服务器
        smtpobj.quit()
