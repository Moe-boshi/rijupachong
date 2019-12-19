'''
install csv,Pillow,tk,pyquery,requests
'''
import requests
import time
import os
import io
import csv
from tkinter import *
from pyquery import PyQuery as pq
from PIL import Image, ImageTk
from urllib.request import urlopen


# GUI界面
# 首页
class FirstGUI:
    def __init__(self, master):
        global url_input, text, chooseStr
        self.master = master
        # 设置窗口标题
        master.title('日剧TV爬虫（双击获取图像）')
        # 设置窗口位置大小
        center_window(master, 500, 250)
        # 固定一下
        master.maxsize(500, 250)
        master.minsize(500, 250)
        # 设置窗口图标
        # root.iconbitmap('spider.ico')
        self.text = Label(master, text='请输入需要下载的URL：')
        self.text.grid()
        name = StringVar()
        self.url_input = Entry(master, textvariable=name, width=45)
        self.url_input.grid(row=0, column=1)
        # 列表控件
        chooseStr = StringVar()
        self.text = Listbox(master, width=70, height=10, listvariable=chooseStr, selectmode=SINGLE)
        # columnspan 组件所跨越的列数
        self.text.grid(row=1, columnspan=2)
        # 解析按钮
        self.start = Button(master, text='开始解析', command=self.startTk)
        self.start.grid(row=2)
        # 导出按钮
        self.output = Button(master, text='导出CSV', command=self.outPut)
        self.output.grid(row=2, column=1)
        # 双击查看图片
        self.text.bind('<Double-Button-1>', self.lookI)

    # 双击查看图片
    def lookI(self, event):
        # 获取当前选中列表值
        n = re.findall(r'[(](.*?),[)]', str(self.text.curselection()))[0]
        # print(imgList)
        showImg(imgList[int(n)])

    # 开始解析网址
    def startTk(self):
        global imgList
        imgList = []
        url = self.url_input.get()
        print(url)
        # 清空listbox
        self.text.delete(0, END)
        if self.noUrl(url, '请先输入网址！') == 1:
            # 初始化为PyQuery对象
            html = get_html(url)
            doc = pq(html)
            # 获取图像
            imgListItems = doc('.quic').items()
            for img in imgListItems:
                imgList.append(img.attr('data-original'))
            # 获取标题
            Lists = doc('.ellipsis-1 a').items()
            # 向listbox中插入数据
            for title in Lists:
                # 插入listbox
                self.text.insert(END, title.text())
            self.task('获取成功！')

    # 导出CSV按钮
    def outPut(self):
        url = self.url_input.get()
        print(url)
        if self.noUrl(url, '请先输入网址！') == 1:
            # 初始化为PyQuery对象
            html = get_html(url)
            doc = pq(html)
            # 获取标题和网址
            Lists = doc('.ellipsis-1 a').items()
            n = 0
            csvList = []
            for item in Lists:
                n += 1
                outLists = [n]
                postTitle = item.text()
                outLists.append(postTitle)
                postUrl = 'https://www.rijutv.com' + item.attr('href')
                # print(postUrl)
                oneList = self.getDetail(postUrl, outLists)
                csvList.append(oneList)
                print(str(n) + '输入' + postTitle)
            self.write_csv(csvList)

    # 获取剧集信息+剧情简介+集数
    def getDetail(self, url, outLists):
        html = get_html(url)
        doc = pq(html)
        firstDetails = doc('.intro').items()
        secondDetails = doc('.item-desc-info').items()
        countDetails = doc('.juji-list li a').items()
        detail1 = ''
        detail2 = ''
        # 剧集信息
        for i in firstDetails:
            detail1 = i.text()
            # print(detail1)
        # 剧情简介
        for i in secondDetails:
            detail2 = i.text()
            # print(detail2)
        # 组合
        outLists.append(url)
        outLists.append(detail1)
        outLists.append(detail2)
        # 集数
        for i in countDetails:
            outLists.append('https://www.rijutv.com' + i.attr('href'))
        return outLists

    # 写入csv文件处理方法
    def write_csv(self, lists):
        nowTime = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        mkdir('download')
        filename = 'download/' + str(nowTime) + '.csv'
        print('文件名：' + filename)
        # 不设置utf-8转换GBK会报错难搞
        with open(filename, 'a', encoding='utf-8', newline='') as f:
            k = csv.writer(f, dialect="excel")
            # 设置第一行
            firstRow = ['编号', '剧名', '网址', '编剧', '剧情简介']
            i = 0
            while i < 100:
                i += 1
                firstRow.append(i)
            k.writerow(firstRow)
            n = 0
            for row in lists:
                n += 1
                k.writerow(row)
                print('输出' + str(n))
            print('输出成功！位置：' + filename)
            self.task('输出成功！当前位置：' + filename, 500)

    # 没有网址弹窗
    def noUrl(self, text, log):
        if text == '':
            self.task(log)
            return 0
        return 1

    def task(self, log, width=200, height=25):
        tk1 = Tk()
        center_window(tk1, width, height)
        tk1.title('提示')
        self.label = Label(tk1, text=log)
        self.label.pack()
        tk1.mainloop()

    url = "https://img.yongjiu7.com/upload/vod/2019-03-03/15515853812.jpg"
    image_bytes = urlopen(url).read()

# 窗口居中
def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    # print(size)
    root.geometry(size)


# 确认文件夹
def mkdir(path):
    # 判断是否存在文件夹如果不存在则创建为文件夹
    folder = os.path.exists(path)
    if not folder:
        # makedirs 创建文件时如果路径不存在会创建这个路径
        os.makedirs(path)
        print('新建文件夹')
    else:
        print('文件夹已存在')


# 获取网页源码
def get_html(url):
    # 添加Header模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    # 请求访问网站
    response = requests.get(url, headers=headers)
    # 获取网页源码
    html = response.text
    # 返回网页源码
    return html


# 显示图片
def showImg(imgUrl):
    root = Toplevel()
    url = imgUrl
    image_bytes = urlopen(url).read()
    # 获取图片内部数据文件
    data_stream = io.BytesIO(image_bytes)
    # 作为PIL图像对象打开
    pil_image = Image.open(data_stream)
    # 可选显示图像信息
    # 获取图像的大小
    w, h = pil_image.size
    center_window(root, w, h)
    root.maxsize(w, h)
    root.minsize(w, h)
    # 拆分图像文件名
    fname = url.split('/')[-1]
    sf = "{} ({}x{})".format(fname, w, h)
    root.title(sf)
    # 将PIL图像对象转换为Tkinter图像对象
    tk_image = ImageTk.PhotoImage(pil_image)
    # 将图像放到一个Label小部件上
    label = Label(root, image=tk_image, bg='brown')
    label.pack(padx=5, pady=5)
    root.mainloop()


def main():
    # new一个tk对象root
    root = Tk()
    # 创建GUI界面
    my_gui = FirstGUI(root)
    # 进入消息循环
    root.mainloop()


# 主程序
main()

# 网址
# https://www.rijutv.com/riju/
# https://www.rijutv.com/v_all/list-catid-7-page-2.html
