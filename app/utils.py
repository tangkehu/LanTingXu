import os
import uuid
from PIL import Image


def random_filename(filename):
    """ 随机文件名 """
    ext = os.path.splitext(filename)[1]
    return uuid.uuid4().hex + ext


def resize_img(path, filename, size: int):
    """ 根据给定大小对图片进行百分比缩小 """
    prefix, ext = os.path.splitext(filename)
    img = Image.open(os.path.join(path, filename))
    width = img.size[0]
    height = img.size[1]
    if width <= size or height <= size:
        return filename
    else:
        if width < height:
            w_percent = size/float(width)
            w_size = size
            h_size = int(height*w_percent)
        else:
            h_percent = size/float(height)
            h_size = size
            w_size = int(width*h_percent)
        img = img.resize((w_size, h_size), Image.ANTIALIAS)
        filename = prefix+'_'+str(size)+ext
        img.save(os.path.join(path, filename), optimize=True, quality=85)
        return filename
