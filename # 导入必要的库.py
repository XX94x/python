# 导入必要的库
from ttkthemes import ThemedTk
import tkinter as tk
from tkinter import ttk
from dataclasses import replace
import requests
import re
from bs4 import BeautifulSoup
from tkinter.messagebox import showinfo 
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime  

time = int(6000)  # 刷新间隔时间（毫秒）
update_timer_id = None  # 定时器ID，用于取消定时任务

# 获取网页HTML内容
def getHTMLText(url):
    try:
        kv = {"User-Agent": 'Mozilla/5.0'}  # 设置请求头，模拟浏览器访问
        r = requests.get(url, timeout=30, headers=kv)  # 发送HTTP请求
        r.raise_for_status()  # 如果状态码不是200，抛出异常
        r.encoding = r.apparent_encoding  # 设置正确的编码
        return r.text  # 返回HTML内容
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return ""

# 解析HTML内容并提取所需信息
def filehtml(html):
    soup = BeautifulSoup(html, "lxml")  # 使用BeautifulSoup解析HTML
    item = str(soup.head.title.string)  # 获取网页标题
    item = item.replace('(崭新出厂)', '')  # 去除无关字符
    item = item.replace(' ', '')
    item = item.replace("|", '')
    item = item.replace("_CS2饰品交易_网易BUFF", '')
    item.split(" ")
    items = str(soup.body.find_all("div", class_="relative-goods"))  # 查找所有商品信息
    chinese_characters = re.findall(r'[\u4e00-\u9fff]+', items)  # 提取中文字符（商品类型）
    data_prices = re.findall(r'data-price="(.*?)"', items)  # 提取价格信息
    return item, chinese_characters, data_prices

# 显示数据
def printdate(item, chinese_characters, data_prices):
    dic = {}
    for i in range(len(chinese_characters)):
        dic[chinese_characters[i]] = data_prices[i]  # 将商品类型与价格对应
    aLabel.config(text=str(item) + str(dic))  # 更新显示标签内容
    root.after(time, lambda: printdate(item, chinese_characters, data_prices))  # 定时刷新数据

# 保存数据到CSV文件
def keepdata(item, chinese_characters, data_prices):
    now = datetime.now()  # 获取当前时间
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间
    with open(f"{item}.csv", "a") as f:  # 打开CSV文件
        f.write(item + "\n" + "时间" + "," + formatted_date + "\n")  # 写入时间
        for i in range(len(chinese_characters)):
            data_prices[i] = data_prices[i].replace(r'data-price="', "")
            f.write("类型" + "," + chinese_characters[i] + "," + data_prices[i] + "," + "元" + "\n")  # 写入商品类型和价格

# 绘制数据图表
def huizhi(item, canvas):
    with open(item + '.csv', "r+") as cnmd:  # 打开CSV文件
        zxcc = []; lyms = []; jjsc = []; psbk = []; zhll = []; sj = []  # 初始化列表
        for i in cnmd:
            i = i.strip()
            i = i.split(',')
            if len(i) <= 1:
                continue
            if i[0] == '时间':
                sj.append(i[1])  # 提取时间
            if i[1] == '崭新出厂':
                zxcc.append(float(i[2]))  # 提取对应价格
            if i[1] == '略有磨损':
                lyms.append(float(i[2]))
            if i[1] == '久经沙场':
                jjsc.append(float(i[2]))
            if i[1] == '破损不堪':
                psbk.append(float(i[2]))
            if i[1] == '战痕累累':
                zhll.append(float(i[2]))

    fig = plt.figure(figsize=(16, 7))  # 创建绘图窗口
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体
    plt.xticks(rotation=30, ha='right')  # 设置X轴标签旋转角度
    plt.plot(sj, zxcc, label='崭新出厂')  # 绘制数据曲线
    plt.plot(sj, lyms, label='略有磨损')
    plt.plot(sj, jjsc, label='久经沙场')
    plt.plot(sj, psbk, label='破损不堪')
    plt.plot(sj, zhll, label='战痕累累')
    plt.legend()  # 显示图例

    canvas_tk = FigureCanvasTkAgg(fig, master=root)  # 将绘图窗口嵌入到Tkinter窗口中
    canvas_widget = canvas_tk.get_tk_widget()

    canvas.delete('all')  # 清空画布
    canvas.create_window((0, 0), window=canvas_widget, anchor='nw')  # 在画布上创建窗口显示图表

    root.update_idletasks()  # 更新界面

    if len(zxcc) > 1 and len(lyms) > 1 and len(jjsc) > 1 and len(psbk) > 1 and len(zhll) > 1:
        zxcc_change = zxcc[-1] - zxcc[-2]  # 计算价格变化
        lyms_change = lyms[-1] - lyms[-2]
        jjsc_change = jjsc[-1] - jjsc[-2]
        psbk_change = psbk[-1] - psbk[-2]
        zhll_change = zhll[-1] - zhll[-2]

        price_label.config(text="当前价格变化"+item+'\n'
                                f"崭新出厂: {zxcc_change}元\n"
                                f"略有磨损: {lyms_change}元\n"
                                f"久经沙场: {jjsc_change}元\n"
                                f"破损不堪: {psbk_change}元\n"
                                f"战痕累累: {zhll_change}元\n")  # 更新价格变化标签
    else:
        price_label.config(text="价格数据不足，无法计算变化")

