import functools
import logging
import threading
import time
import pymysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB


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
class MysqlPool(object):
    """
    全局共享的数据库连接池, 在启动时就已经初始化了
    """
    def __init__(self, test_str1=123456):
        self.test_str1 = test_str1
        self.POOL = None
        logging.info('准备数据库链接')

    # 这里依然要重写__new__, 是为了添加*args, **kw, 不然使用了装饰器后不能传参了
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def create(self, host, user, password, db,
               port=3306, charset='utf8', maxconnections=5, maxcached=5, maxshared=5, connect_timeout=10):
        """
        创建连接池，确保连接池只创建一次
        """
        logging.info('aaaaaaaaa')
        with threading.RLock():
            if self.POOL is None:
                self.POOL = PooledDB(
                    creator=pymysql,
                    maxconnections=maxconnections,
                    maxcached=maxcached,
                    maxshared=maxshared,
                    blocking=True,
                    setsession=[],
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=db,
                    charset=charset,
                    connect_timeout=connect_timeout,
                )
                logging.info("数据库连接池创建成功")
            else:
                logging.info("连接池已经存在，不重复创建")

    def connect(self):
        if self.POOL is None:
            raise Exception("连接池未初始化，请先调用 create 方法")
        conn = self.POOL.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def connect_close(self, conn, cursor):
        cursor.close()
        conn.close()

    def fetch_all(self, sql, args=None):
        conn, cursor = self.connect()
        try:
            if args is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, args)
            record_list = cursor.fetchall()
        finally:
            self.connect_close(conn, cursor)
            # logging.info(f"{self.test_str1}")
        return record_list

    def fetch_one(self, sql, args=None):
        conn, cursor = self.connect()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        return result

    def transaction(self, sql, args=None):
        conn, cursor = self.connect()
        row = cursor.execute(sql, args)
        conn.commit()
        self.connect_close(conn, cursor)
        return row

    def info(self) -> dict:
        """
        获取当前连接池的信息
        :return:
        """
        return {
            "最大连接数": self.POOL._maxconnections,
            "当前连接数": self.POOL._connections
        }

