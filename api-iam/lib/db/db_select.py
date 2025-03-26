import logging
import os
import sys
from .db_redis import kvdb_redis
from .db_diskcache import kvdb_diskcache
from ..singleton import singleton


@singleton
class kvdb:
    def __init__(self, db_type=None, conf=None, default_config_name="config_global", is_init: bool = True,
            default_config_filepath=os.path.abspath(os.path.dirname(sys.argv[0])) + "/db"):
        """

        :param db_type: 选择的数据库类型, 目前支持"redis"|"diskcache"
        :param conf: redis的配置
        :param default_config_name: 默认的主key, 存储主配置文件
        :param is_init: 是否初始化diskcache的目录(删除旧数据)
        :param default_config_filepath: diskcache的数据存储目录
        """

        self.default_config_name = default_config_name

        if db_type == "redis":
            self.db = kvdb_redis(conf=conf, default_config_name=default_config_name)
        elif db_type == "diskcache":
            self.db = kvdb_diskcache(
                default_config_name=default_config_name, is_init=is_init,
                default_config_filepath=default_config_filepath
            )
        else:
            raise ZeroDivisionError(f"不支持的键值数据库类型: {db_type}")

        logging.info(f"已指定键值数据库为{db_type}")

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)

        return cls._instance

    def check(self, k=None) -> bool:
        """
        判断k是否存在
        :param k: key名字
        :return:
        """

        return self.db.check(k=k)

    def read(self, k=None, default=None, expire_time: bool = False, tag: bool = False, retry: bool = False,
             read: bool = False, ):
        """
        获取数据
        :param k: key的名字, 不填默认为self.default_config_name定义的值
        :param default: 如果对应的键值没有，则返回这个default设置的默认值
        :param expire_time: 同时返回缓存的过期时间(linux秒数), 这样会使结果变为元组, 默认为False
        :param tag: 同时返回注释, 这样会使结果变为元组, 默认为False
        :param retry: 失败是否重试, 默认为False
        :param read: 返回二进制数据, 默认为False
        :return:
        """
        return self.db.read(k=k, default=default, expire_time=expire_time, tag=tag, retry=retry, read=read,)

    def get(self, k=None, default=None, expire_time: bool = False, tag: bool = False, retry: bool = False,
             read: bool = False, ):
        """
        获取数据, 用于兼容redis里的自定义类返回非序列化的数据
        :param k: key的名字, 不填默认为self.default_config_name定义的值
        :param default: 如果对应的键值没有，则返回这个default设置的默认值
        :param expire_time: 同时返回缓存的过期时间(linux秒数), 这样会使结果变为元组, 默认为False
        :param tag: 同时返回注释, 这样会使结果变为元组, 默认为False
        :param retry: 失败是否重试, 默认为False
        :param read: 返回二进制数据, 默认为False
        :return:
        """
        return self.db.get(k=k, default=default, expire_time=expire_time, tag=tag, retry=retry, read=read,)

    def set(self, v, k=None, expire=None, read=False, tag=None, retry: bool = True):
        """
        创建一条数据, 如果key已存在, 则更新值
        :param v: 数据
        :param k: key名字, 默认为self.default_config_name定义的值
        :param expire: 过期时间，指定该缓存条目的有效期, 可以是秒数或一个 timedelta 对象, 如果 expire 被设置为 None,则永远有效
        :param bool read: 布尔值, 以二进制模式读取内容, 默认为False
        :param str tag: 注释
        :param bool retry: 布尔值, 表示连接超时是否重试, 默认为True
        :return:
        """

        return self.db.set(v=v, k=k, expire=expire, tag=tag, retry=retry, read=read,)

    def touch(self, k=None, expire=None, retry=False):
        """
        延长key的过期时间
        :param k: key名字
        :param expire: 过期时间，指定该缓存条目的有效期, 可以是秒数或一个 timedelta 对象, 如果 expire 被设置为 None,则永远有效
        :param bool retry: 布尔值, 表示连接超时是否重试, 默认为False
        :return:
        """

        return self.db.touch(k=k, expire=expire, retry=retry)

    def incr(self, delta: int, k=None, expire=None, touch: bool = True):
        """
        当key的值为纯数字时, 加上传入的数值, 如果当前没有这个key, 自动从0开始算
        :param delta: 加的数字
        :param k: key的名字, 默认为self.default_config_name定义的值
        :param expire: 过期时间, 只有key不存在时生效, 除非touch为True
        :param touch: 是否刷新过期时间, 如果为True, 则key已存在时刷新过期时长为expire
        :return:
        """

        return self.db.incr(delta=delta, k=k, expire=expire, touch=touch)

    def decr(self, delta: int, k=None, expire=None, touch: bool = True):
        """
        当key的值为纯数字时, 减掉传入的数值, 如果当前没有这个key, 自动从0开始算, 可以为负数
        :param delta: 加的数字
        :param k: key的名字, 默认为self.default_config_name定义的值
        :param expire: 过期时间, 只有key不存在时生效, 除非touch为True
        :param touch: 是否刷新过期时间, 如果为True, 则key已存在时刷新过期时长为expire
        :return:
        """

        return self.db.decr(delta=delta, k=k, expire=expire, touch=touch)

    def delete(self, k=None, retry: bool = False):
        """
        删除值
        :param k: key名
        :param retry: 是否重试, 默认为否
        :return:
        """

        return self.db.delete(k=k, retry=retry)

    def getall_key(self):
        """
        获取所有键
        """

        return self.db.getall_key()

    def getall_item(self, *args):
        """
        获取所有键值
        :param args:
        :return:
        """

        return self.db.getall_item()