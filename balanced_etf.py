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


def pretreatment_data(file_path, investment=5000, start_date='2023-10-13'):
    """
    read the 'Fund History.csv',
    then return a DataFrame of Date, NAV and real Value based on the investment.
    """
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Effective Date']).dt.strftime('%Y-%m-%d')
    df = df.loc[df['Date'] >= start_date, ['Date', 'NAV']]
    df = df.iloc[::-1].reset_index(drop=True)
    df['Value'] = [round(investment/12.9971 * i, 2) for i in df['NAV']]
    return df


def graph_drawer(df):
    """
    Feed the DataFrame to the pylot for graph.
    """

    fig = px.line(df, x='Date', y='Value', title='Value Over Time', hover_data={'NAV': ':.2f'})  # text='Value'
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Value')
    fig.update_xaxes(type='category')

    # 在折线上显示标记
    # fig.update_traces(textposition="top center")
    # fig.update_traces(textfont=dict(size=16))

    # 旋转 X 轴上的日期标签
    fig.update_xaxes(tickangle=45)

    # 显示网格线
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='gray')
    # fig.write_html('interactive_chart.html')
    fig.show()


file = os.path.join("C:\\Users\\small\\Downloads", 'Fund History.csv')
if os.path.isfile(file):  # if there is a "Fund History.csv", remove it for the new one.
    os.remove(file)
table_downloader()
dataframe = pretreatment_data(file)
graph_drawer(dataframe)
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
