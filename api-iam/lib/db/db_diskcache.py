import functools
import shutil
import diskcache
import os
import sys
import logging
import threading


def singleton(cls_tmp):
    """
    同步锁, 接受一个类作为参数, 确保多线程环境下的类的单实例模式
    """
    # 保存原始 __new__ 和 __init__
    cls_tmp.__new_original__ = cls_tmp.__new__

    # 这里定义的singleton_new稍后会取代原__new__
    # 这里使用了 functools.wraps，使得装饰后的函数保留原始函数的签名和元数据
    @functools.wraps(cls_tmp.__new__)
    def singleton_new(cls, *args, **kwargs):
        # RLock() 是一种递归锁，与普通锁不同，递归锁允许同一个线程多次获得锁而不会导致死锁。这一步的目的是防止多个线程同时创建类实例, 防止小概率事件
        # 当一个线程获取锁时，其他线程会被阻塞，直到该线程释放锁，从而确保线程安全, 这里仅仅是定义锁, 并没有触发
        with threading.RLock():
            # 检查是否已有实例
            # 从类的 __dict__ 中检查是否已经存在实例 __it__。如果已经存在一个实例，直接返回该实例，避免再次创建，从而确保单例模式的效果
            it = cls.__dict__.get('__it__')
            if it is not None:
                return it

            # 如果类实例尚不存在，则调用原始的 __new__ 方法创建新实例，并将其存储在类属性 __it__ 中
            # 这样一来，后续的线程如果尝试创建该类的实例，会直接返回这个已经创建好的实例。
            cls.__it__ = it = cls.__new_original__(cls, *args, **kwargs)
            # 调用保存的原始 __init__ 方法 it.__init_original__(*args, **kwargs)，初始化实例
            it.__init_original__(*args, **kwargs)
            return it

    # 将类的 __new__ 方法替换为自定义的 singleton_new 方法，这样每次创建新实例时都会经过同步锁的检查，确保单例
    cls_tmp.__new__ = singleton_new
    # 将类的原始 __init__ 保存为 __init_original__，供新创建实例时使用
    cls_tmp.__init_original__ = cls_tmp.__init__
    # 将类的 __init__ 方法替换为 object.__init__。
    # 之所以这样做，是为了防止多次调用 __init__。在 Python 中，每次调用 __new__ 后，__init__ 都会执行。
    # 而在单例模式下，实例只需要初始化一次，所以替换为 object.__init__，使得后续的 __init__ 调用变成空操作
    cls_tmp.__init__ = object.__init__

    # 返回修改后的类
    return cls_tmp


