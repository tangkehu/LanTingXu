import os
import uuid


def random_filename(filename):
    """ 随机文件名 """
    ext = os.path.splitext(filename)[1]
    return uuid.uuid4().hex + ext
