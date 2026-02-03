"""
鲸介12306 抢票助手 - 核心逻辑模块
从原 12306_booking_script.py 重构而来，供 GUI 调用

开发者：鲸介 (Whale_DIY)
项目：Auto12306 智能抢票系统
开源协议：MIT License
"""
import re
import time
import random
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import Select


def parse_hhmm_to_minutes(hhmm):
    """将 HH:MM 格式转换为分钟数"""
    try:
        h, m = map(int, hhmm.split(':'))
        return h*60 + m
    except Exception:
        return None


def time_in_range(t, start, end):
    """判断时间是否在范围内"""
    tm = parse_hhmm_to_minutes(t)
    sm = parse_hhmm_to_minutes(start)
    em = parse_hhmm_to_minutes(end)
    if None in (tm, sm, em):
        return False
    return sm <= tm <= em


def extract_depart_time_from_row(row):
    """从表格行中提取出发时间"""
    try:
        cand = row.find_elements(
            By.XPATH,
            ".//td[position()=2 or contains(@class,'cdz') or contains(@class,'cds')]//*[self::strong or self::span or self::div or self::em]"
        )
        for c in cand:
            t = (c.text or '').strip()
            if re.fullmatch(r'([01]\d|2[0-3]):([0-5]\d)', t):
                return t
    except Exception:
        pass
    
    try:
        txt = row.text or ''
        m = re.search(r'(?:^|\s)([01]\d|2[0-3]):([0-5]\d)(?:\s|$)', txt)
        if m:
            return f"{m.group(1)}:{m.group(2)}"
    except Exception:
        pass
    
    return None


def extract_train_number_from_row(row):
    """从表格行中提取车次号"""
    try:
        cand = row.find_elements(By.XPATH, ".//td[1]//*[self::strong or self::span or self::a or self::div]")
        for c in cand:
            t = (c.text or '').strip().upper()
            if re.fullmatch(r'[GDKCTZXYFS]\d{1,5}', t):
                return t
        txt = (row.text or '').upper()
        m = re.search(r'\b([GDKCTZXYFS]\d{1,5})\b', txt)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def click_book_in_row(row, driver):
    """点击表格行中的预订按钮"""
    try:
        btns = row.find_elements(By.XPATH, ".//a[contains(text(),'预订')]")
        if not btns:
            return False
        btn = btns[0]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", btn)
        time.sleep(0.2)
        try:
            btn.click()
            return True
        except Exception:
            driver.execute_script('arguments[0].click();', btn)
            return True
    except Exception as e:
        print(f'点击预订失败: {e}')
        return False


def _find_rows(driver):
    """获取查询结果表格的所有有效数据行"""
    xpath = "//*[@id='queryLeftTable']/tr[not(contains(@class,'ticket-hd')) and not(contains(@style,'display: none'))]"
    return driver.find_elements(By.XPATH, xpath)


def _find_row_by_train_number(driver, target):
    """根据车次号查找对应的表格行"""
    target = (target or '').strip().upper()
    if not target:
        return None
    try:
        nodes = driver.find_elements(By.XPATH, f"//*[@id='queryLeftTable']//a[normalize-space(text())='{target}']/ancestor::tr[1]")
        for n in nodes:
            if n.is_displayed():
                return n
    except Exception:
        pass
    try:
        rows = _find_rows(driver)
        for r in rows:
            tn = extract_train_number_from_row(r)
            if tn == target:
                return r
    except Exception:
        pass
    return None


def book_by_time_range(driver, start_hhmm, end_hhmm, max_attempts=30, refresh_interval=(3,6)):
    """按时间范围抢票"""
    for attempt in range(1, max_attempts+1):
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'queryLeftTable')))
            rows = _find_rows(driver)
            found_times = []
            candidates = []
            for r in rows:
                dep = extract_depart_time_from_row(r)
                if dep:
                    found_times.append(dep)
                if dep and time_in_range(dep, start_hhmm, end_hhmm):
                    if r.find_elements(By.XPATH, ".//a[contains(text(),'预订')]"):
                        candidates.append((dep, r))
            if candidates:
                candidates.sort(key=lambda x: parse_hhmm_to_minutes(x[0]))
                dep, row = candidates[0]
                print(f'发现时间匹配的车次: {dep}，尝试预订...')
                if click_book_in_row(row, driver):
                    return f'成功尝试预订出发时间 {dep} 的车次'
            else:
                if attempt == 1 or attempt % 5 == 0:
                    preview = ','.join(sorted(set(found_times))[:6]) if found_times else '无'
                    print(f'本次共扫描 {len(rows)} 行，解析到出发时刻: {preview}；未命中范围 {start_hhmm}-{end_hhmm}')
        except Exception as e:
            print(f'第{attempt}次尝试失败: {e}')
        
        if attempt < max_attempts:
            try:
                refresh_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'query_ticket')))
                refresh_btn.click()
            except Exception as e:
                print(f'点击查询按钮刷新失败: {e}，尝试整页刷新')
                driver.refresh()
            wait_time = random.uniform(*refresh_interval)
            print(f'无匹配结果，等待{wait_time:.2f}s后重试...')
            time.sleep(wait_time)
    return '没抢到，可惜~'


