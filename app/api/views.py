
import time
import xml.etree.ElementTree as ET
from flask import request,url_for

from app.utils import TuringApi
from . import api_bp


@api_bp.route('/wx/msg', methods=['GET', 'POST'])
def wx_msg():
    """ 微信消息接收及被动回复API """

    msg = parse_xml(request.data)
    if isinstance(msg, MsgRequest):
        to_user = msg.FromUserName
        from_user = msg.ToUserName

        if msg.MsgType == 'text':
            msg_content = msg.Content
            rep_content = "感谢关注兰亭续文创工作室官方公众号，开业活动即将开始！敬请期待..."

            if msg_content == '官网':
                rep_content = "官网地址：https://www.lanting.live/"
            elif msg_content == '服务':
                return NewsMsgResponse(to_user, from_user).send()
            else:
                # 图灵聊天
                turing = TuringApi(msg_content)
                if turing.is_successful and turing.msg != msg_content:
                    rep_content = turing.msg

            return TextMsgResponse(to_user, from_user, rep_content).send()

        if msg.MsgType == 'event':
            return NewsMsgResponse(to_user, from_user).send()

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
        elif msg_type == 'event':
            return EventMsgRequest(xml_data)


class MsgRequest:
    """ 微信消息Request的xml格式解析 """

    def __init__(self, xml_data):
        self.ToUserName = xml_data.find('ToUserName').text
        self.FromUserName = xml_data.find('FromUserName').text
        self.CreateTime = xml_data.find('CreateTime').text
        self.MsgType = xml_data.find('MsgType').text


class TextMsgRequest(MsgRequest):
    """ 普通文本消息 """

    def __init__(self, xml_data):
        super(TextMsgRequest, self).__init__(xml_data)
        self.MsgId = xml_data.find('MsgId').text
        self.Content = xml_data.find('Content').text


class EventMsgRequest(MsgRequest):
    """ 关注/取消关注事件消息 """

    def __init__(self, xml_data):
        super(EventMsgRequest, self).__init__(xml_data)
        self.Event = xml_data.find('Event').text


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


class NewsMsgResponse(MsgResponse):
    def __init__(self, to_user_name, from_user_name):
        super(NewsMsgResponse, self).__init__(to_user_name, from_user_name)
        self._dict['Title'] = '兰亭续文化创意工作室'
        self._dict['Description'] = '以花为媒，以茶代酒，以汉服为心意，以文创为名片，诚邀您来品来评！点击进入...'
        self._dict['PicUrl'] = 'https://www.lanting.live' + url_for("static", filename='img/bg-masthead.jpg')
        self._dict['Url'] = 'https://www.lanting.live/'

    def send(self):
        xml_form = """
        <xml>
          <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
          <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
          <CreateTime>{CreateTime}</CreateTime>
          <MsgType><![CDATA[news]]></MsgType>
          <ArticleCount>1</ArticleCount>
          <Articles>
            <item>
              <Title><![CDATA[{Title}]]></Title>
              <Description><![CDATA[{Description}]]></Description>
              <PicUrl><![CDATA[{PicUrl}]]></PicUrl>
              <Url><![CDATA[{Url}]]></Url>
            </item>
          </Articles>
        </xml>
        """
        return xml_form.format(**self._dict)
