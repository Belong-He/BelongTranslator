from Belong.FanYi import Youdao, Google, Baidu, Kekenet  ,Kingsoft
import ctypes
from tkinter import Tk,Button, Entry, Text, Label, StringVar, W, E, S, N,Toplevel
from tkinter.font import Font
from jyutping import get as jyutpingget
from Belong.SimplifiedTraditional import Simplified2Traditional, Traditional2Simplified
from pyperclip import paste, copy

from sys import exit

from Belong.FanYi import YoudaoSpeechLibrary
from time import sleep

from PIL.ImageGrab import grabclipboard
from aip import AipOcr

from Belong.playCantonese import play
from os import path, makedirs

import _thread
from keyboard import wait
from Belong.FileRename import rename

from json import loads,dumps
# from Belong.BaiduAip import VoiceBroadcast
from playsound import playsound#路径不能有中文

# 弹窗
class MyDialog(Toplevel):#配置文字识别码的窗口
    def __init__(self):
        super().__init__()
        self.title('文字识别码')
        self.geometry('380x100+380+635')
        self.minsize(380, 100)
        self.userinfo = []
        self.JsonPath = 'MyLibrary/Setting/Configuration.json'
        # 弹窗界面
        self.setup_UI()


    def setup_UI(self):
        with open(self.JsonPath, 'r+', encoding='utf-8')as file:
            # file.write()
            tJson=file.read()
            self.idd=loads(tJson)
            # print(idd)
            APP_ID = self.idd['APP_ID']
            API_KEY = self.idd['API_KEY']
            SECRET_KEY =self.idd['SECRET_KEY']

        # 第一行（两列）

        Label(self, text='APP_ID:', width=11).grid(row=0, column=0, sticky=(W, E))

        self.APP_ID = StringVar()
        Entry(self, textvariable=self.APP_ID, width=42).grid(row=0, column=1, sticky=(W, E))
        self.APP_ID.set(APP_ID)

        # 第二行

        Label(self, text='API_KEY:', width=11).grid(row=1, column=0, sticky=(W, E))
        self.API_KEY = StringVar()
        # Entry(row2, textvariable=self.API_KEY, width=20).pack(side=LEFT)
        Entry(self, textvariable=self.API_KEY, width=42).grid(row=1, column=1, sticky=(W, E))
        self.API_KEY.set(API_KEY)

        # 第三行

        Label(self, text='SECRET_KEY:', width=11).grid(row=2, column=0, sticky=(W, E))
        self.SECRET_KEY = StringVar()
        Entry(self, textvariable=self.SECRET_KEY, width=42).grid(row=2, column=1, sticky=(W, E))
        self.SECRET_KEY.set(SECRET_KEY)

        # 第四行

        Button(self, text="确定", command=self.ok).grid(row=3, column=0, sticky=(W,E))
        Button(self, text="取消", command=self.cancel).grid(row=3, column=1, sticky=(W,E))


    def ok(self,t=None):
        self.userinfo = [self.APP_ID.get(), self.API_KEY.get(),self.SECRET_KEY.get()]  # 设置数据
        self.idd['APP_ID']=self.userinfo[0]
        self.idd['API_KEY']=self.userinfo[1]
        self.idd['SECRET_KEY']=self.userinfo[2]
        with open(self.JsonPath, 'w', encoding='utf-8')as file:
            tJson = dumps(self.idd, indent=4, ensure_ascii=False)
            file.write(tJson)
            if self.userinfo[0] and self.userinfo[1] and self.userinfo[2]:
                self.client = AipOcr(self.userinfo[0],self.userinfo[1],self.userinfo[2])  # 登录客户端
        self.destroy()  # 销毁窗口

    def cancel(self):
        self.userinfo =[]  # 空！
        self.destroy()


