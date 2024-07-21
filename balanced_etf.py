import time
import pandas as pd
import plotly.express as px
import os
import webbrowser
from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
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


def pretreatment_data(file_path, start_date='2023-10-13'):
    """
    read the 'Fund History.csv', set Date as index, extract only the data after start_date,
    convert RP from str to float, then return a DataFrame of Date, NAV and real Value based on the investment.
    """
    start_date = pd.to_datetime(start_date).date()
    df = pd.read_csv(file_path, index_col='Effective Date', parse_dates=True)
    df.index = df.index.date
    df.sort_index(inplace=True)
    df['RP'] = pd.to_numeric(df['Reinvestment Price'], errors='coerce')
    df = df.loc[df.index >= start_date, ['NAV', 'RP']]
    return df


def get_new_shares(df_, current_shares, trade_day):
    """
    Calculate new shares: new shares = current shares * previous day NAV / Reinvestment Price of trade day
    """
    previous_day = trade_day - pd.Timedelta(days=1)
    return current_shares * df_.loc[previous_day, 'NAV'].item() / df_.loc[trade_day, 'RP'].item()


def value_calcul(df, investment=5000):
    """
    Calculate the value from the start date to the latest day.
    """
    initial_shares = investment / 12.9971
    df['shares'] = float('NaN')
    df.loc[df.index[0], 'shares'] = initial_shares

    # maybe many trade days during several years
    trade_day_index_group = df.index[df['RP'].notnull()]

    # one trade day, one new shares
    cur_shares = initial_shares
    new_shares_group = []
    for tdi in trade_day_index_group:
        new_shares_group.append(get_new_shares(df, cur_shares, tdi))
        cur_shares = new_shares_group[-1]

    # refill the new shares at the trade days
    for day, shares in zip(trade_day_index_group, new_shares_group):
        df.loc[day, 'shares'] = shares

    # refill respectively the new shares to the days after trade days
    df['shares'] = df['shares'].ffill()

    # calculate the values
    df['Value'] = round(df['NAV'] * df['shares'], 2)
    return df


def new_graph_drawer(df_):
    """
    Feed the DataFrame to the pyecharts for graph.
    """
    makepoint_data = [
                           opts.MarkPointItem(coord=[df_.index.to_list()[-1], df_['Value'].to_list()[-1]],
                                              value=df_['Value'].to_list()[-1],
                                              symbol_size=80)
                       ]
    if df_['Value'].to_list()[-1] != float(df_['Value'].max()):
        makepoint_data.append(opts.MarkPointItem(type_="max", name="max", symbol_size=80))

    line = Line(init_opts=opts.InitOpts(width='1800px', height='900px'))
    line.add_xaxis(df_.index.to_list())
    line.add_yaxis('Value',
                   df_['Value'].to_list(),
                   label_opts=opts.LabelOpts(is_show=False),
                   tooltip_opts=opts.TooltipOpts(trigger_on='mousemove|click', is_show=True,
                                                 axis_pointer_type='cross',
                                                 formatter=JsCode(
                                                     """
                                                     function(params) {
                                                        var z = """ + str(df_['NAV'].to_list()) + """;
                                                        var index = params.dataIndex;
                                                        return 
                                                            'Date: ' + params.data[0] + 
                                                            '<br>Value: ' + params.data[1] + 
                                                            '<br>NAV: ' + z[index]
                                                     }
                                                     """
                                                 )),
                   markpoint_opts=opts.MarkPointOpts(
                       data=makepoint_data
                   ),
                   )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title='Balanced ETF'),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type='cross'),
        yaxis_opts=opts.AxisOpts(min_=df_['Value'].min() // 100 * 100)
    )
    line.render()


def graph_drawer(df_):
    """
    Feed the DataFrame to the pylot for graph.
    """

    fig = px.line(df_, x='Date', y='Value', title='Value Over Time', hover_data={'NAV': ':.2f'})  # text='Value'
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Value')
    fig.update_xaxes(type='category')

    # 旋转 X 轴上的日期标签
    fig.update_xaxes(tickangle=45)

    # 显示网格线
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='gray')
    # fig.write_html('interactive_chart.html')
    fig.show()


if __name__ == "__main__":
    file = os.path.join("C:\\Users\\small\\Downloads", 'Fund History.csv')
    if os.path.isfile(file):  # if there is a "Fund History.csv", remove it and wait for the new one.
        os.remove(file)
    table_downloader()
    df = value_calcul(pretreatment_data(file))
    new_graph_drawer(df)
    # graph_drawer(df)
    webbrowser.open('render.html')
    os.remove(file)
