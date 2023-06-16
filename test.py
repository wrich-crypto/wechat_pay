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

call_back_server_domain = 'https://www.blk123.com/api'

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