def book_by_train_number(driver, target_train_number, max_attempts=30, refresh_interval=(2,4)):
    """按指定车次抢票"""
    target = (target_train_number or '').strip().upper()
    if not target:
        return '未设置目标车次'
    for attempt in range(1, max_attempts+1):
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'queryLeftTable')))
            row = _find_row_by_train_number(driver, target)
            if row is not None:
                print(f'发现目标车次 {target}，尝试预订...')
                if click_book_in_row(row, driver):
                    return f'成功尝试预订指定车次 {target}'
        except Exception as e:
            print(f'第{attempt}次尝试失败: {e}')
        
        if attempt < max_attempts:
            try:
                refresh_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'query_ticket')))
                refresh_btn.click()
            except Exception as e:
                print(f'点击查询按钮刷新失败: {e}，尝试整页刷新')
                driver.refresh()
            wait_time = random.uniform(*refresh_interval)
            print(f'未出现目标车次 {target}，等待{wait_time:.2f}s后重试...')
            time.sleep(wait_time)
    return f'未抢到指定车次 {target}，可惜~'


def select_seat_fast(driver, preferred_type="first"):
    """快速选座"""
    print(f"快速选择座位，偏好: {preferred_type}")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'seat-sel-bd'))
        )
    except Exception as e:
        print(f'座位选择对话框加载失败: {e}')
        return False
    try:
        seats = driver.find_elements(By.XPATH, "//div[@class='seat-sel-bd']//a[contains(@href, 'javascript:')]")
        if not seats:
            return False
        seats[0].click()
        print('已快速选择一个座位')
        return True
    except Exception as e:
        print(f'快速选座失败: {e}')
        return False


def setup_browser_and_login():
    """设置浏览器并完成登录（供预登录使用）"""
    edge_options = Options()
    edge_options.add_experimental_option('detach', True)
    edge_options.add_argument('--disable-blink-features=AutomationControlled')
    edge_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.3485.54')
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Edge(options=edge_options)
    
    try:
        driver.get('https://www.12306.cn')
        driver.maximize_window()
        print('✓ 已打开12306官网')
        
        time.sleep(2)
        
        # 登录流程
        try:
            print('正在查找登录按钮...')
            try:
                login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'J-btn-login')))
                login_button.click()
                print('✓ 已点击登录按钮')
            except:
                login_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'登录') or contains(@class,'login')]"))
                )
                login_button.click()
                print('✓ 已点击登录按钮')
        except Exception as e:
            print(f'⚠ 点击登录按钮失败：{e}')
            print('提示：请手动点击页面上的"登录"按钮')
            time.sleep(3)
        
        try:
            print('正在切换到扫码登录...')
            try:
                scan_login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[text()='扫码登录' or contains(text(),'扫码')]"))
                )
                scan_login_button.click()
                print('✓ 已切换到扫码登录')
            except:
                print('提示：可能已在扫码登录页面')
        except Exception as e:
            print(f'⚠ 切换扫码登录失败：{e}')
            print('提示：请手动点击"扫码登录"按钮')
            time.sleep(2)
        
        print('\n📱 请用手机12306 APP扫码登录...')
        print('⏳ 等待扫码中...\n')
        
        # 等待登录成功
        login_success = False
        for i in range(60):
            try:
                try:
                    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[text()='个人中心' or contains(text(),'个人')]")))
                    login_success = True
                    break
                except:
                    if driver.find_elements(By.XPATH, "//*[contains(@class,'user') or contains(@id,'user')]"):
                        login_success = True
                        break
            except Exception:
                pass
            
            if i % 10 == 0 and i > 0:
                print(f'仍在等待扫码... ({i}秒)')
            time.sleep(1)
        
        if not login_success:
            print('❌ 登录超时')
            print('提示：请确保已用12306 APP扫码并确认登录')
            driver.quit()
            return None
        
        print('✓ 登录成功！')
        return driver
    
    except Exception as e:
        print(f'登录过程出错: {e}')
        try:
            driver.quit()
        except:
            pass
        return None


