from utils.detect import detect
from PyQt5.QtWidgets import QApplication, QMessageBox,QGridLayout
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.uic as uic
import cv2 as cv
import datetime
import matplotlib as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

plt.use('Qt5Agg')

ages = {'(0-2)':0,'(4-6)':0,'(8-12)':0,'(15-20)':0,'(25-32)':0,'(38-43)':0,'(48-53)':0,'(60-100)':0}
gender = {'Child':0,'Male':0,'Female':0}
expression = {'angry':0,'disgust':0,'fear':0, 'happy':0,'sad':0, 'surprise':0, 'neutral':0}


class SI:
    MainWin = None
    LoginWin = None

url = "http://huatsing.pythonanywhere.com/api/mgr/event"


class MyFigureCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100,ages=ages,gender=gender,expression=expression):
        fig = Figure(figsize=(width, height), dpi=dpi)
        
        self.age = fig.add_subplot(1,3,1)
        self.gender = fig.add_subplot(1,3,2)
        self.expression = fig.add_subplot(1,3,3)

        self.compute_initial_figure(ages,gender,expression)
        fig.subplots_adjust(bottom=0.15)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self,ages,gender,expression):
        ages_labels = list(ages.keys())
        ages_nums = list(ages.values())

        gender_labels = list(gender.keys())
        gender_nums = list(gender.values())

        expression_labels = list(expression.keys())
        expression_nums = list(expression.values())

        self.age.bar(ages_labels, ages_nums)
        self.age.set_title("age")
        self.age.set_xticks(ages_labels)
        self.age.set_xticklabels(labels = ages_labels,rotation=-45)
        self.gender.pie(gender_nums, labels=gender_labels, autopct='%1.1f%%',shadow=True, startangle=90)
        self.gender.axis('equal') 
        self.gender.set_title("gender")
        self.expression.bar(expression_labels, expression_nums)
        self.expression.set_title("expression")
        self.expression.set_xticks(expression_labels)
        self.expression.set_xticklabels(labels = expression_labels,rotation=-45)