# 主窗
class MyApp(Tk):
    def __init__(self):
        super().__init__()
        self.wm_attributes('-topmost', 1)  # 窗口最前置
        self.title('Belong Tools')
        self.geometry('380x166+0+635')
        self.minsize(380, 166)
        jjson = {
            "APP_ID": "",
            "API_KEY": "",
            "SECRET_KEY": ""
        }
        JsonPath='MyLibrary/Setting/Configuration.json'
        if not path.exists(JsonPath):
            makedirs('MyLibrary/Setting')
            with open(JsonPath, 'w', encoding='utf-8')as file:
                file.write(dumps(jjson))
        # 不合法字符配对块
        self.pattern = r',|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|\_|，|。|、|；|‘|’|【|】|·|！|…|（|）|\t|-'
        #先登录客户端
        try:
            with open(JsonPath, 'r+', encoding='utf-8')as file:
                # file.write()
                tJson=file.read()
                self.idd=loads(tJson)
                # print(idd)
                self.APP_ID = self.idd['APP_ID']
                self.API_KEY = self.idd['API_KEY']
                self.SECRET_KEY =self.idd['SECRET_KEY']
                if self.APP_ID and self.API_KEY and self.SECRET_KEY:
                    self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)  # 登录客户端
        except Exception as e:
            print(e)

        if not path.exists('MyLibrary'):
            makedirs('MyLibrary')
        if not path.exists('MyLibrary/Note/Kingsoft'):
            makedirs('MyLibrary/Note/Kingsoft')
        if not path.exists('MyLibrary/Note/Youdao'):
            makedirs('MyLibrary/Note/Youdao')
        if not path.exists('MyLibrary/Note/Baidu'):
            makedirs('MyLibrary/Note/Baidu')
        if not path.exists('MyLibrary/Note/Kekenet'):
            makedirs('MyLibrary/Note/Kekenet')
        if not path.exists('MyLibrary/Note/Google'):
            makedirs('MyLibrary/Note/Google')

        # 程序多线程
        self.setupUI()
        _thread.start_new_thread(self.playEN, ())
        _thread.start_new_thread(self.playUS, ())
        _thread.start_new_thread(self.IdentifyWrap, ())
        _thread.start_new_thread(self.Identify, ())
        _thread.start_new_thread(self.console, ())
        _thread.start_new_thread(self.show, ())
        self.hideConsole()

    def setupUI(self):
        self.result =StringVar()
        self.ft1 =Font(family='华文行楷', size=18)

        self.entry1 = Entry(self, fg='black', font=('GB2312', 18), bg='light green', width=30,
                            textvariable=self.result)
        self.entry1.grid(row=0, column=0, sticky=(W, E))
        self.entry1.focus()

        self.listb = Text(self, width=30, height=4, fg='black', font=('GB2312', 18))
        self.listb.grid(row=1, column=0, sticky=(W, E, S, N))

        self.Belong=Button(self, text='炳良翻译器', fg='purple', font=self.ft1, command=self.setup_config)
        self.Belong.grid(row=2, column=0, sticky=(W, E))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.bind('<Return>', self.kingsoft)
        self.bind('<Control-Return>', self.google)
        self.bind('<F1>', self.kingsoft)
        self.bind('<F2>', self.youdao)
        self.bind('<F3>', self.baidu)
        self.bind('<F4>', self.kekenet)
        self.bind('<F5>', self.google)
        # self.bind('<F8>', self.ContinuousReading)  # 连读
        self.bind('<F10>', self.help)
        self.bind('<F11>', self.simpletranditional)
        self.bind('<Escape>', exit)

    # 设置参数
    def setup_config(self):
        # 接收弹窗的数据
        res = self.ask_userinfo()
        # print(res)
        if res is None: return

    # 弹窗
    def ask_userinfo(self):
        inputDialog = MyDialog()
        self.wait_window(inputDialog)  # 这一句很重要！！！

        return inputDialog.userinfo

    def SetStr(self,str):
        self.result.set(str)

    def ListBar(self,translation):
        self.listb.delete(1.0, "end")
        self.listb.insert("insert", translation)

    def GetStr(self):
        entrywords = self.entry1.get()
        entrywords = rename(entrywords)[0].strip()
        return entrywords

    """翻译"""

    def note(self, where, word, explain):
        if word:
            with open('MyLibrary/Note/' + where + '/' + word + '.txt', 'w', encoding='utf-8')as file:
                file.write(explain)
                file.write('\n')
            return 1
        else:
            return 0

    def translate(self, entrywords, where):
        if where == 'Kingsoft':
            translation = Kingsoft.trans(entrywords)
        elif where == 'Youdao':
            translation = Youdao.trans(entrywords)
        elif where == 'Baidu':
            translation = Baidu.trans(entrywords)
        elif where == 'Kekenet':
            translation = Kekenet.trans(entrywords)
        elif where == 'Google':
            translation = Google.minitrans(entrywords)
        return translation

    def ShowExplain(self, where):
        entrywords = self.GetStr()
        entrywords = rename(entrywords)[0].strip()
        if entrywords:
            if path.exists('MyLibrary/Note/' + where + '/' + entrywords + '.txt'):
                with open('MyLibrary/Note/' + where + '/' + entrywords + '.txt', 'r', encoding='utf-8')as file:
                    translation = file.read()
                self.ListBar(translation)
                print(where + ':  ' + entrywords + '.txt' + ':  已处在')
                return 0
            else:
                translation = self.translate(entrywords, where)
                self.ListBar(translation)
                self.note(where, entrywords, translation)
        else:
            clipwords = paste()
            self.SetStr(clipwords)
            translation = self.translate(clipwords, where)
            self.ListBar(translation)
            self.note(where, entrywords, translation)

    """ F1 """
    def kingsoft(self, t=None):#金山
        where = 'Kingsoft'
        try:
            self.ShowExplain(where)
        except Exception as e:
            print(e)
            self.youdao()


    """ F2 """

    def youdao(self, t=None):  # 有道
        where = 'Youdao'
        try:
            self.ShowExplain(where)
        except Exception as e:
            print(e)
            self.baidu()

    """ F3 """

    def baidu(self, t=None):  # 百度
        where = 'Baidu'
        try:
            self.ShowExplain(where)
        except Exception as e:
            print(e)
            self.kekenet()

    """ F4 """

    def kekenet(self, t=None):  # 可可英语
        where = 'Kekenet'
        try:
            self.ShowExplain(where)
        except Exception as e:
            print(e)
            self.google()

    """ F5 """

    def google(self, t=None):  # 谷歌
        where = 'Google'
        try:
            self.ShowExplain(where)
        except Exception as e:
            print(e)
            self.ListBar('全部翻译都用不了了，自求多福吧！')

    """ F6"""

    def playEN(self, t=None):
        while 1:
            wait(hotkey='f6')
            sleep(0.1)
            entrywords =self.GetStr()
            try:
                YoudaoSpeechLibrary.PlayENSound(entrywords.strip())
            except Exception as e:
                print(e)

    """ F7 """

    def playUS(self, t=None):
        while 1:
            wait(hotkey='f7')
            sleep(0.1)
            entrywords = self.GetStr()
            try:
                YoudaoSpeechLibrary.PlayUSSound(entrywords.strip())
            except Exception as e:
                print(e)

    """ F8 """

    """ F9 """


    """F10"""
    def help(self, t=None):
        sentence = '翻译的内容保存在本地，便于下次查询时能快一点点调用\nF1金山词霸，F2有道翻译\nF3百度翻译，F4可可英语\nF5谷歌翻译\nF6有道英式发音(连读)，中文男音\nF7有道美式发音(连读)，中文女音\nF10使用说明\nF11简繁体转换' \
                   '\nAlt+Q文字识别不换行\nAlt+R文字识别换行\nAlt+C显示隐藏Console(调试黑框)'
        self.ListBar(sentence)
    """ F11 """
    def playcantonese(self):
        self.words = self.GetStr()
        CantonesePathMP3='MyLibrary/Cantonese library/'
        try:
            if path.exists(CantonesePathMP3+'.mp3'):
                playsound(CantonesePathMP3+'.mp3')
                return True
            if path.exists(CantonesePathMP3 + '.wav'):
                playsound(CantonesePathMP3+'.wav')
                return True
            YoudaoSpeechLibrary.PlayCantonese(self.words,  output =CantonesePathMP3)
        except Exception as e:
            print(e)
    def simpletranditional(self,t=None):
        self.words = self.GetStr()
        if len(self.words) == 1:
            play(self.words)
        else:
            _thread.start_new_thread(self.playcantonese, ())
        Traditional = Simplified2Traditional(self.words)
        Simplified = Traditional2Simplified(self.words)
        try:
            pinyins = jyutpingget(self.words)
        except:
            pinyins = ''
        result = ''
        pinpinyin=''
        if isinstance(pinyins, list):
            for pinyin1 in pinyins:
                if isinstance(pinyin1, list):
                    pinpinyin += pinyin1[0]+' '
                    continue
                pinpinyin+=pinyin1+' '
            result += "简体：" + Simplified + '\n\n' + "繁体：" + Traditional + '\n' + pinpinyin+ '\n'
        else:
            result += "简体：" + Simplified + '\n\n' + "繁体：" + Traditional + '\n' + pinyins + '\n'
        self.ListBar(result.strip())

    """ F12 """

    def show(self, t=None):
        while True:
            wait(hotkey='f12')
            self.update()  # 更新
            self.deiconify()  # 显示
            self.entry1.focus()
            wait(hotkey='f12')
            self.withdraw()  # 隐藏

    """ 文字识别"""
    """ Alt+q / Alt+r"""

    def IdentifyClient(self, image):
        try:
            text = self.client.handwriting(image)  # 50/天
            print('手写识别50/天')
        except:
            text = self.client.basicAccurate(image)  # 500/天
            print('精准识别500/天')
        else:
            text = self.client.basicGeneral(image)  # 50000/天
            print('通用识别50000/天')
        return text

    def OpenImage(self):
        with open('MyLibrary\文字识别缓存图片.png', 'rb')as f:
            image = f.read()
            text = self.IdentifyClient(image)
            result = text['words_result']
            return result

    def chooseIdentifyClientPort(self, yesno):
        try:  # 换行
            result = self.OpenImage()
            #播放提醒
            try:
                playsound('MyLibrary\Setting\gaoding.mp3')
            except Exception as e:
                print(e)
            if yesno:#不换行
                self.NowrapData = ''
                for i in result:
                    self.NowrapData = self.NowrapData + i['words']
                # return self.NowrapData
            else:#换行
                self.WrapData = ''
                for i in result:
                    print(i['words'])
                    self.WrapData = self.WrapData + i['words'] + '\n'
                # return self.WrapData
        except:
            return False

    """文字识别不换行"""

    def Identify(self, t=None):
        while 1:
            wait(hotkey='alt+q')
            sleep(0.1)
            try:
                image = grabclipboard()
                image.save('MyLibrary\文字识别缓存图片.png')
            except:
                print('剪切板没图片，使用已保存图片识别')
            try:
                self.chooseIdentifyClientPort(True)
                copy(self.NowrapData.rstrip())
            except:
                continue

    """文字识别换行"""

    def IdentifyWrap(self, t=None):
        while 1:
            wait(hotkey='alt+r')
            sleep(0.1)
            try:
                image = grabclipboard()
                image.save('MyLibrary\文字识别缓存图片.png')
            except:
                print('剪切板没图片，使用已保存图片识别')
            try:
                self.chooseIdentifyClientPort(False)
                copy(self.WrapData.rstrip())
            except:
                continue

    """Console显示隐藏"""
    """Alt+c"""
    def hideConsole(self):
        """
        在GUI模式下隐藏控制台窗口。
        """

        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            # if you wanted to close the handles...
            # ctypes.windll.kernel32.CloseHandle(whnd)

    def showConsole(self):
        """取消隐藏控制台窗口"""
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 1)


    def console(self):
        while True:
            wait(hotkey='alt+c')
            self.showConsole()
            wait(hotkey='alt+c')
            self.hideConsole()


if __name__ == '__main__':
    app = MyApp()
    app.mainloop()