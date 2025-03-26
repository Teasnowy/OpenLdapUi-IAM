import sys
import requests
import json
import logging
from ruamel.yaml import YAML


# 这个类是用直接访问接口的形式访问nacos, 并没有用第三方的nacos库
class cnacos:

    def __init__(
        self, host='127.0.0.1', port=8848, path='/nacos', user='nacos', password='nacos', tenant=None,
        group='DEFAULT_GROUP', dataid=None, token=None
    ):
        self.token = None
        self.token_res = None
        # 这里必须要加http://, 不然报错No connection adapters were found
        self.url = 'http://{}:{}{}'.format(host, port, path)
        self.tenant = tenant
        self.group = group
        self.dataid = dataid
        self.user = user
        self.password = password
        self.auth()

    # 登录并鉴权
    def auth(self):
        url_auth = "{}/v1/auth/login".format(self.url)
        data_auth = {
            "username": self.user,
            "password": self.password
        }
        r = requests.post(url=url_auth, data=data_auth)
        self.token_res = r.json()
        if self.token_res.get('accessToken'):
            self.token = self.token_res['accessToken']
            logging.info("取到nacos的登录token: {}".format(self.token_res,))
        else:
            logging.error("获取到的nacos token为空: {}".format(self.token_res))
            raise ZeroDivisionError('登录nacos时遇到问题')
        return self.token

    def updateenv(self, tenant, group, dataid, token):
        # 如果为空, 代表用户没有传入这些参数, 那么就优先读取主类初始化时的参数值
        if not tenant:
            tenant = self.tenant
        if not group:
            group = self.group
        if not dataid:
            dataid = self.dataid
        # 如果外部传入了token, 那么就使用外部的
        if not token:
            token = self.token
        # 返回
        return tenant, group, dataid, token

    # 获取配置的函数
    def getconf(self, tenant=None, group=None, dataid=None, token=None, to_type=None):

        # 优先读取传给函数的, 但如果没有给函数穿参, 那么读取主类的
        tenant, group, dataid, token = self.updateenv(tenant, group, dataid, token)

        # 定义get的参数
        parm_get = {
            "accessToken": self.token,
            "tenant": tenant,
            "group": group,
            "dataId": dataid
        }

        # 拼接请求配置的url
        url_config_get = '{}/v1/cs/configs'.format(self.url)
        logging.info('尝试获取配置的url: {}, 参数: {}'.format(url_config_get, parm_get))
        r = requests.get(url=url_config_get, params=parm_get)
        if r.status_code == 200:
            if r.text:
                if to_type == "json":
                    # 解析返回的配置文件, 将yaml解析为json
                    yaml = YAML(typ='rt')
                    res = yaml.load(r.text)
                    return res
                else:
                    return r.text
            else:
                return r.text
        else:
            logging.error("获取配置时遇到问题, 状态码: {}, 返回: {}".format(r.status_code, r.text))
            raise ZeroDivisionError('获取nacos配置时遇到问题')

    # 更新配置的函数, nacos没有指定的dataid时自动新建
    def setconf(self, tenant=None, group=None, dataid=None, data=None, token=None):

        # 优先读取传给函数的, 但如果没有给函数穿参, 那么读取主类的
        tenant, group, dataid, token = self.updateenv(tenant, group, dataid, token)

        # 定义get的参数
        data_set = {
            "accessToken": self.token,
            "tenant": tenant,
            "group": group,
            "dataId": dataid,
            "content": data
        }

        # 拼接上传配置的url
        url_config_set = '{}/v1/cs/configs'.format(self.url)
        logging.info('尝试上传配置的url: {}, 参数: {}'.format(url_config_set, data_set))
        r = requests.post(url=url_config_set, data=data_set)
        if r.status_code == 200:
            return r.text
        else:
            logging.error("上传配置时遇到问题, 状态码: {}, 返回: {}".format(r.status_code, r.text))
            raise ZeroDivisionError('上传nacos配置时遇到问题')

    # 删除配置的函数
    def delconf(self, tenant=None, group=None, dataid=None, token=None):

        # 优先读取传给函数的, 但如果没有给函数穿参, 那么读取主类的
        tenant, group, dataid, token = self.updateenv(tenant, group, dataid, token)

        # 定义get的参数
        data_del = {
            "accessToken": self.token,
            "tenant": tenant,
            "group": group,
            "dataId": dataid,
        }

        # 拼接删除配置的url
        url_config_set = '{}/v1/cs/configs'.format(self.url)
        logging.info('尝试删除配置的url: {}, 参数: {}'.format(url_config_set, data_del))
        r = requests.delete(url=url_config_set, data=data_del)
        if r.status_code == 200:
            return r.text
        else:
            logging.error("删除配置时遇到问题, 状态码: {}, 返回: {}".format(r.status_code, r.text))
            raise ZeroDivisionError('删除nacos配置时遇到问题')
