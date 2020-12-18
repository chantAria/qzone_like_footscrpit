from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from location import locate
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
import random


def save_pic(driver):
    imgUse = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div[1]/div[2]/img').get_attribute('src')
    imgU = requests.get(imgUse)
    imgU = imgU.content
    with open('./src.jpg', 'wb') as f:
        f.write(imgU)
        f.close()


def openAndWait(qq, pwd, driver):
    url = 'https://i.qq.com/'
    username = qq
    password = pwd

    driver.get(url)
    time.sleep(1)
    login_frame = driver.find_element_by_id('login_frame')
    driver.switch_to_frame(login_frame)
    driver.find_element_by_xpath('/html/body/div[1]/div[9]/a[1]').click()
    nameI = driver.find_element_by_xpath('/html/body/div[1]/div[5]/div/div[1]/div[3]/form/div[1]/div/input').send_keys(
        username)
    pwdI = driver.find_element_by_xpath(
        '/html/body/div[1]/div[5]/div/div[1]/div[3]/form/div[2]/div[1]/input').send_keys(password)
    time.sleep(1)
    submit = driver.find_element_by_xpath('/html/body/div[1]/div[5]/div/div[1]/div[3]/form/div[4]/a/input').click()
    time.sleep(2.5)
    frame = driver.find_element_by_id('tcaptcha_iframe')
    driver.switch_to_frame(frame)


def get_track(distance):
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.15
    # 初速度
    v = 1
    r = [0.9, 0.95, 0.975, 1, 1.025, 1.05, 1.1]
    i = 0
    while current < distance:
        if current < mid:
            a = 1
        else:
            a = -3.5
        v0 = v
        v = v0 + a * t
        r1 = random.choice(r)
        move = v * t * r1
        current += move
        track.append(move)
        if distance - current <= move:
            track.append(distance - current)
            return track
        i = i + 1
    return track


def move(distance, qq, pwd, driver, con=1):
    for n in range(3):
        track = get_track(distance)
        url_login = driver.current_url
        slider = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[1]')
        ActionChains(driver).click_and_hold(slider).perform()
        time.sleep(1)
        i = 0
        for x in track:
            y = random.choice([-2, -1, 0, 1, 2])
            ActionChains(driver).move_by_offset(xoffset=x, yoffset=y).perform()
            t = random.choice([0.007, 0.008, 0.009, 0.010, 0.011])
            if i < 20:
                time.sleep(t * 10)
            else:
                time.sleep(t)
            i += 1
        time.sleep(1)
        ActionChains(driver).release(on_element=slider).perform()
        for j in range(5):
            url_now = driver.current_url
            if url_now != url_login:
                print('登录成功,返回cookies')
                cookies = driver.get_cookies()
                # driver.quit()
                return cookies
            time.sleep(1)
        if n != 2: print('尝试失败,正在进行再次尝试')
    print('多次失败,重新载入页面')
    if con >= 3:
        print('多次登录失败，程序停止')
        return 'more'
    login(qq, pwd, driver, con + 1)


def login(qq, pwd, driver, con=1):
    # 打开网页
    openAndWait(qq, pwd, driver)
    # 保存图片
    save_pic(driver)
    # 判断位置
    x = locate()
    # 转换为实际长度 /1.954
    xBegin = 119.194
    try:
        distance = x - xBegin
    except:
        print('未捕捉到拼图位置,重新载入页面')
        login(qq, pwd, driver, con)
    else:
        distance = distance / 1.72  # 注意,这里需要调整为适合你的大小
        # 模拟鼠标移动
        return move(distance, qq, pwd, driver, con)


def loginBefore(qq, pwd):
    opt = Options()
    opt.add_argument('--headless')
    opt.add_argument('log-level=3')
    driver = webdriver.Chrome(chrome_options=opt)
    try:
        cookie = login(qq, pwd, driver)
    except:
        pass
    finally:
        driver.quit()
    return cookie


if __name__ == '__main__':
    login()
