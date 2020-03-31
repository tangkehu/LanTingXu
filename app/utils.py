import os
import uuid
import json
import requests
from PIL import Image
from functools import wraps
from logging.handlers import SMTPHandler
from flask_login import current_user
from flask import abort, current_app


def random_filename(filename):
    """ 随机文件名 """
    ext = os.path.splitext(filename)[1]
    return uuid.uuid4().hex + ext


def resize_img(path, filename, size: int, file_obj=None, save_flg=False):
    """ 根据给定大小对图片进行百分比缩小 """
    prefix, ext = os.path.splitext(filename)
    img = Image.open(file_obj) if file_obj else Image.open(os.path.join(path, filename))
    width = img.size[0]
    height = img.size[1]
    if width <= size or height <= size:
        if save_flg:
            img.save(os.path.join(path, filename), optimize=True, quality=85)
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


def goods_img_ratio(filename):
    try:
        img = Image.open(os.path.join(current_app.config['GOODS_IMG_PATH'], filename))
        width = img.size[0]
        height = img.size[1]
    except Exception as e:
        current_app.logger.info(str(e))
        width = 100
        height = 100
    return height/width


def goods_order_map(way='flow', index=1, li=False):
    """ 商品排序MAP，按不同的方式获取相应的内容 """
    from .models import Goods
    order_dic = {
        'flow': (Goods.view_count.desc(), '综合排序'),
        'date_up': (Goods.updata_time.asc(), '时间升序'),
        'date_down': (Goods.updata_time.desc(), '时间降序'),
        'price_up': (Goods.price.asc(), '价格升序'),
        'price_down': (Goods.price.desc(), '价格降序')
    }
    return order_dic[way][index] if li is False else [(one, order_dic[one][1]) for one in order_dic]


# Provide a class to allow SSL (Not TLS) connection for mail handlers by overloading the emit() method
class SSLSMTPHandler(SMTPHandler):
    def emit(self, record):
        """ Emit a record. 465端口发送支持SSL的邮件"""
        try:
            import smtplib
            import email.utils
            from email.message import EmailMessage
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP_SSL(self.mailhost, port)
            msg = EmailMessage()
            msg['From'] = self.fromaddr
            msg['To'] = ','.join(self.toaddrs)
            msg['Subject'] = self.getSubject(record)
            msg['Date'] = email.utils.localtime()
            msg.set_content(self.format(record))
            if self.username:
                smtp.login(self.username, self.password)
            smtp.send_message(msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def permission_required(permission):
    """ 用于进行权限验证的装饰器 """
    def decorator(fun):
        @wraps(fun)
        def decorator_fun(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return fun(*args, **kwargs)
        return decorator_fun
    return decorator


class TuringApi:
    """ 图灵机器人文字聊天 """

    def __init__(self, text):
        self.msg = ''

        _data = {
            'input_text': text,
            'robot_id': "205892",
            'user_info': {
                'open_id': "87f78815-6d56-4c3c-be0c-336318afe239"
            }
        }
        try:
            rep = requests.post('http://open.turingapi.com/v1/openapi', json.dumps(_data)).json()
        except Exception as e:
            pass
        else:
            if rep.get('code') == 200 and rep.get('msg') == 'success':
                for item in rep['result']['datas']:
                    self.msg += item['value']+'\n'
