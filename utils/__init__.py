# Author: IFCZT
# Email: ifczt@qq.com
import hashlib
import re
from random import random


def path_to_key(path):
    return re.sub(r'/', ':', path.strip('/'))


# 多个装饰器合并
# 列如 @icompose(classmethod, idb)
def icompose(*funs):
    def deco(f):
        for fun in reversed(funs):
            f = fun(f)
        return f

    return deco


# 生成密码
def encryption_md5(value: [str, bool]):
    return hashlib.md5(value.encode(encoding='UTF-8')).hexdigest()