class Sub_Model:

    def __init__(self,Session,Username):
        # super(Sub_Model, self).__init__()
        self.ui = uic.loadUi('qtsource/sub_model.ui')
        #RUN OR STOP
        self.power = False
        # 对应属性开关
        self.experssion_Flag = False
        self.age_Flag = False
        self.gender_Flag = False
        self.Upload = False
        # 定时器，为了与opcncv适配
        self._timer = QtCore.QTimer(self.ui)
        self._timer.timeout.connect(self.add_to_Camera)
        self._timesnum = 0
        self.idx =  ('nvarguscamerasrc ! '
               'video/x-raw(memory:NVMM), '
               'width=(int)2592, height=(int)1458, '
               'format=(string)NV12, framerate=(fraction)30/1 ! '
               'nvvidconv flip-method=2 ! '
               'video/x-raw, width=(int)540, height=(int)530, '
               'format=(string)BGRx ! '
               'videoconvert ! appsink')
        self.username = Username
        self.session = Session

        # 相应按键与函数绑定
        self.ui.pub_rs.clicked.connect(self.on_Run_Stop_clicked)
        self.ui.pub_cleartext.clicked.connect(self.on_ClearText_clicked)

        self.ui.check_age.stateChanged.connect(self.on_Attribute_clicked)
        self.ui.check_facial.stateChanged.connect(self.on_Attribute_clicked)
        self.ui.check_gender.stateChanged.connect(self.on_Attribute_clicked)
        self.ui.check_upload.stateChanged.connect(self.on_Attribute_clicked)


    # 摄像函数（外加检测)
    def add_to_Camera(self):
        #读取帧数
        hasFrame, frame = self.cap.read()
        if not hasFrame:
            self.ui.textBrowser.append("检测结束")
            #摄像关闭、定时器停止
            self.cap.release()
            self._timer.stop()
            self.power = not self.power
            self._timesnum = 0
        else:
            
            #frame = cv.flip(frame, 1)


            frame,label = detect(frame,self.experssion_Flag,self.age_Flag,self.gender_Flag)

            # 这是一帧内的标签，应该全部显示，而不同帧的标签，尽量隔一段时间
            if(self._timesnum == 0):
                for i in label:
                    # 数据库的增操作
                    self.ui.textBrowser.append(i)
                    gender,age,expression = i.split(' ')
                    if(self.Upload):
                        time = datetime.datetime.now()
                        time = time.strftime('%Y-%m-%d %H:%M:%S')
                        payload = {
                            'action': 'add_event',
                            "data":{
                                "time":time,
                                "username":self.username,
                                "age":age,
                                "expression":expression,
                                "gender":gender
                                }
                            }
                        res = self.session.post(url,json = payload)
                        resObj = res.json()
                        if resObj['ret'] != 0:
                            QMessageBox.warning(self.ui,'添加数据失败',resObj['msg'])
                            return
                    

            img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img = cv.resize(img,(528,528))
            x = img.shape[1]
            y = img.shape[0]
            frame = QtGui.QImage(img, x, y, x*3,QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(frame)
            self.item = QtWidgets.QGraphicsPixmapItem(pix) # 创建像素图元
            self.scene = QtWidgets.QGraphicsScene() # 创建场景
            self.scene.addItem(self.item)
            self.ui.Graphic_main.setScene(self.scene) # 将场景添加至视图
            self._timesnum +=1
            if(self._timesnum == 10):
                self._timesnum = 0

    # 只显示图片/可理解为只显示单张图片 不做处理、可用于显示开机界面
    def add_to_pic(self,frame):
        img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img = cv.resize(img,(528,528))
        x = img.shape[1]
        y = img.shape[0]
        frame = QtGui.QImage(img, x, y, x*3,QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(frame)
        self.item = QtWidgets.QGraphicsPixmapItem(pix)
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addItem(self.item)
        self.ui.Graphic_main.setScene(self.scene)

    def on_Run_Stop_clicked(self):
        self.power = not self.power

        if self.power:
            self.cap = cv.VideoCapture(self.idx)
            self._timer.start(15)
            self.ui.textBrowser.append("检测开始")
        else:
            self.cap.release()
            self._timer.stop()
            self._timesnum = 0
            self.ui.textBrowser.append("检测结束")
            
    def on_ClearText_clicked(self):
        self.ui.textBrowser.clear()


    def on_Attribute_clicked(self):
        self.experssion_Flag = self.ui.check_facial.checkState()
        self.age_Flag = self.ui.check_age.checkState()
        self.gender_Flag = self.ui.check_gender.checkState()
        self.Upload = self.ui.check_upload.checkState()


class Sub_Config:
    def __init__(self,Session):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("qtsource/sub_config.ui")
        self.ui.table_config.setColumnWidth(0, 400)
        self.ui.table_config.setColumnWidth(1, 400)

        self.ui.table_config.horizontalHeader().setStretchLastSection(True)


    def onSignIn(self):
        pass

class Sub_Visual:
    def __init__(self,Session,Username):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("qtsource/sub_visual.ui")
        self.username = Username
        self.session = Session
        
        

        self.ui.dateTime_start.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.ui.dateTime_start.setDateTime(datetime.datetime(2020, 4, 6, 21, 21, 20))
        self.ui.dateTime_end.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.ui.dateTime_end.setDateTime(QtCore.QDateTime.currentDateTime())
        self.ui.dateTime_start.setCalendarPopup(True)
        self.ui.dateTime_end.setCalendarPopup(True)

        self.ui.pub_find.clicked.connect(self.Find_visual)

        self.layout = QGridLayout()  # 创建网格布局的对象
        self.ui.mainwidget.setLayout(self.layout)
        # self.layout.addWidget(mc,0,0,1,1)


    # 数据库的过滤操作 （username与datetime) 选择pagesize
    def Find_visual(self):
        ages = {'(0-2)':0,'(4-6)':0,'(8-12)':0,'(15-20)':0,'(25-32)':0,'(38-43)':0,'(48-53)':0,'(60-100)':0}
        gender = {'Child':0,'Male':0,'Female':0}
        expression = {'angry':0,'disgust':0,'fear':0, 'happy':0,'sad':0, 'surprise':0, 'neutral':0}
        tstart = self.ui.dateTime_start.dateTime()
        tend = self.ui.dateTime_end.dateTime()
        string = tstart.toString('yyyy-MM-dd HH:mm:ss')+'#'+tend.toString('yyyy-MM-dd HH:mm:ss')+'#'+self.username

        payload = {
            'action': 'list_event',
            'pagenum': 0,
            'keywords':string
            }
        res = self.session.get(url,params=payload)
        resObj = res.json()

        if resObj['ret'] != 0:
            QMessageBox.warning(self.ui,'查找数据失败',resObj['msg'])
            return
        pagesize = len(resObj['retlist'])

        for i in range(0,pagesize):
            if(resObj['retlist'][i]['gender']!=''):
                gender[resObj['retlist'][i]['gender']] +=1
            if(resObj['retlist'][i]['age']!=''):
                ages[resObj['retlist'][i]['age']] +=1
            if(resObj['retlist'][i]['expression']!=''):
                expression[resObj['retlist'][i]['expression']] +=1
        mc = MyFigureCanvas(self.ui.mainwidget, width=5, height=3, dpi=100,ages=ages,gender=gender,expression=expression)
        mc.resize(self.ui.mainwidget.width(),self.ui.mainwidget.height())


        self.layout.addWidget(mc,0,0)


class Sub_Digit:
    def __init__(self,Session,Username):
        self.session = Session
        self.username = Username
        self.index = 1
        self.total = 0
        # 从文件中加载UI定义
        self.ui = uic.loadUi("qtsource/sub_datatable.ui")
        self.ui.dateTime_start.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.ui.dateTime_start.setDateTime(datetime.datetime(2020, 4, 6, 21, 21, 20))
        self.ui.dateTime_end.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.ui.dateTime_end.setDateTime(QtCore.QDateTime.currentDateTime())
        self.ui.dateTime_start.setCalendarPopup(True)
        self.ui.dateTime_end.setCalendarPopup(True)

        self.ui.table_data.setRowCount(25)
        self.ui.table_data.setColumnWidth(0, 180)
        self.ui.table_data.setColumnWidth(1, 180)
        self.ui.table_data.setColumnWidth(2, 180)
        self.ui.table_data.setColumnWidth(3, 180)
        self.ui.table_data.horizontalHeader().setStretchLastSection(True)


        self.ui.pub_find.clicked.connect(lambda:self.Find_DigitTable(index = self.index))
        self.ui.pub_prior.clicked.connect(self.Priorpage)
        self.ui.pub_next.clicked.connect(self.Nextpage)
        self.ui.progressBar.setValue(self.index)
        # self.ui.progressBar.setMinimum(self.index)


    # 数据库的过滤操作 （username与datetime) 固定pagesize pagenum
    def Find_DigitTable(self,index):
        self.ui.table_data.clearContents()

        tstart = self.ui.dateTime_start.dateTime()
        tend = self.ui.dateTime_end.dateTime()
        string = tstart.toString('yyyy-MM-dd HH:mm:ss')+'#'+tend.toString('yyyy-MM-dd HH:mm:ss')+'#'+self.username

        payload = {
            'action': 'list_event',
            'pagenum': index,
            'pagesize' : 25,
            'keywords':string
            }
        res = self.session.get(url,params=payload)
        resObj = res.json()

        if resObj['ret'] != 0:
            QMessageBox.warning(self.ui,'查找数据失败',resObj['msg'])
            return
        self.ui.progressBar.setValue(index)
        #总页数
        self.total = int(resObj['total']/25)+1
        self.ui.progressBar.setMaximum(self.total)


       
        pagesize = len(resObj['retlist'])

        for i in range(0,pagesize):
            self.ui.table_data.setItem(i,0, QtWidgets.QTableWidgetItem(resObj['retlist'][i]['time']))
            self.ui.table_data.setItem(i,1, QtWidgets.QTableWidgetItem(resObj['retlist'][i]['gender']))
            self.ui.table_data.setItem(i,2, QtWidgets.QTableWidgetItem(resObj['retlist'][i]['age']))
            self.ui.table_data.setItem(i,3, QtWidgets.QTableWidgetItem(resObj['retlist'][i]['expression']))

    def Nextpage(self):
        if self.index != self.total:
            self.index +=1

            self.Find_DigitTable(self.index)
        else:
            QMessageBox.warning(self.ui,'已是最终页',"已经是最终页了！")

    def Priorpage(self):
        if self.index != 1:
            self.index -=1
            self.Find_DigitTable(self.index)
        else:
            QMessageBox.warning(self.ui,'已是第一页',"已经是第一页了！")




        


        # qtime = self.ui.dateTime_start.time()




if __name__ == "__main__":
    app = QApplication([])

    desktop = cv.imread('images/login_desktop.png')
    new = Sub_Model()
    new.add_to_pic(desktop)
    new.ui.show()
    app.exec_()
