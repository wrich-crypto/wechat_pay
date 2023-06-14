# -*- coding: utf-8 -*-
from random import sample
from string import ascii_letters, digits
import requests

from flask import Flask, jsonify, request

from wechatpayv3 import SignType, WeChatPay, WeChatPayType

import json
import logging
import os
import time
import uuid

# 读取配置文件
with open('config.json', 'r') as f:
    config = json.load(f)

# 设置变量
MCHID = config['MCHID']
PRIVATE_KEY_PATH = config['PRIVATE_KEY_PATH']
CERT_SERIAL_NO = config['CERT_SERIAL_NO']
APIV3_KEY = config['APIV3_KEY']
APPID = config['APPID']
APPID_SECRET = config['APPID_SECRET']
NOTIFY_URL = config['NOTIFY_URL']
CERT_DIR = config['CERT_DIR']
LOGGER_NAME = config['LOGGER']
PARTNER_MODE = config['PARTNER_MODE']
PROXY = config['PROXY']
call_back_server_domain = config['call_back_server_domain']

# 使用变量
print("MCHID:", MCHID)
print("PRIVATE_KEY_PATH:", PRIVATE_KEY_PATH)
print("CERT_SERIAL_NO:", CERT_SERIAL_NO)
print("APIV3_KEY:", APIV3_KEY)
print("APPID:", APPID)
print("NOTIFY_URL:", NOTIFY_URL)
print("CERT_DIR:", CERT_DIR)
print("LOGGER:", LOGGER_NAME)
print("PARTNER_MODE:", PARTNER_MODE)
print("PROXY:", PROXY)
print("call_back_server_domain", call_back_server_domain)

# 商户证书私钥
with open(PRIVATE_KEY_PATH) as f:
    PRIVATE_KEY = f.read()
    print("PRIVATE_KEY:", PRIVATE_KEY)

# 日志记录器，记录web请求和回调细节
logging.basicConfig(filename=os.path.join(os.getcwd(), 'demo.log'), level=logging.DEBUG, filemode='a', format='%(asctime)s - %(process)s - %(levelname)s: %(message)s')
LOGGER = logging.getLogger(LOGGER_NAME)

# 初始化
wxpay = WeChatPay(
    wechatpay_type=WeChatPayType.NATIVE,
    mchid=MCHID,
    private_key=PRIVATE_KEY,
    cert_serial_no=CERT_SERIAL_NO,
    apiv3_key=APIV3_KEY,
    appid=APPID,
    notify_url=NOTIFY_URL,
    cert_dir=CERT_DIR,
    logger=LOGGER,
    partner_mode=PARTNER_MODE,
    proxy=PROXY)

app = Flask(__name__)


@app.route('/pay')
def pay():
    # 以native下单为例，下单成功后即可获取到'code_url'，将'code_url'转换为二维码，并用微信扫码即可进行支付测试。
    out_trade_no = ''.join(sample(ascii_letters + digits, 8))
    description = '平台充值'
    amount = int(request.args.get('amount'))
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        pay_type=WeChatPayType.NATIVE
    )
    return jsonify({'code': code, 'out_trade_no': out_trade_no, 'amount': amount, 'message': message})


@app.route('/pay_jsapi')
def pay_jsapi():
    # 以jsapi下单为例，下单成功后，将prepay_id和其他必须的参数组合传递给JSSDK的wx.chooseWXPay接口唤起支付
    out_trade_no = ''.join(sample(ascii_letters + digits, 8))
    description = '平台充值'
    amount = int(request.args.get('amount'))
    opend_id = request.args.get('openid')
    payer = {'openid': opend_id}
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        pay_type=WeChatPayType.JSAPI,
        payer=payer
    )
    result = json.loads(message)
    if code in range(200, 300):
        prepay_id = result.get('prepay_id')
        timestamp = str(int(time.time()))
        noncestr = uuid.uuid4().hex
        package = 'prepay_id=' + prepay_id
        paysign = wxpay.sign([APPID, timestamp, noncestr, package])
        signtype = 'RSA'
        return jsonify({'code': 0, 'result': {
            'appId': APPID,
            'timeStamp': timestamp,
            'nonceStr': noncestr,
            'package': 'prepay_id=%s' % prepay_id,
            'signType': signtype,
            'paySign': paysign
        }})
    else:
        return jsonify({'code': -1, 'out_trade_no': out_trade_no, 'amount': amount, 'result': {'reason': result.get('code')}})


