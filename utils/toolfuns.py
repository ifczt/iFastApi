import hashlib
import re
from random import random


def path_to_key(path):
    return re.sub(r'/', ':', path.strip('/'))


# 生成密码
def encryption_md5(value: [str, bool]):
    return hashlib.md5(value.encode(encoding='UTF-8')).hexdigest()
