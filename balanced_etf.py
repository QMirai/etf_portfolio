import csv
import time
import pandas as pd
import plotly.express as px
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def table_downloader():
    # 使用WebDriverManager来获取Chrome WebDriver
    chrome_service = ChromeService(ChromeDriverManager().install())
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--mute-audio")

    # 创建一个 Chrome WebDriver 实例
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    # 打开网页
    driver.get('https://bmomf.lipperweb.com/bmomf/profile/?symbol=45121:94792&lang=en#History')
    driver.set_window_size(800, 600)
    wait = WebDriverWait(driver, 10)
    button = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'button[data-timeperiod="1-4"]')))
    button.click()
    # 使用ID查找链接元素
    link = driver.find_element(By.ID, 'lnkCsvExport')
    # 点击链接
    link.click()
    while not os.path.isfile(file):  # wait until the file is downloaded
        time.sleep(0.5)
    driver.quit()


def pretreatment_data(investment=5000):
    """
    read the 'Fund History.csv',
    then return three lists dates, navs and real values based on the investment.
    """
    _dates = []
    _navs = []
    with open(file, 'r', encoding='utf-8') as csvfile:
        data = csv.reader(csvfile)
        next(data)
        while True:
            row = next(data)
            if row[0] == '10/12/2023':
                break
            else:
                _dates.append(row[0])
                _navs.append(float(row[1]))
    _dates.reverse()
    _navs.reverse()
    _values = [round(investment/12.9971 * i, 2) for i in _navs]
    return _dates, _navs, _values


def graph_drawer(_dates, _navs, _values):
    """
    wrap three lists into pandas data frame, then feed it to the pylot for graph.
    """
    # DATA FRAME 包装
    data_frame = {
        'Date': _dates,
        'Value': _values,
        'NAV': _navs
    }
    df = pd.DataFrame(data_frame)

    fig = px.line(df, x='Date', y='NAV', title='Value Over Time', text='Value')
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Value')
    fig.update_xaxes(type='category')

    # 在折线上显示标记
    fig.update_traces(textposition="top center")
    fig.update_traces(textfont=dict(size=16))

    # 旋转 X 轴上的日期标签
    fig.update_xaxes(tickangle=45)

    # 显示网格线
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='gray')
    # fig.write_html('interactive_chart.html')
    fig.show()


file = os.path.join("C:\\Users\\small\\Downloads", 'Fund History.csv')
if os.path.isfile(file):  # if there is a "Fund History.csv", remove it for the new one downloaded.
    os.remove(file)
table_downloader()
dates, navs, values = pretreatment_data()
graph_drawer(dates, navs, values)
os.remove(file)


# plt.figure(figsize=(15, 6))
# plt.plot(dates, navs, marker='o', linestyle='-')
# plt.title('NAV Over Time')
# plt.xlabel('Date')
# plt.ylabel('NAV')
# plt.grid(True)
# plt.xticks(dates, rotation=45)
# plt.tight_layout()

# plt.show()
