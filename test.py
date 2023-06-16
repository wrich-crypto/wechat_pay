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

def request_payment_notify(amount, out_trade_no):
    url = f"{call_back_server_domain}/user/pay/notify"
    headers = {'Content-Type': 'application/json'}
    data = {
        "amount": amount,
        "out_trade_no": out_trade_no
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response

request_payment_notify(2000, '123')