def run_booking_with_driver(driver, params):
    """使用已登录的浏览器实例执行抢票（供GUI调用）"""
    if not driver:
        print('❌ 浏览器实例无效')
        return
    
    print('=' * 60)
    print('🚄 鲸介12306 抢票助手 - 开始抢票')
    print('=' * 60)
    print(f"出发站: {params['from_station']} → 到达站: {params['to_station']}")
    print(f"日期: {params['travel_date']} | 票型: {params['ticket_type']}")
    if params.get('target_train_number'):
        print(f"策略: 指定车次 [{params['target_train_number']}]")
    else:
        tr = params['depart_time_range']
        print(f"策略: 时间范围 [{tr['start']} - {tr['end']}]")
    print('=' * 60)
    
    try:
        # 进入购票页面
        try:
            ticket_link = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, 'link_for_ticket')))
            ticket_link.click()
            time.sleep(0.2)
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
            print('✓ 已进入购票页面')
        except Exception as e:
            print(f'进入购票页面失败：{e}')
            return
        
        # 填写出发站
        try:
            from_station_input = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, 'fromStationText')))
            from_station_input.click()
            from_station_input.clear()
            from_station_input.send_keys(params['from_station'])
            print(f"✓ 已输入出发地: {params['from_station']}")
            first_option = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#citem_0 > span:nth-child(1)')))
            first_option.click()
        except Exception as e:
            print(f'操作出发地输入框失败：{e}')
            return
        
        # 填写到达站
        try:
            to_station_input = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, 'toStationText')))
            to_station_input.click()
            to_station_input.clear()
            to_station_input.send_keys(params['to_station'])
            print(f"✓ 已输入目的地: {params['to_station']}")
            first_option = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#citem_0 > span:nth-child(1)')))
            first_option.click()
        except Exception as e:
            print(f'操作目的地输入框失败：{e}')
            return
        
        # 填写出发日期
        try:
            date_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'train_date')))
            date_input.click()
            date_input.clear()
            date_input.send_keys(params['travel_date'])
            print(f"✓ 已输入出发时间: {params['travel_date']}")
            try:
                driver.find_element(By.CLASS_NAME, 'cal').click()
            except Exception:
                pass
        except Exception as e:
            print(f'时间输入框操作失败：{e}')
            return
        
        # 选择票型
        try:
            if params['ticket_type'] == 'student':
                WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, 'sf2'))).click()
                print('✓ 已选择学生票')
            else:
                WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, 'sf1'))).click()
                print('✓ 已选择成人票')
        except Exception as e:
            print(f'票种选择失败：{e}')
            return
        
        # 等待开售时间
        try:
            bst = (params.get('booking_start_time') or '').strip()
            if bst:
                start_datetime = datetime.strptime(bst, '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                if now < start_datetime:
                    wait_seconds = (start_datetime - now).total_seconds()
                    print(f'等待开售时间，还需 {wait_seconds:.1f} 秒...')
                    if wait_seconds > 10:
                        time.sleep(max(0, wait_seconds - 10))
                    while datetime.now() < start_datetime:
                        time.sleep(0.05)
            print('🚀 到达抢票时间，开始抢票！')
        except Exception as e:
            print(f'时间处理出错: {e}')
            return
        
        # 第一次查询
        try:
            query_button = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, 'query_ticket')))
            query_button.click()
            print('✓ 已提交查询，正在等待结果...')
            time.sleep(0.2)
        except Exception as e:
            print(f'查询失败：{e}')
            return
        
        # 执行抢票策略
        ttn = (params.get('target_train_number') or '').strip().upper()
        if ttn:
            print(f'策略：指定车次 [{ttn}]')
            result_msg = book_by_train_number(driver, ttn, max_attempts=30, refresh_interval=(2,4))
        else:
            tr = params['depart_time_range']
            print(f"策略：时间范围 [{tr['start']} - {tr['end']}]")
            result_msg = book_by_time_range(driver, tr['start'], tr['end'], max_attempts=30, refresh_interval=(2,4))
        print(result_msg)
        
        # 选择乘车人
        try:
            passenger_checkbox = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'normalPassenger_0')))
            passenger_checkbox.click()
            print('✓ 已成功选择乘车人')
        except Exception as e:
            print(f'选择乘车人失败：{e}')
        
        try:
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.ID, 'dialog_xsertcj_ok'))).click()
        except Exception as e:
            print(f'点击确认按钮失败：{e}')
        
        # 订单页票种选择
        try:
            if params['ticket_type'] == 'adult':
                ticket_type_select = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'ticketType_1')))
                Select(ticket_type_select).select_by_value('1')
                print('✓ 订单页已选择票种：成人票')
        except Exception as e:
            print(f'订单页选择票种失败：{e}')
        
        # 提交订单
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'submitOrder_id'))).click()
            print('✓ 已成功点击提交订单按钮')
        except Exception as e:
            print(f'点击提交订单按钮失败：{e}')
        time.sleep(0.4)
        
        # 学生票提示
        if params['ticket_type'] == 'student':
            try:
                WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.ID, 'qd_closeDefaultWarningWindowDialog_id'))).click()
            except Exception as e:
                print(f'点击确认按钮失败：{e}')
        
        # 选座
        select_seat_fast(driver, preferred_type=params.get('seat_position_preference','first'))
        time.sleep(0.8)
        
        # 最终确认
        try:
            WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, 'qr_submit_id'))).click()
            print('✓ 已提交最终确认')
            print('=' * 60)
            print('🎉 抢票流程完成！请在浏览器中完成支付')
            print('=' * 60)
        except Exception as e:
            print(f'点击确认按钮失败：{e}')
    
    except Exception as e:
        print(f'抢票过程出现异常: {e}')
        raise
