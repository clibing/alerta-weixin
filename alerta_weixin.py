import logging
from weixin_core import WeixinCore

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.weixin')

wxc = WeixinCore()

AlertLevel = {
    'Severity': False,
    'critical': True,
    'major': False,
    'minor': False,
    'warning': False,
    'indeterminate': False,
    'cleared': False,
    'normal': False,
    'ok': False,
    'informational': False,
    'debug': False,
    'trace': False,
    'unknown': False
}


class WeixinPush(PluginBase):
    """
       will push message to weixin when alert level is danger
    """
    def pre_receive(self, alert):
        LOG.debug("alert message will handle by weixin push plugin")

        level = alert.severity

        if level not in AlertLevel or not AlertLevel[level]:
            LOG.info("alert severity level: %s is not support will skip" % level)
            return alert

        try:
            message = '来源：%s\n服务：%s\n类型：%s\n受影响服务: %s\n事件：[%s](%s)\n详细内容：%s\n所属组：%s\n所属资源：%s' \
               % (alert.origin, alert.service, alert.event_type, alert.correlate,
                  alert.event, alert.value, alert.text, alert.group, alert.resource)
            wxc.send_data(message)
        except Exception as e:
            LOG.error("send weixin message is error: %s" % e)
        return alert

    def post_receive(self, alert):
        pass

    def status_change(self, alert, status, text):
        pass

    def create_data(self, alert):
        return