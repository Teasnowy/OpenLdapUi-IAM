# -*- coding: utf-8 -*-
# pip install --upgrade tencentcloud-sdk-python
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入对应产品模块的client models。
from tencentcloud.sms.v20210111 import sms_client, models
# 导入可选配置类
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
import logging


def send_sms(tel, access_key_id, access_key_secret, data:list, sign_name, template_code, appid):
    """
    :param tel: 手机号码
    :param access_key_id: 登录key
    :param access_key_secret: 登录密钥
    :param data: 短信模板的参数, 是个列表
    :param sign_name: 签名的名字, 注意不是签名ID
    :param template_code: 模板的ID
    :param appid: 应用的appid
    :return:
    """
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey。
        # 为了保护密钥安全，建议将密钥设置在环境变量中或者配置文件中。
        # 硬编码密钥到代码中有可能随代码泄露而暴露，有安全隐患，并不推荐。
        # SecretId、SecretKey 查询: https://console.cloud.tencent.com/cam/capi
        # cred = credential.Credential("secretId", "secretKey")
        cred = credential.Credential(access_key_id, access_key_secret)

        # 实例化一个http选项，可选的，没有特殊需求可以跳过。
        httpProfile = HttpProfile()
        # 如果需要指定proxy访问接口，可以按照如下方式初始化hp（无需要直接忽略）
        # httpProfile = HttpProfile(proxy="http://用户名:密码@代理IP:代理端口")
        httpProfile.reqMethod = "POST"  # post请求(默认为post请求)
        httpProfile.reqTimeout = 10    # 请求超时时间，单位为秒(默认60秒)
        httpProfile.endpoint = "sms.tencentcloudapi.com"  # 指定接入地域域名(默认就近接入)

        # 非必要步骤:
        # 实例化一个客户端配置对象，可以指定超时时间等配置
        clientProfile = ClientProfile()
        clientProfile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法
        clientProfile.language = "zh-CN"
        clientProfile.httpProfile = httpProfile

        # 实例化要请求产品(以sms为例)的client对象
        # 第二个参数是地域信息，可以直接填写字符串ap-guangzhou，支持的地域列表参考 https://cloud.tencent.com/document/api/382/52071#.E5.9C.B0.E5.9F.9F.E5.88.97.E8.A1.A8
        client = sms_client.SmsClient(cred, "ap-nanjing", clientProfile)

        # 实例化一个请求对象，根据调用的接口和实际情况，可以进一步设置请求参数
        # 您可以直接查询SDK源码确定SendSmsRequest有哪些属性可以设置
        # 属性可能是基本类型，也可能引用了另一个数据结构
        # 推荐使用IDE进行开发，可以方便地跳转查阅各个接口和数据结构的文档说明
        req = models.SendSmsRequest()

        # 短信应用ID: 短信SdkAppId在 [短信控制台] 添加应用后生成的实际SdkAppId，示例如1400006666
        req.SmsSdkAppId = str(appid)
        # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名
        req.SignName = str(sign_name)
        # 模板 ID: 必须填写已审核通过的模板 ID
        req.TemplateId = str(template_code)
        # 模板参数: 模板参数的个数需要与 TemplateId 对应模板的变量个数保持一致，，若无模板参数，则设置为空
        req.TemplateParamSet = data
        # 下发手机号码，采用 E.164 标准，+[国家或地区码][手机号]
        # 示例如：+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        req.PhoneNumberSet = [tel]

        resp = client.SendSms(req)
        status_list = resp.SendStatusSet
        # 输出json格式的字符串回包
        # res = json.loads(resp.to_json_string())
        logging.info(f"发送短信成功: {status_list}")
        for i in status_list:
            if i.Code != "Ok":
                logging.error(f"腾讯云发送{tel}的短信{data}失败: {i.Message}")
            else:
                logging.info(f"腾讯云发送{tel}的短信{data}成功")


    except TencentCloudSDKException as err:
        logging.error(f"腾讯云发送{tel}的短信{data}失败: {err}")
        logging.exception(err)
        raise ZeroDivisionError("暗号发送失败")
    except Exception as err:
        logging.error(f"腾讯云发送{tel}的短信{data}遇到了意外的错误, ")
        logging.exception(err)
        raise ZeroDivisionError("暗号发送失败")

