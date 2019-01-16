import os
import uuid
from PIL import Image
from logging.handlers import SMTPHandler


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
