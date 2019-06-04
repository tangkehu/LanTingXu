
import time
import xml.etree.ElementTree as ET
from flask import request
from . import api_bp


@api_bp.route('/wx/msg', methods=['GET', 'POST'])
def wx_msg():
    """ 微信消息接收及被动回复API """

    msg = parse_xml(request.data)
    if isinstance(msg, MsgRequest) and msg.MsgType == 'text':
        to_user = msg.FromUserName
        from_user = msg.ToUserName
        content = "感谢关注兰亭续文创工作室官方公众号，开业活动即将开始！敬请期待..."
        reply_msg = TextMsgResponse(to_user, from_user, content)
        return reply_msg.send()
    else:
        return "success"


def parse_xml(web_data):
    """ 解析接收到微信消息的Request请求中的XML数据 """

    try:
        xml_data = ET.fromstring(web_data)
    except ET.ParseError:
        return None
    else:
        msg_type = xml_data.find('MsgType').text
        if msg_type == 'text':
            return TextMsgRequest(xml_data)
        elif msg_type == 'image':
            return ImageMsgRequest(xml_data)


class MsgRequest:
    """ 微信消息Request的xml格式解析 """

    def __init__(self, xml_data):
        self.ToUserName = xml_data.find('ToUserName').text
        self.FromUserName = xml_data.find('FromUserName').text
        self.CreateTime = xml_data.find('CreateTime').text
        self.MsgType = xml_data.find('MsgType').text
        self.MsgId = xml_data.find('MsgId').text


class TextMsgRequest(MsgRequest):
    def __init__(self, xml_data):
        super(TextMsgRequest, self).__init__(xml_data)
        self.Content = xml_data.find('Content').text.encode("utf-8")


class ImageMsgRequest(MsgRequest):
    def __init__(self, xml_data):
        super(ImageMsgRequest, self).__init__(xml_data)
        self.PicUrl = xml_data.find('PicUrl').text
        self.MediaId = xml_data.find('MediaId').text


class MsgResponse:
    """ 微信消息Response的xml格式生成 """

    def __init__(self, to_user_name, from_user_name):
        self._dict = dict()
        self._dict['ToUserName'] = to_user_name
        self._dict['FromUserName'] = from_user_name
        self._dict['CreateTime'] = int(time.time())

    def send(self):
        return "success"


class TextMsgResponse(MsgResponse):
    def __init__(self, to_user_name, from_user_name, content):
        super(TextMsgResponse, self).__init__(to_user_name, from_user_name)
        self._dict['Content'] = content

    def send(self):
        xml_form = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return xml_form.format(**self._dict)


class ImageMsgResponse(MsgResponse):
    def __init__(self, to_user_name, from_user_name, media_id):
        super(ImageMsgResponse, self).__init__(to_user_name, from_user_name)
        self._dict['MediaId'] = media_id

    def send(self):
        xml_form = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Image>
        </xml>
        """
        return xml_form.format(**self._dict)
