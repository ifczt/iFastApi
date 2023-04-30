# Author: IFCZT
# Email: ifczt@qq.com
import re


def path_to_key(path):
    return re.sub(r'/', ':', path.strip('/'))