@app.route('/pay_h5')
def pay_h5():
    # 以h5下单为例，下单成功后，将获取的的h5_url传递给前端跳转唤起支付。
    out_trade_no = ''.join(sample(ascii_letters + digits, 8))
    description = '平台充值'
    amount = int(request.args.get('amount'))
    scene_info = {'payer_client_ip': '1.2.3.4', 'h5_info': {'type': 'Wap'}}
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        pay_type=WeChatPayType.H5,
        scene_info=scene_info
    )
    return jsonify({'code': code, 'out_trade_no': out_trade_no, 'amount': amount, 'message': message})


@app.route('/pay_miniprog')
def pay_miniprog():
    # 以小程序下单为例，下单成功后，将prepay_id和其他必须的参数组合传递给小程序的wx.requestPayment接口唤起支付
    out_trade_no = ''.join(sample(ascii_letters + digits, 8))
    description = 'demo-description'
    amount = 1
    payer = {'openid': 'demo-openid'}
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        pay_type=WeChatPayType.MINIPROG,
        payer=payer
    )
    result = json.loads(message)
    if code in range(200, 300):
        prepay_id = result.get('prepay_id')
        timestamp = 'demo-timestamp'
        noncestr = 'demo-nocestr'
        package = 'prepay_id=' + prepay_id
        paysign = wxpay.sign(data=[APPID, timestamp, noncestr, package], sign_type=SignType.RSA_SHA256)
        signtype = 'RSA'
        return jsonify({'code': 0, 'result': {
            'appId': APPID,
            'timeStamp': timestamp,
            'nonceStr': noncestr,
            'package': 'prepay_id=%s' % prepay_id,
            'signType': signtype,
            'paySign': paysign
        }})
    else:
        return jsonify({'code': -1, 'result': {'reason': result.get('code')}})


@app.route('/pay_app')
def pay_app():
    # 以app下单为例，下单成功后，将prepay_id和其他必须的参数组合传递给IOS或ANDROID SDK接口唤起支付
    out_trade_no = ''.join(sample(ascii_letters + digits, 8))
    description = 'demo-description'
    amount = 1
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        pay_type=WeChatPayType.APP
    )
    result = json.loads(message)
    if code in range(200, 300):
        prepay_id = result.get('prepay_id')
        timestamp = 'demo-timestamp'
        noncestr = 'demo-nocestr'
        package = 'Sign=WXPay'
        paysign = 'demo-sign'
        return jsonify({'code': 0, 'result': {
            'appid': APPID,
            'partnerid': MCHID,
            'prepayid': prepay_id,
            'package': package,
            'nonceStr': noncestr,
            'timestamp': timestamp,
            'sign': paysign
        }})
    else:
        return jsonify({'code': -1, 'result': {'reason': result.get('code')}})


@app.route('/notify', methods=['POST'])
def notify():
    print("notify begin")

    result = wxpay.callback(request.headers, request.data)
    if result and result.get('event_type') == 'TRANSACTION.SUCCESS':
        resp = result.get('resource')
        appid = resp.get('appid')
        mchid = resp.get('mchid')
        out_trade_no = resp.get('out_trade_no')
        transaction_id = resp.get('transaction_id')
        trade_type = resp.get('trade_type')
        trade_state = resp.get('trade_state')
        trade_state_desc = resp.get('trade_state_desc')
        bank_type = resp.get('bank_type')
        attach = resp.get('attach')
        success_time = resp.get('success_time')
        payer = resp.get('payer')
        amount = resp.get('amount').get('total')
        print(f"resp:{resp} appid:{appid}\n")

        response = request_payment_notify(amount, out_trade_no)
        print(response.json())

        return jsonify({'code': 'SUCCESS', 'message': '成功'})
    else:
        return jsonify({'code': 'FAILED', 'message': '失败'}), 500

@app.route('/get_openid', methods=['GET'])
def get_openid():
    code = request.args.get('code')
    print(f"code:{code} \n")
    if not code:
        return jsonify({'error': 'Missing code parameter.'})

    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': APPID,  # Replace with your App ID
        'secret': APPID_SECRET,  # Replace with your App Secret
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    response = r.json()

    if 'openid' in response:
        return jsonify({'openid': response['openid']})
    else:
        return jsonify({'error': 'Could not get OpenID.'})

def request_payment_notify(amount, out_trade_no):
    url = f"{call_back_server_domain}/user/pay/notify"
    headers = {'Content-Type': 'application/json'}
    data = {
        "amount": amount,
        "out_trade_no": out_trade_no
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response

@app.route('/MP_verify_uojEHjZVAqTrxeKU.txt')
def serve_verification_file():
    return 'uojEHjZVAqTrxeKU'

if __name__ == '__main__':
    app.run(port=8899)