# 获取数据并更新
def fetch_and_update(url, canvas):
    html = getHTMLText(url)  # 获取网页HTML内容
    if html:
        item, chinese_characters, data_prices = filehtml(html)  # 解析HTML并提取信息
        keepdata(item, chinese_characters, data_prices)  # 保存数据到CSV文件
        printdate(item, chinese_characters, data_prices)  # 显示数据
        huizhi(item, canvas)  # 绘制图表
        global update_timer_id
        update_timer_id = root.after(time, lambda: fetch_and_update(url, canvas))  # 定时刷新数据

# 开始定时更新数据
def start_updates(url, canvas):
    global update_timer_id
    if update_timer_id is not None:
        root.after_cancel(update_timer_id)  # 取消之前的定时任务
    fetch_and_update(url, canvas)  # 获取数据并更新

# 创建主窗口
root = ThemedTk(theme="breeze")
root.title("Buffgo")
root.geometry("1600x1200")

root.columnconfigure(0, weight=1)  # 设置列权重
root.rowconfigure(1, weight=1)  # 设置行权重

font_style = ("微软雅黑", 17)

style = ttk.Style()
style.configure("TButton", font=font_style)  # 设置按钮样式

# 创建界面元素
label1 = ttk.Label(root, text="欢迎使用Buffgo请在下方输入网址\n或点击按钮查询价格信息", font=font_style)
label1.place(x=0, y=0)
price_label = tk.Label(root, text="价格变化将显示在这里", font=("Helvetica", 12))
price_label.place(x=600, y=0)
button1 = ttk.Button(root, text="沙鹰印花集", style="TButton", command=lambda: start_updates("https://buff.163.com/goods/781660#tab=selling&page_num=1", canvas))
button1.place(x=0, y=70)
button2 = ttk.Button(root, text="A1印花集", style="TButton", command=lambda: start_updates("https://buff.163.com/goods/835780#tab=selling&page_num=1", canvas))
button2.place(x=200, y=70)
button3 = ttk.Button(root, text="usp印花集", style="TButton", command=lambda: start_updates("https://buff.163.com/goods/900565#tab=selling&page_num=1", canvas))
button3.place(x=400, y=70)
aLabel = tk.Label(width=170, font="宋体", bg="white", height=2)
aLabel.place(x=0, y=120)
entry = ttk.Entry(root, width=50, font=font_style)
entry.place(x=0, y=180)
button0 = ttk.Button(root, text="获取售价信息", style="TButton", command=lambda: start_updates(entry.get(), canvas))
button0.place(x=0, y=230)
canvas = tk.Canvas(root, width=400, height=400)
canvas.place(x=0, y=280)

root.mainloop()