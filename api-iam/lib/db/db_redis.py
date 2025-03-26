from ..singleton import singleton
import json
import sys
import redis
import logging
from rediscluster import RedisCluster

@singleton
class kvdb_redis:
    def __init__(self, conf=None, default_config_name="config_global"):
        """
        redis的连接
        :param default_config_name: 默认的主key名字
        :param conf: redis连接信息
        """
        self.timeout = conf["timeout"]
        self.default_config_name = default_config_name
        # 根据配置实例化redis
        if conf:
            if conf["select"] == "src":
                src = conf["src"]
                self.c = redis.StrictRedis(
                    host=src["host"],
                    port=src["port"], db=src["db"],
                    password=src["passwd"],
                    socket_connect_timeout=self.timeout,
                    decode_responses=True
                )
                logging.info(f'启用了redis的单实例模式: host: {src["host"]}, port: {src["port"]}, db: {src["db"]}')
            elif conf["select"] == "cluster":
                cluster = conf["cluster"]
                self.c = RedisCluster(
                    startup_nodes=cluster['startup_nodes'],
                    password=cluster['passwd'],
                    socket_connect_timeout=self.timeout,
                    decode_responses=True
                )
                logging.info(f'启用了redis的集群模式: startup_nodes: {cluster["startup_nodes"]}')
            else:
                raise ZeroDivisionError("不支持的redis模式")
        else:
            raise ZeroDivisionError("传入的redis信息解析失败")

        logging.info("已初始化redis键值数据库")

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

        res = self.c.scan_iter(k)
        key_list = []
        for i in res:
            key_list.append(i)

        # logging.info(f"{k}测试为: {key_list}")
        if key_list:
            return True
        else:
            return False

    def read(self, k=None, default=None, expire_time: bool = False, tag: bool = False, retry: bool = False,
             read: bool = False, ):
        """
        获取数据, 获取被本类序列化过的key
        :param k: key的名字, 不填默认为self.default_config_name定义的值
        :param default: 如果对应的键值没有，则返回这个default设置的默认值
        :param expire_time: 同时返回缓存的过期时间(linux秒数), 这样会使结果变为元组, 默认为False
        :param tag: 同时返回注释, 这样会使结果变为元组, 默认为False
        :param retry: 失败是否重试, 默认为False
        :param read: 返回二进制数据, 默认为False
        :return:
        """
        if not k:
            k = self.default_config_name

        # flag是读取模式, r表示只读
        # logging.info(f"读取{self.config_filepath}数据: {k}")
        data_result = self.c.get(k)
        if not data_result:
            data_result = default
        else:
            # 反序列化
            data_result = self.value_get(data_result)

        return data_result


    def get(self, k=None, default=None, expire_time: bool = False, tag: bool = False, retry: bool = False,
             read: bool = False, ):
        """
        获取数据, 是redis的原生get
        :param k: key的名字, 不填默认为self.default_config_name定义的值
        :param default: 如果对应的键值没有，则返回这个default设置的默认值
        :return:
        """
        if not k:
            k = self.default_config_name

        # flag是读取模式, r表示只读
        # logging.info(f"读取{self.config_filepath}数据: {k}")
        data_result = self.c.get(k)
        if not data_result:
            data_result = default

        return data_result

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
        # logging.info(f"向redis写入数据: {k}: {v}")
        try:
            if not k:
                k = self.default_config_name

            # 由于redis的普通键不能存储字典, 所以依据类型序列化后存储
            v = self.value_store(v)

            res = self.c.set(k, v, ex=expire)

            logging.info(f"向redis写入数据: {k}")
            if not res:
                raise ZeroDivisionError(f"向redis中set数据失败, key: {k}, value: {v}")
        except Exception as el:
            logging.error("向redis中更新数据时遇到了问题")
            logging.exception(el)
            raise ZeroDivisionError(f"向redis中set数据失败, key: {k}, value: {v}")

    def touch(self, k=None, expire=None, retry=False):
        """
        延长key的过期时间 (需要redis版本不低于 6.2.0, 如低于可考虑先persist再expire)
        :param k: key名字
        :param expire: 过期时间，指定该缓存条目的有效期, 可以是秒数或一个 timedelta 对象, 如果 expire 被设置为 None,则永远有效
        :param bool retry: 布尔值, 表示连接超时是否重试, 默认为False
        :return:
        """
        if not k:
            k = self.default_config_name
        # 需要redis版本不低于 6.2.0, 如低于可考虑先persist再expire
        res = self.c.touch(k)
        # logging.info(f"已续期: {k}, 剩余{self.c.ttl(k)}")

        if not res:
            raise ZeroDivisionError(f"向redis中touch数据失败, key: {k}")

    def incr(self, delta: int, k=None, expire=None, touch: bool = True):
        """
        当key的值为纯数字时, 加上传入的数值, 如果当前没有这个key, 自动从0开始算
        :param delta: 加的数字
        :param k: key的名字, 默认为self.default_config_name定义的值
        :param expire: 过期时间, 只有key不存在时生效, 除非touch为True
        :param touch: 是否刷新过期时间, 如果为True, 则key已存在时刷新过期时长为expire
        :return:
        """

        if not k:
            k = self.default_config_name

        # 测试k是否存在, 不存在则新建为0, 这里不能用本类的set, 应该用原生的, 不然无法自动+1
        # res = self.check(k)
        # logging.info(f"{k}测试为: {res}")
        if not self.check(k):
            # logging.info(f"触发了incr的新增: {k}, 过期设定为: {expire}秒")
            self.c.set(k, 0, ex=expire)
        # 如果需要刷新已存在key的持续时长, 默认为是, 因为redis的计算函数默认不会续期key
        if touch:
            self.touch(k)

        res = self.c.incr(k, amount=delta,)

        if not res:
            raise ZeroDivisionError(f"向redis中incr数据失败, key: {k}, delta: {delta}")

    def decr(self, delta: int, k=None, expire=None, touch: bool = True):
        """
        当key的值为纯数字时, 减掉传入的数值, 如果当前没有这个key, 自动从0开始算, 可以为负数
        :param delta: 加的数字
        :param k: key的名字, 默认为self.default_config_name定义的值
        :param expire: 过期时间, 只有key不存在时生效, 除非touch为True
        :param touch: 是否刷新过期时间, 如果为True, 则key已存在时刷新过期时长为expire
        :return:
        """
        if not k:
            k = self.default_config_name

        # 测试k是否存在, 不存在则新建为0
        if not self.check(k):
            self.c.set(k, 0, ex=expire)
        # 如果需要刷新已存在key的持续时长, 默认为是, 因为redis的计算函数默认不会续期key
        if touch:
            self.touch(k, expire)

        res = self.c.decr(k, amount=delta)

        if not res:
            raise ZeroDivisionError(f"向redis中decr数据失败, key: {k}, delta: {delta}")

    def delete(self, k=None, retry: bool = False):
        """
        删除值
        :param k: key名
        :param retry: 是否重试, 默认为否
        :return:
        """
        if not k:
            k = self.default_config_name
        res = self.c.delete(k)
        if not res:
            raise ZeroDivisionError(f"向redis中delete数据失败, key: {k}")

    def value_store(self, data):
        """
        # 由于redis的普通键不能存储字典, 所以依据类型序列化后存储
        :param data:
        :return:
        """

        # 序列化存储前，检查数据类型
        if isinstance(data, (str, int, float, bool)):
            # 直接存储基本类型（字符串、数字、布尔值）
            return json.dumps({'type': 'basic', 'value': data})
        elif isinstance(data, list):
            # 存储列表
            return json.dumps({'type': 'list', 'value': data})
        elif isinstance(data, dict):
            # 存储字典
            return json.dumps({'type': 'dict', 'value': data})
        else:
            # 其他类型，转为字符串
            return json.dumps({'type': 'unknown', 'value': str(data)})

    def value_get(self, data_redis):
        """
        将redis中的数据转化为代码能读懂的数据
        :param data_redis: redis中被本类序列化过的数据, 如: {'type': 'dict', 'value': data}
        :return:
        """
        stored_data = json.loads(data_redis)
        data_type = stored_data['type']
        value = stored_data['value']
        if data_type == 'basic':
            # 基本类型，直接返回值
            if isinstance(value, str):
                try:
                    return json.loads(value)  # 尝试将字符串转回原始类型
                except ValueError:
                    return value  # 如果不能转换，就返回原始字符串
            return value
        elif data_type == 'list':
            # 列表类型，返回列表
            return value
        elif data_type == 'dict':
            # 字典类型，返回字典
            return value
        else:
            # 其他类型，返回字符串
            return str(value)

    def getall_key(self):
        """
        获取所有键
        """
        res = []
        res_iter = self.c.scan_iter()
        for i in res_iter:
            res.append(i)
        return res

    def getall_item(self, *args):
        """
        获取所有键值
        :param args:
        :return:
        """

        list_k = self.getall_key()
        dict_res = {}
        for k in list_k:
            dict_res[k] = self.read(k)

        return dict_res