@singleton
class kvdb_diskcache:

    def __init__(
            self, default_config_name="config_global", is_init: bool = True,
            default_config_filepath=os.path.abspath(os.path.dirname(sys.argv[0])) + "/db"
            ):
        """

        :param default_config_name: 默认的主key名字
        :param is_init: 启动时是否删除旧数据, 默认为是
        :param default_config_filepath: 缓存数据存放的目录, 默认为当前脚本所在目录下的db
        """
        self.config_filepath = default_config_filepath
        self.path_db = os.path.dirname(self.config_filepath)
        # 是否先删除旧数据
        if is_init:
            if os.path.exists(self.config_filepath):
                shutil.rmtree(self.config_filepath)
        self.default_config_name = default_config_name
        # 实例化diskcache, diskcache会自己创建目录
        self.c = diskcache.Cache(self.config_filepath)
        logging.info("已初始化diskcache键值数据库")

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
        if not k:
            k = self.default_config_name

        if k in self.c:
            return True
        else:
            return False

    def read(self, k=None, default=None, expire_time: bool = False, tag: bool = False, retry: bool = False, read: bool = False,):
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
        if not k:
            k = self.default_config_name
        # flag是读取模式, r表示只读
        # logging.info(f"读取{self.config_filepath}数据: {k}")
        data_result = self.c.get(k, default=default, expire_time=expire_time, tag=tag, retry=retry, read=read)

        self.expire()
        return data_result


    def get(self, k=None, default=None, expire_time: bool = False, tag: bool = False, retry: bool = False, read: bool = False,):
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
        if not k:
            k = self.default_config_name
        # flag是读取模式, r表示只读
        # logging.info(f"读取{self.config_filepath}数据: {k}")
        data_result = self.c.get(k, default=default, expire_time=expire_time, tag=tag, retry=retry, read=read)

        self.expire()
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
        self.expire()
        try:
            if not k:
                k = self.default_config_name
            res = self.c.set(k, v, expire=expire, read=read, tag=tag, retry=retry)
            logging.info(f"向{self.config_filepath}写入数据: {k}")
            if not res:
                raise ZeroDivisionError(f"向diskcache中set数据失败, key: {k}, value: {v}")
        except Exception as el:
            logging.error("向临时键值数据库中更新数据时遇到了问题")
            logging.exception(el)
            raise ZeroDivisionError(f"向diskcache中set数据失败, key: {k}, value: {v}")

    def touch(self, k=None, expire=None, retry=False):
        """
        延长key的过期时间
        :param k: key名字
        :param expire: 过期时间，指定该缓存条目的有效期, 可以是秒数或一个 timedelta 对象, 如果 expire 被设置为 None,则永远有效
        :param bool retry: 布尔值, 表示连接超时是否重试, 默认为False
        :return:
        """
        if not k:
            k = self.default_config_name

        res = self.c.touch(k, expire=expire, retry=retry)
        self.expire()
        if not res:
            raise ZeroDivisionError(f"向diskcache中touch数据失败, key: {k}")

    def add(self, v, k=None, expire=None, read=True, tag="data", retry: bool = True):
        """
        创建一条数据, 如果key已存在, 则失败
        :param v: 数据
        :param k: key名字, 默认为self.default_config_name定义的值
        :param expire: 过期时间，指定该缓存条目的有效期, 可以是秒数或一个 timedelta 对象, 如果 expire 被设置为 None,则永远有效
        :param bool read: 布尔值, 以二进制模式读取内容, 默认为False
        :param str tag: 注释
        :param bool retry: 布尔值, 表示连接超时是否重试, 默认为True
        :return:
        """
        if not k:
            k = self.default_config_name
        res = self.c.add(k, v, expire=expire, read=read, tag=tag, retry=retry)
        self.expire()
        if not res:
            raise ZeroDivisionError(f"向diskcache中add数据失败, key: {k}, value: {v}")

    def incr(self, delta: int, k=None, expire=None, touch: bool=True):
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

        # 测试k是否存在, 不存在则新建为0
        if not self.check(k):
            self.set(0, k, expire=expire)
        # 如果需要刷新已存在key的持续时长
        if touch:
            self.touch(k, expire)

        res = self.c.incr(k, delta=delta)
        self.expire()
        if not res:
            raise ZeroDivisionError(f"向diskcache中incr数据失败, key: {k}, delta: {delta}")

    def decr(self, delta: int, k=None, expire=None, touch: bool=True):
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
            self.set(0, k, expire=expire)
        # 如果需要刷新已存在key的持续时长
        if touch:
            self.touch(k, expire)

        res = self.c.decr(k, delta=delta)
        self.expire()
        if not res:
            raise ZeroDivisionError(f"向diskcache中decr数据失败, key: {k}, delta: {delta}")

    def delete(self, k=None, retry: bool = False):
        """
        删除值
        :param k: key名
        :param retry: 是否重试, 默认为否
        :return:
        """
        if not k:
            k = self.default_config_name
        res = self.c.delete(k, retry=retry)
        if not res:
            raise ZeroDivisionError(f"向diskcache中delete数据失败, key: {k}")

    def pop(self, k=None, default=None, expire_time: bool = False, tag: bool = False, retry: bool = False, read: bool = False,):
        """
        删除值, 但同时返回值
        :param k: key名
        :param retry: 是否重试, 默认为否
        :param default: 如果对应的键值没有，则返回这个default设置的默认值
        :param expire_time: 同时返回缓存的过期时间(linux秒数), 这样会使结果变为元组, 默认为False
        :param tag: 同时返回注释, 这样会使结果变为元组
        :return:
        """
        if not k:
            k = self.default_config_name
        res = self.c.pop(k, default=default, expire_time=expire_time, tag=tag, retry=retry)
        if not res:
            raise ZeroDivisionError(f"向diskcache中delete数据失败, key: {k}")

        return res

    def expire(self):
        """
        diskcache并不会主动删除过期数据, 需要手动清除所有过期数据
        :return:
        """
        self.c.expire()

    def create_db(self, is_delete):
        # 如果不存在则新建目录
        os.makedirs(os.path.dirname(self.config_filepath), mode=0o777, exist_ok=True)

    def getall_key(self):
        """
        获取所有键
        """
        res = []
        self.c.expire()
        res_iter = self.c.iterkeys()
        # print(list(res))
        res = list(res_iter)
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
