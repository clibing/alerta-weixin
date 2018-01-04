# coding: utf-8

import json
import os
import datetime
import requests
import logging
try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

'''
#################################################################
微信企业号推送消息

author: clibing 458914534@qq.com
blog: https://blog.linuxcrypt.cn
Github:  https://github.com/clibing/alerta-weixin.git

#################################################################
'''

LOG = logging.getLogger('alerta.plugins.weixin')

DEFAULT_CORP_ID = ''
DEFAULT_CORP_SECRET = ''
DEFAULT_AGENT_ID = ''
DEFAULT_PARTY_ID = ''
DEFAULT_USER_ID = ''
DEFAULT_TAG_ID = ''

CORP_ID = os.environ.get('CORP_ID') or app.config.get('CORP_ID', DEFAULT_CORP_ID)
CORP_SECRET = os.environ.get('CORP_SECRET') or app.config.get('CORP_SECRET', DEFAULT_CORP_SECRET)
AGENT_ID = os.environ.get('AGENT_ID') or app.config.get('AGENT_ID', DEFAULT_AGENT_ID)

PARTY_ID = os.environ.get('PARTY_ID') or app.config.get('PARTY_ID', DEFAULT_PARTY_ID)
USER_ID = os.environ.get('USER_ID') or app.config.get('USER_ID', DEFAULT_USER_ID)
TAG_ID = os.environ.get('TAG_ID') or app.config.get('TAG_ID', DEFAULT_TAG_ID)


class WeixinCore(object):
    def __init__(self, *args):
        super(WeixinCore, self).__init__(*args)
        self.corp_id = CORP_ID                  # 企业号id
        self.corp_secret = CORP_SECRET          # 企业通信秘钥
        self.agent_id = AGENT_ID                # 应用id
        self.party_id = PARTY_ID                # 部门id
        self.user_id = USER_ID                  # 用户id，多人用 | 分割，全部用 @all
        self.tag_id = TAG_ID                    # 标签id
        self.access_token = ''                  # 微信身份令牌
        self.expires_in = datetime.datetime.now()-datetime.timedelta(seconds=60)

    # 微信基本请求URI前缀
    @property
    def server_uri(self):
        return "https://qyapi.weixin.qq.com"

    # 生成获取access_token的uri
    @property
    def access_token_uri(self):
        return self.server_uri() + "/cgi-bin/gettoken?corpid=%&corpsecret=%" % (self.crop_id, self.corp_secret)

    # 最新微信企业号调整校验规则，tagid必须是string类型，如果是数字类型会报错，故而使用str()函数进行转换
    @property
    def create_payload(self, data):
        return {
            "touser": self.user_id and str(self.user_id) or '',     # 用户账户，建议使用tag
            "toparty": self.party_id and str(self.party_id) or '',  # 部门id，建议使用tag
            "totag": self.tag_id and str(self.tag_id) or '',        # tag可以很灵活的控制发送群体细粒度。比较理想的推送应该是，在heartbeat或者其他elastic工具自定义字段，添加标签id。这边根据自定义的标签id，进行推送
            'msgtype': "text",
            "agentid": self.agent_id,
            "text": {
                "content": data.encode('UTF-8')                  # 避免中文字符发送失败
            },
            "safe": "0"
        }
    # 生成发送数据的URI
    @property
    def send_uri(self):
        access_token = self.get_access_token()
        return self.server_uri + '/cgi-bin/message/send?access_token=%s' % access_token

    # 获取access_token，当本地可用直接返回
    @property
    def get_access_token(self):
        # 检查本地access_token是否过期
        if self.expires_in >= datetime.datetime.now() and self.access_token:
            return self.access_token

        # 获取新的access_token
        try:
            response = requests.get(self.access_token_uri)
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception("get access_token failed , stacktrace:%s" % e)

        token_json = response.json()

        # check access_token is exist
        if 'access_token' not in token_json:
            raise Exception("get access_token failed , , the response is :%s" % response.text())

        # 获取access_token和expires_in
        self.access_token = token_json['access_token']
        self.expires_in = datetime.datetime.now() + datetime.timedelta(seconds=token_json['expires_in'])
        return self.access_token

    '''
    封装发送微信数据
    https://work.weixin.qq.com/api/doc#10167/%E6%96%87%E6%9C%AC%E6%B6%88%E6%81%AF
    {
        "touser": "UserID1|UserID2|UserID3",
        "toparty": "PartyID1|PartyID2",
        "totag": "TagID1 | TagID2",
        "msgtype": "text",
        "agentid": 1,
        "text": {
            "content": "你的快递已到，请携带工卡前往邮件中心领取。\n出发前可查看<a href=\"http://work.weixin.qq.com\">邮件中心视频实况</a>，聪明避开排队。"
        },
        "safe": 0
    }
    参数	 是否必须	说明
    touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向该企业应用的全部成员发送
    toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
    totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
    msgtype	是	消息类型，此时固定为：text
    agentid	是	企业应用的id，整型。可在应用的设置页面查看
    content	是	消息内容，最长不超过2048个字节
    safe	否	表示是否是保密消息，0表示否，1表示是，默认0
    '''
    @classmethod
    def send_data(self, content):
        # 参考 http://blog.csdn.net/handsomekang/article/details/9397025
        # len utf8 3字节，gbk2 字节，ascii 1字节
        if len(content) > 2048:
            content = content[:2045] + "..."

        send_url = self.send_uri()

        headers = {'content-type': 'application/json'}

        payload = self.create_payload(content)

        try:
            response = requests.post(send_url, data=json.dumps(payload, ensure_ascii=False), headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception("send message has error: %s" % e)

        LOG.info("send msg and response: %s" % response.text )

    @classmethod
    def get_info(self):
        return {'type': 'WeChat'}
