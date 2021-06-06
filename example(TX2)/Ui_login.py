import cv2 as cv
from PyQt5.QtWidgets import QApplication, QMessageBox,QGridLayout,QFileDialog
import PyQt5.uic as uic

from share import SI,Sub_Model,Sub_Config,Sub_Digit,Sub_Visual
import  requests

Session = requests.Session()

class Win_Login:

    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("qtsource/Win_Login.ui")
        self.ui.pub_login.clicked.connect(self.onSignIn)
        
        self.ui.edit_password.returnPressed.connect(self.onSignIn)

    def onSignIn(self):
        username = self.ui.edit_username.text().strip()
        password = self.ui.edit_password.text().strip()
        payload = {
        'username': username,
        'password': password
        }

        url = "http://huatsing.pythonanywhere.com/api/mgr/signin"
        res = Session.post(url,data=payload)

        resObj = res.json()
        if resObj['ret'] != 0:
            QMessageBox.warning(
                self.ui,
                '登录失败',
                resObj['msg'])
            return


        SI.MainWin = Win_Main(Session = Session,Username = username)
        SI.MainWin.ui.show()
        self.ui.edit_password.setText('')
        self.ui.hide()

class Win_Main:
    def __init__(self,Session,Username):
        # 从文件中加载UI定义
        # self.ui代表着主界面
        self.session = Session
        self.ui = uic.loadUi("qtsource/Main_w.ui")
        self.ui.setFixedSize(self.ui.width(),self.ui.height())
        # self.ui.setFixedSize(800,480)
        # 对主窗口进行布局
        self.main_layout = QGridLayout()  # 创建网格布局的对象
        self.ui.main_w.setLayout(self.main_layout)
        self.ui.setCentralWidget(self.ui.main_w)
        # 各子窗口的预先记录与布局
        self.ui.sub_model = Sub_Model(Session = Session,Username = Username)
        self.ui.sub_model.ui.textBrowser.append("欢迎登录:"+Username)
        self.ui.sub_datatable = Sub_Digit(Session = Session,Username = Username)
        self.ui.sub_visual = Sub_Visual(Session = Session,Username = Username)
        self.ui.sub_config = Sub_Config(Session = Session)

        self.ui.sub_model.ui.resize(self.ui.main_w.width(),self.ui.main_w.height())
        self.ui.sub_datatable.ui.resize(self.ui.main_w.width(),self.ui.main_w.height())
        self.ui.sub_visual.ui.resize(self.ui.main_w.width(),self.ui.main_w.height())
        self.ui.sub_config.ui.resize(self.ui.main_w.width(),self.ui.main_w.height())

        self.main_layout.addWidget(self.ui.sub_model.ui, 0, 0)
        self.main_layout.addWidget(self.ui.sub_datatable.ui, 0, 0)
        self.main_layout.addWidget(self.ui.sub_visual.ui, 0, 0)
        self.main_layout.addWidget(self.ui.sub_config.ui, 0, 0)

        self.ui.sub_datatable.ui.table_data.resize(self.ui.sub_datatable.ui.width(),self.ui.sub_datatable.ui.height()-50)
        self.ui.sub_visual.ui.mainwidget.resize(self.ui.sub_visual.ui.width(),self.ui.sub_visual.ui.height()-50)
        # 隐藏当前不需要的
        self.ui.sub_datatable.ui.hide()
        self.ui.sub_visual.ui.hide()
        self.ui.sub_config.ui.hide()
        desktop = cv.imread('images/login_desktop.png')
        self.ui.sub_model.add_to_pic(desktop)
        self.ui.sub_model.ui.show()
        # 行为与函数绑定
        self.ui.action_visual.triggered.connect(self.onVisual)
        self.ui.action_realtime.triggered.connect(self.onRealtime)
        self.ui.action_digit.triggered.connect(self.onDigit)
        self.ui.action_config.triggered.connect(self.onConfig)
        self.ui.action_Exit.triggered.connect(self.onSignOut)
        self.ui.action_offline.triggered.connect(self.onOffline)

    def onSignOut(self):
        url = "http://huatsing.pythonanywhere.com/api/mgr/signout"
        res = self.session.post(url)

        resObj = res.json()
        if resObj['ret'] != 0:
            QMessageBox.warning(
                self.ui,
                '退出失败',
                resObj['msg'])
            return
        self.ui.hide()
        SI.LoginWin.ui.show()

    def onVisual(self):
        self.ui.sub_config.ui.hide()
        self.ui.sub_datatable.ui.hide()
        self.ui.sub_visual.ui.show()
        self.ui.sub_model.ui.hide()

    def onModel(self):
        self.ui.sub_config.ui.hide()
        self.ui.sub_datatable.ui.hide()
        self.ui.sub_visual.ui.hide()
        self.ui.sub_model.ui.show()

    def onDigit(self):
        self.ui.sub_config.ui.hide()
        self.ui.sub_datatable.ui.show()
        self.ui.sub_visual.ui.hide()
        self.ui.sub_model.ui.hide()

    def onConfig(self):
        self.ui.sub_datatable.ui.hide()
        self.ui.sub_visual.ui.hide()
        self.ui.sub_model.ui.hide()
        self.ui.sub_config.ui.show()

    def onOffline(self):
        filePath, _  = QFileDialog.getOpenFileName(
            self.ui,             # 父窗口对象
            "选择你要上传的图片/视频", # 标题
            r"images/",        # 起始目录
            "图片类型 (*.png *.jpg *.bmp *.mov)" # 选择类型过滤项，过滤内容在括号中
        )
        self.ui.sub_model.idx = filePath
        self.onModel()
    def onRealtime(self):
        self.ui.sub_model.idx = ('nvarguscamerasrc ! '
               'video/x-raw(memory:NVMM), '
               'width=(int)2592, height=(int)1458, '
               'format=(string)NV12, framerate=(fraction)30/1 ! '
               'nvvidconv flip-method=2 ! '
               'video/x-raw, width=(int)540, height=(int)530, '
               'format=(string)BGRx ! '
               'videoconvert ! appsink')
        self.onModel()




        
if __name__ == "__main__":
    app = QApplication([])
    SI.LoginWin = Win_Login()
    SI.LoginWin.ui.show()
    # new = Win_Main()
    # new.ui.show()
    app.exec_()
