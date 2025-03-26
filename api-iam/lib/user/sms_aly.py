import logging
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class sms_aly:
    """
    发送短信, 直接调用sms_aly().send(...)
    """
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Dysmsapi20170525Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的 AccessKey ID,
            access_key_id=access_key_id,
            # 您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = f'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    @staticmethod
    def send(
        sms, tel, access_key_id, access_key_secret, template_code, sign_name
    ) -> None:
        """

        :param sms: 短信模板内容, 通常是一个字典, 比如模板内容是 "验证码: {content}" ,那么sms就为 {"content": 123456}
        :param tel: 手机号码
        :param access_key_id: 登录用key
        :param access_key_secret: 登录用secret
        :param template_code: 阿里云短信模板code
        :param sign_name: 阿里云短信签名
        :return:
        """
        client = sms_aly.create_client(access_key_id, access_key_secret)
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=tel,
            sign_name=sign_name,
            template_code=template_code,
            template_param=str(sms)
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res = client.send_sms_with_options(send_sms_request, runtime).to_map()
            if res["body"]["Code"] != 'OK':
                logging.error(f'发送{tel}短信: {sms}失败, 返回: {res}')
                raise ZeroDivisionError(f"发送短信失败")

        except Exception as error:
            # 如有需要，请打印 error
            logging.error(f'发送{tel}短信: {sms}失败')
            logging.exception(error)
            raise ZeroDivisionError(f"发送短信失败")
