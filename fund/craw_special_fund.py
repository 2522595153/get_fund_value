# -*- coding:utf-8 -*-


import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import json

app = Flask(__name__)


@app.route('/')
def hello():
    return "hello, this is fund value getting sever"

def get_special_fund(code):
    try:
        if len(code) != 6:
            print('基金代码位数不为6，请核对基金代码')
            return 0, 0, '基金代码位数不为6，请核对基金代码'
        url = f'http://fundf10.eastmoney.com/jjjz_'+ str(code)+'.html'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER'
        }
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        resp_text = resp.text
        soup = BeautifulSoup(resp_text,'html.parser')
        values = soup.select('body > div > div.mainFrame > div.r_cont > div.basic-new > div.bs_jz > div.col-right > p > label')
        predict_val = values[0].text.strip().replace('盘中估算：','').split('\n')[0]
        title = soup.select('body > div > div.mainFrame > div.r_cont > div.basic-new > div.bs_jz > div.col-left > h4 ')
        title_name = title[0].text.strip()[:-8]
        return code, title_name, predict_val
    except Exception as e:
        print('e',e)
        print('该基金代码不存在或者不能爬取到，请核对代码')
        return 0, 0, '该基金代码不存在或者不能爬取到，请核对代码'


@app.route('/get_special_fund',methods=['GET','POST'])
def get_value():
    # 接收数据
    original_dir = request.get_json()
    code = original_dir['code'].strip()
    print('code:',code)
    fund_code, fund_name, fund_value = get_special_fund(code)
    if fund_code == 0:
        return fund_value
    else:
        final_dir = {}
        final_dir['fund_code'] = code
        final_dir['fund_name'] = fund_name
        final_dir['fund_value'] = fund_value
        return jsonify(final_dir)



if __name__ == '__main__':
    app.run(threaded=True, debug=True,host='0.0.0.0',port=5000)