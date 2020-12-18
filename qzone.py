import _thread
import datetime
import demjson
import os
import re
import re
import requests
import smtplib
import time
from PIL import Image
from email.header import Header
from email.mime.text import MIMEText
from flask import Flask
from flask import Response
from flask import request
from selenium import webdriver
from flask import render_template

import login

app = Flask(__name__)


def get_cookie(qq, pwd):
    cookie = login.loginBefore(qq, pwd)  # 获取cookie
    if cookie == 'more':
        email('WARNING', 'MORE THAN TWICE', qq)
        return
    gogogo(cookie, qq, pwd)  # 启动点赞程序


def gogogo(cookie, qq, pwd):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    cookie, gtk = get_args(cookie)  # 格式化cookie,并且计算gtk
    headers['Cookie'] = cookie
    i = 0
    while True:  # 开始运行脚本
        data = get_content(headers, gtk, qq)  # 获取content
        if data == 'need login':  # 如果返回need login即为cookie过期,发送邮件并且重新get_cookie
            email('WARNING', 'NEED LOGIN', qq)
            break
        for d in data:  # 为每一个说说点赞
            do_like(d, gtk, headers, qq)
        if i % 12 == 0:
            print_time()
            print('PROGRAM WORKING...' + qq)  # 控制台打印该qq运行脚本状态
        i = i + 1
        if i == 1: email('CONGRATULATE', 'PROGRAM WORKING...', qq)  # 第一次运行完后,发送成功邮件
        time.sleep(292)  # 时间间隔,可自行调整
    get_cookie(qq, pwd)


# 以下函数为辅助函数,均与主进程无关

def get_args(cookie):
    for c in cookie:
        if c['name'] == 'p_skey':
            p_skey = c['value']
            break
    cookie = change_cookie(cookie)  # 格式化cookie
    gtk = get_gtk(p_skey)  # 计算gtk
    return cookie, gtk


def change_cookie(cookie):
    s = ''
    for c in cookie:
        s = s + c['name'] + '=' + c['value'] + '; '
    return s


def get_gtk(p_skey):
    hash = 5381
    for i in p_skey:
        hash += (hash << 5) + ord(i)
    return hash & 0x7fffffff


def get_content(headers, gtk, qq):
    try:
        r = requests.get(
            'https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds3_html_more?uin=' + qq + '&g_tk=' + str(
                gtk), headers=headers)
        r = r.text[10:-2]
        r = demjson.decode(r)
        if ('data' in r):
            data = r['data']['data']
            return data
        else:
            return 'need login'
    except:
        print('get_content错误')
        return []


def do_like(d, gtk, headers, qq):
    url = 'https://user.qzone.qq.com/proxy/domain/w.qzone.qq.com/cgi-bin/likes/internal_dolike_app?g_tk=' + str(gtk)

    body = {
        'qzreferrer': 'http://user.qzone.qq.com/' + qq,
        'opuin': qq,
        'from': 1,
        'active': 0,
        'fupdate': 1
    }

    try:
        html = d['html']

        # print(html)
        # unikey = re.search(r'data-unikey=\"http:[^"]*\"', html).group(0)
        # curkey = re.search(r'data-curkey=\"http:[^"]*\"', html).group(0)
        # print(unikey, curkey)

        temp = re.search(
            'data-unikey="(http[^"]*)"[^d]*data-curkey="([^"]*)"[^d]* data-clicklog=("like")[^h]*href="javascript:;"',
            html);

        if temp is None:
            return

        unikey = temp.group(1)
        curkey = temp.group(2)

        # print(unikey, curkey)

        body['unikey'] = unikey
        body['curkey'] = curkey
        body['appid'] = d['appid']
        body['typeid'] = d['typeid']
        body['fid'] = d['key']

        r = requests.post(url, data=body, headers=headers)
    except:
        return


def print_time():
    print(datetime.datetime.now(), end=' ')
    return


@app.route('/', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'GET':
        return render_template("index.html", position="login")  # 打开客户端页面
    if request.method == 'POST':
        qq = request.form['qq']
        pwd = request.form['pwd']
        _thread.start_new_thread(get_cookie, (qq, pwd))  # 打开新线程
        return render_template("index.html", position="continue")


@app.route('/email')
def email(title='test', content='test', id='123456789'):
    sender = '123456789@qq.com'
    receivers = [id + '@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header("自动点赞脚本", 'utf-8')
    message['To'] = Header(id, 'utf-8')
    message['Subject'] = Header(title, 'utf-8')
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.qq.com', 587)
        smtpObj.login('123456789@qq.com', 'qq邮箱授权码')
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        return 'finish'
    except smtplib.SMTPException:
        return 'error'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
