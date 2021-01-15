# -*- coding:utf-8 -*-


import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import json
from loguru import logger

app = Flask(__name__)


@app.route('/')
def hello():
    return '''
    hello, this is fund value getting sever<br>
    你可以使用post请求访问这个服务，地址:<br>
    http://121.4.78.151:5000/get_special_fund<br>
    传入的数据格式为:<br>
    {'code':'110011','nums':'100','cost':'8.566'}<br>
    返回数据格式为:<br>
    {'fund_code': '110011', <br>
    'fund_name': '易方达中小盘混合 ', <br>
    'predict_assets': 74.93, //预测持有收益 <br>
     'predict_income': -23.5905,//预测当日收益 <br>
     'predict_value': 9.3153}//预测当日收益
    
    '''

def get_special_fund(code,nums,cost):
    '''
    输入:
    code: 基金代码
    nums: 持有份额
    cost: 成本单位净值
    返回:
    fund_code: 基金代码
    fund_name: 基金名称
    predict_value: 当日预测净值
    predict_income: 当日预计收益
    predict_assets: 持仓收益
    '''
    try:
        nums = float(nums)
        cost = float(cost)
        if len(code) != 6:
            logger.error('基金代码位数不为6，请核对基金代码')
            return 0, 0, '基金代码位数不为6，请核对基金代码', 0 , 0
        url = f'http://fundf10.eastmoney.com/jjjz_'+ str(code)+'.html'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER'
        }
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        resp_text = resp.text
        soup = BeautifulSoup(resp_text,'html.parser')
        values = soup.select('body > div > div.mainFrame > div.r_cont > div.basic-new > div.bs_jz > div.col-right > p > label')
        tmp_predict = values[0].text.strip().replace('盘中估算：','').split('\n')
        predict_val = float(tmp_predict[0])
        predict_rate = float(tmp_predict[2].strip('%'))/100
        #计算当日收益
        today_val = round(float(values[1].text.strip().split('\r\n')[2].strip().split('(')[0]),4)
        predict_income = round(today_val * nums * predict_rate,4)
        #计算持仓收益
        predict_assets = round((predict_val - cost) * nums,4)
        title = soup.select('body > div > div.mainFrame > div.r_cont > div.basic-new > div.bs_jz > div.col-left > h4 ')
        title_name = title[0].text.strip()[:-8]
        return code, title_name, predict_val, predict_income, predict_assets
    except Exception as e:
        print('e',e)
        logger.error('该基金代码不存在或者不能爬取到，请核对代码')
        return 0, 0, 0,  '该基金代码不存在或者不能爬取到，请核对代码',0


@app.route('/get_special_fund',methods=['GET','POST'])
def get_value():
    # 接收数据
    try:
        original_dir = request.get_json()
        code = original_dir['code'].strip()
        nums = original_dir['nums'].strip()
        cost = original_dir['cost'].strip()
        fund_code, fund_name, fund_value, predict_income, predict_assets = get_special_fund(code, nums, cost)
        if fund_code == 0:
            return jsonify({'error':fund_value})
        else:
            final_dir = {}
            final_dir['fund_code'] = code
            final_dir['fund_name'] = fund_name
            final_dir['predict_value'] = fund_value
            final_dir['predict_income'] = predict_income
            final_dir['predict_assets'] = predict_assets
            return jsonify(final_dir)
    except Exception as e:
        logger.error('输入参数有误，请核对后再次请求,报错信息:{}'.format(e))
        return jsonify({'error':'输入参数有误，请核对后再次请求'})



if __name__ == '__main__':
    app.run(threaded=True, debug=True,host='0.0.0.0',port=5000)