
import time
import xml.etree.ElementTree as ET
from flask import request, url_for

from app.utils import TuringApi
from app.models import WxUser
from . import api_bp


class MsgContent:
    msg0 = '小店：https://www.lanting.live/\n电话：13398190196\n' \
           '地址：成都大学校园内附属幼儿园对面超市三楼306室 地铁4号线成都大学站D口100米\n\n回复任意消息发现更多好玩'
    msg1 = "兰亭续文创工作室官方公众号感谢您的关注！\n\n" \
           "传承发扬兰亭之义，志趣相投，方得乐也。\n" \
           "以花为媒，以茶代酒，以汉服为心意，以文创为名片，诚邀您来品来评。我们真诚欢迎您的到来！\n\n" \
           "毕业季超值活动开始啦！\n回复'1'领取店铺优惠券\n回复'毕业季活动'了解活动内容\n预定请通过电话加微信联系店员\n更多活动，敬请期待...\n\n" + msg0
    msg2 = "兰亭续文创工作室\n" \
           "毕业季超值活动开始啦！\n回复'1'领取店铺优惠券\n回复'毕业季活动'了解活动内容\n预定请通过电话加微信联系店员\n更多活动，敬请期待...\n\n" + msg0
    msg3 = "官网地址：https://www.lanting.live/"
    msg4 = "恭喜你获得5元毕业季超值活动店铺优惠券一张！\n使用方式：向店铺工作人员出示本消息即可，不得与套餐叠加使用。\n更多活动，敬请期待...\n\n" + msg0
    msg5 = "你已参与该活动，谢谢你的关注！\n更多活动，敬请期待...\n\n" + msg0
    msg6 = "毕业季超值活动详情\n五大项目 24小时体验\n\n" \
           "套餐一：128元套餐\n古典妆容+汉服造型+头饰+道具+租金在80以内的汉服\n\n" \
           "套餐二：158元套餐\n古典妆容+汉服造型+头饰+道具+租金在120以内的汉服\n\n" \
           "套餐三：188元套餐\n古典妆容+汉服造型+头饰+道具+租金在150以内的汉服\n\n" \
           "预订方式：可通过微信、QQ、微博、贴吧预订，6月12日—6月30日预订，7月12日以前有效，以定金为准，定金统一为50元。\n\n" \
           "福利：\n预订人数超过50人，在预订人员中抽一位幸运儿送一套【全新汉服】\n" \
           "关注'兰亭续文创工作室'官方微信公众号，回复暗号'1'即可获得店铺优惠券（不可与活动套餐叠加使用）\n" \
           "QQ帮忙转发即送店铺优惠券（不可与活动套餐叠加使用），转发超过100次，抽送一位一件汉服\n\n" \
           "活动时间：\n2019/6/12 21:00 - 2019/6/30 21:00\n\n以上活动最终解释权归兰亭续文创工作室所有\n\n" + msg0


@api_bp.route('/wx/msg', methods=['GET', 'POST'])
def wx_msg():
    """ 微信消息接收及被动回复API """

    msg = parse_xml(request.data)
    if isinstance(msg, MsgRequest):
        to_user = msg.FromUserName
        from_user = msg.ToUserName
        validate_time = WxUser.validate_time(to_user)  # 每间隔五分钟就补充推广消息
        rep_content = MsgContent.msg1 if validate_time else ''

        if msg.MsgType == 'text':
            msg_content = msg.Content
            if msg_content == '官网':
                rep_content = MsgContent.msg3
            elif msg_content == '1':
                validate_flag = WxUser.validate_flag(to_user)  # 检验是否已参加活动
                rep_content = MsgContent.msg5 if validate_flag else MsgContent.msg4
            elif msg_content == '毕业季活动':
                rep_content = MsgContent.msg6
            else:
                # 聊天
                turing_msg = TuringApi(msg_content).msg
                if turing_msg:
                    rep_content = (turing_msg + '\n' + MsgContent.msg2) if validate_time else turing_msg

        return TextMsgResponse(to_user, from_user, rep_content).send() if rep_content else "success"

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
        else:
            return MsgRequest(xml_data)


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
