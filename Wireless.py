import sys
import os
import requests
absolute=os.path.abspath('.')
path_dir=os.path.join(absolute,'plug')
os.add_dll_directory(path_dir)
import vlc
from PySide2.QtWidgets import QDirModel
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QFrame
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QGridLayout
from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QSlider
from PySide2.QtWidgets import QSplitter
from PySide2.QtWidgets import QAbstractItemView
from PySide2.QtWidgets import QTabWidget
from PySide2.QtWidgets import QTableWidgetItem
from PySide2.QtWidgets import QTextEdit
from PySide2.QtGui import QPixmap
from PySide2.QtGui import Qt,\
    QIcon,\
    QImage
from  PySide2.QtCore import QTimer
import pyqtgraph as pg
import pandas as pd
import numpy as np
import  json
import time
import  xlrd
import cv2
class GridWirless(QWidget):
    def __init__(self):
        super(GridWirless, self).__init__()
        self.setWindowTitle("巡检机器人业务")
        self.instance1 = vlc.Instance()
        self.mediaplayer1 = self.instance1.media_player_new()
        self.instance2 = vlc.Instance()
        self.mediaplayer2 = self.instance1.media_player_new()
        #self.display_1 = QWidget()
        #self.display_2=QWidget()
        #self.splitter = QSplitter(self.display_2)
        self.tab=QTabWidget()
        self.tab.setVisible(False)
        self.pw = pg.PlotWidget()
        self.tableWidget = QtWidgets.QTableWidget()
        self.layv = QVBoxLayout()
        self.layv.addWidget(self.tab)
        self.layv.addWidget(self.tableWidget)
        #self.display_1.setMinimumWidth(600)
        self.pw.setTitle("温度趋势",
                         color='008080',
                         size='12pt')
        self.pw.setLabel("left", "温度(摄氏度)")
        self.pw.setLabel("bottom", "时间")
        self.pw.setYRange(min=-10,  # 最小值
                          max=50)  # 最大值
        self.pw.showGrid(x=True, y=True)

        self.pw.setBackground('w')

        self.videoframe1 = QFrame()
        self.videoframe2 = QFrame()
        self.videoframe2.setMinimumHeight(300)
        self.videoframe1.setMinimumHeight(300)
        self.videoframe1.setStyleSheet('background:black')
        self.videoframe1.setFrameShape(QFrame.StyledPanel)
        self.videoframe1.setFrameShadow(QFrame.Sunken)
        self.videoframe2.setStyleSheet('background:black')
        self.videoframe2.setFrameShape(QFrame.StyledPanel)
        self.videoframe2.setFrameShadow(QFrame.Sunken)
        self.mediaplayer1.set_hwnd(self.videoframe1.winId())
        self.mediaplayer2.set_hwnd(self.videoframe2.winId())
        self.button_play = QPushButton(
            QIcon('Icon/Start.png'),
            '启动',
            self
        )
        self.button_pause = QPushButton(
            QIcon('Icon/Pause.png'),
            '暂停',
            self
        )
        self.button_release = QPushButton(
            QIcon('Icon/Stop.png'),
            '停止',
            self
        )
        self.button_add=QPushButton(
            QIcon('Icon/Add.png'),
            '',
            self
        )
        self.slider_1 = QSlider(Qt.Horizontal)  # 1
        self.slider_1.setRange(0, 100)  # 2
        self.slider_1.valueChanged.connect(lambda: self.set_valume(self.slider_1.value()))
        self.tableWidget.setGeometry(QtCore.QRect(0, 60, 813, 371))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.raise_()
        #self.tableWidget.setMinimumHeight(450)
        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(90, 20, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("打开数据")
        self.pushButton.clicked.connect(self.openfile)
        self.pushButton.clicked.connect(self.creat_table_show)
        self.pushButton.clicked.connect(self.temp_c)
        self.layout_displayV = QVBoxLayout()
        self.layout_displayH=QHBoxLayout()
        self.layout_h=QHBoxLayout()
        self.layout_h.addWidget(self.videoframe1)
        self.layout_h.addWidget(self.videoframe2)
        self.layout_displayV.addLayout(self.layout_h)
        self.layout_displayH.addWidget(self.button_add)
        self.layout_displayH.addWidget(self.button_play)
        self.layout_displayH.addWidget(self.button_pause)
        self.layout_displayH.addWidget(self.button_release)
        self.layout_displayH.addWidget(self.pushButton)
        self.layout_displayH.addWidget(self.slider_1)
        self.layout_displayV.addLayout(self.layout_displayH)
        self.layout_displayV.addLayout(self.layv)
        self.setLayout(self.layout_displayV)
        self.red_camera_url =''
        self.hd_camera_url =''
        self.loading_data()
        self.media1 = self.instance1.media_new(self.hd_camera_url)
        self.media2 = self.instance2.media_new(self.red_camera_url)
        self.mediaplayer1.set_media(self.media1)
        self.mediaplayer2.set_media(self.media2)
        self.button_add.clicked.connect(self.addevice)
        self.button_play.clicked.connect(self.start_camera)
        self.button_pause.clicked.connect(self.pause_camera)
        self.button_release.clicked.connect(self.stop1)
        self.button_play.clicked.connect(self.start_red_cam)
        self.button_pause.clicked.connect(self.pause_red_camera)
        self.button_release.clicked.connect(self.stop2)
    def loading_data(self):
        with open('robot_data.ini', 'r', encoding='utf-8') as file:
            data_json = file.read()
            data_urls = json.loads(data_json)
            self.red_camera_url=data_urls['red']
            self.hd_camera_url=data_urls['hd']
    def addevice(self):
        device_info=Addevice()
        if device_info.camera_hd_url=='' or device_info.red_camera_url=='':
            pass
        else:
            self.hd_camera_url=device_info.camera_hd_url
            self.red_camera_url=device_info.red_camera_url
            self.data_info=device_info.device_data_url
            self.data_recv(device_info.device_data_url)
    def data_recv(self,url_data):
        if not url_data=='':
            url = url_data
            try:
                r = requests.get(url)
                with open('检测数据.xlsx', 'wb') as file:
                    file.write(r.content)
            except:
                pass
        else:
            pass
    def start_camera(self):
        if not self.mediaplayer1.play():
            self.mediaplayer1.set_media(self.media1)
        print('data.device_camera')
        self.mediaplayer1.video_set_marquee_string(vlc.VideoMarqueeOption.Text,
                                                   '高清摄像头'
                                                   )
        self.mediaplayer1.play()
    def pause_camera(self):
        self.mediaplayer1.pause()
    def stop1(self):
        self.mediaplayer1.stop()
    def start_red_cam(self):
        if not self.mediaplayer2.play():
            self.mediaplayer2.set_media(self.media2)
        print('data.device_camera_red')
        self.mediaplayer2.play()
    def pause_red_camera(self):
        self.mediaplayer2.pause()
    def stop2(self):
        self.mediaplayer2.stop()
    def set_valume(self,value):
        self.mediaplayer1.audio_set_volume(value)
        self.mediaplayer2.audio_set_volume(value)
    def openfile(self):
        openfile_name = QFileDialog.getOpenFileName(self,
                                                    '选择文件',
                                                    '',
                                                    'Excel files(*.xlsx , *.xls)'
                                                    )
        global path_openfile_name
        path_openfile_name = openfile_name[0]
    def creat_table_show(self):
        if len(path_openfile_name) > 0:
            input_table = pd.read_excel(path_openfile_name)
            data= input_table.values.tolist()  # 获取所有的数据，注意这里不能用head()方法哦~
            print(data[1])
            print("获取到所有的值:\n{0}".format(data))  # 格式化输出
            input_table_rows = input_table.shape[0]
            input_table_colunms = input_table.shape[1]
            input_table_header = input_table.columns.values.tolist()
            self.tableWidget.setColumnCount(input_table_colunms)
            self.tableWidget.setRowCount(input_table_rows)
            self.tableWidget.setHorizontalHeaderLabels(input_table_header)
            for i in range(input_table_rows):
                input_table_rows_values = input_table.iloc[[i]]
                input_table_rows_values_array = np.array(input_table_rows_values)
                input_table_rows_values_list = input_table_rows_values_array.tolist()[0]
                for j in range(input_table_colunms):
                    input_table_items_list = input_table_rows_values_list[j]
                    input_table_items = str(input_table_items_list)
                    newItem = QTableWidgetItem(input_table_items)
                    newItem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                    self.tableWidget.setItem(i, j, newItem)
        else:
            self.show()
    def temp_c(self):
        workbook = xlrd.open_workbook(path_openfile_name)
        rows=workbook.sheet_by_name('温度').nrows
        for i in range(1,rows):
            y_hour=workbook.sheet_by_name('温度').row_values(0)[1:]
            temp = workbook.sheet_by_name('温度').row_values(i)
            pdd=pg.PlotWidget()
            pdd.setTitle("温度趋势",
                         color='008080',
                         size='12pt')
            pdd.setLabel("bottom", "时间")
            pdd.setLabel("left", "温度(摄氏度)")
            pdd.setLabel('top', '{}'.format(temp[0]))
            pdd.setYRange(min=-10,  # 最小值
                              max=50)  # 最大值
            pdd.showGrid(x=True, y=True)
            pdd.setBackground('w')
            self.hour = [
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10
            ]
            temperature = [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ]
            pdd.plot(y_hour,
                         temp[1:],
                         pen=pg.mkPen('g') # 线条颜色
                         )
            self.tab.addTab(pdd,
                            '{}'.format(temp[0])
                            )




class dialog(QDialog):
    def __init__(self):
        super(dialog, self).__init__()
        self.setWindowTitle('请添加设备')
        self.resize(200, 140)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.name1 = QLabel(self)
        self.name1.setText('请输入设备名称：')
        self.name = QLineEdit(self)
        self.url = QLabel(self)
        self.url.setText('请输入url：')
        self.ip = QLineEdit(self)
        self.buttok = QPushButton('确认', self)
        self.buttcancel = QPushButton('取消', self)
        self.hlayout = QHBoxLayout()
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.name1)
        self.vlayout.addWidget(self.name)
        self.vlayout.addWidget(self.url)
        self.vlayout.addWidget(self.ip)
        self.hlayout.addWidget(self.buttok)
        self.hlayout.addWidget(self.buttcancel)
        self.grid1 = QGridLayout()
        self.grid1.addLayout(self.vlayout, 0, 0)
        self.grid1.addLayout(self.hlayout, 1, 0)
        self.setLayout(self.grid1)
        self.buttok.clicked.connect(self.get_data)
        self.buttcancel.clicked.connect(self.reject)
        self.setStyleSheet('PushButton{background:blue;'
                           'border-radius:7px solid orange}')
        self.show()
        self.exec_()
    def get_data(self):
        if self.name.text() == '' or self.ip.text() == '':
            QMessageBox.information(
                self,
                '提示',
                '输入不能为空！'
            )
        else:
            self.accept()
            return self.name.text() ,self.ip.text()


class xlsxtab(QWidget):
    def __init__(self):
        super(xlsxtab, self).__init__()
        self.resize(600, 600)
        self.model_xlsx =QDirModel(self)
        self.model_xlsx.setReadOnly(False)
        self.model_xlsx.setSorting(QDir.Name | QDir.IgnoreCase)
        self.tree_one.setModel(self.model)
        self.tree_one.clicked.connect(self.display_info)
        self.tree_one.expand(self.index)
        self.tree_one.scrollTo(self.index)
        self.info_label = QLabel(self)
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.tree)
        self.v_layout.addWidget(self.info_label)
        self.setLayout(self.v_layout)
    def display_info(self):
        index_xlsx = self.tree.currentIndex()
        file_name_xlsx = self.model.fileName(index_xlsx)
        file_path_xlsx = self.model.filePath(index_xlsx)
        file_info_xlsx = 'File Name: {}\nFile Path: {}'.format(file_name_xlsx, file_path_xlsx)
        self.info_label.setText(file_info_xlsx)
class Addevice(QDialog):
    def __init__(self):
        super(Addevice, self).__init__()
        self.setWindowTitle('设备信息')
        self.resize(400, 400)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.camera_hd = QLabel(self)
        self.camera_hd.setText('高清摄像头端口地址：')
        self.camera_hd_url = QLineEdit(self)
        self.red_camera = QLabel(self)
        self.red_camera.setText('红外摄像头端口地址：')
        self.red_camera_url= QLineEdit(self)
        self.device_data=QLabel(self)
        self.device_data.setText('数据接入端口')
        self.device_data_url=QLineEdit(self)
        self.buttok = QPushButton('确认', self)
        self.buttcancel = QPushButton('取消', self)
        self.hlayout = QHBoxLayout()
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.camera_hd)
        self.vlayout.addWidget(self.camera_hd_url)
        self.vlayout.addWidget(self.red_camera)
        self.vlayout.addWidget(self.red_camera_url)
        self.vlayout.addWidget(self.device_data)
        self.vlayout.addWidget(self.device_data_url)
        self.hlayout.addWidget(self.buttok)
        self.hlayout.addWidget(self.buttcancel)
        self.grid1 = QGridLayout()
        self.grid1.addLayout(self.vlayout, 0, 0)
        self.grid1.addLayout(self.hlayout, 1, 0)
        self.setLayout(self.grid1)
        self.buttok.clicked.connect(self.get_data)
        self.buttcancel.clicked.connect(self.reject)
        self.show()
        self.exec_()
    def get_data(self):
        if self.device_data_url.text() == '' or self.camera_hd_url.text() == '' or self.red_camera_url.text()=='':
            QMessageBox.information(self,
                                    '提示',
                                    '输入不能为空！'
                                    )
        else:
            self.accept()
            self.sava_data()
            return self.camera_hd_url.text() ,self.red_camera_url.text(),self.device_data_url.text()
    def sava_data(self):
        with open('robot_data.ini',
                  'r',
                  encoding='utf-8'
                  ) as file:
            data_j = file.read()
            data_dic = json.loads(data_j)
            data_dic['hd']=self.camera_hd_url.text()
            data_dic['red']=self.red_camera_url.text()
            data_dic['data']=self.device_data_url.text()
            print(data_dic)
        jsondata = json.dumps(
            data_dic,
            sort_keys=True,
            indent=4,
            separators=(',', ': '),
            ensure_ascii=False
        )
        with open(
                'robot_data.ini',
                'w',
                encoding='utf-8'
        ) as f:
            f.write(jsondata)
    def style(self):
        self.setStyleSheet('QTabBar::tab{ border-bottom: none; '
                           'color: #000;'
                           ' padding: 4px;'
                           ' background-color: #888;'
                           ' border: 1px solid #555; }'
                           'QTabBar::tab:hover { background-color: #AAA; }'
                           'QTabWidget::pane {'
                           'border: none;'
                           'border-top: 3px solid rgb(0, 160, 230);'
                           'background: transparent;}'
                           'QTabWidget::tab-bar {border: none;}'
                            '{border-style:solid;border-color:rgb(1, 124, 217)}'
                            'background:transparent;}'
                           'QTabWidget::tab-bar{alignment:left;}'
                            'QTabBar::tab{'
                            'background-color: rgb(1, 124, 217);'
                            'background-color: rgb(4, 116, 191); '
                            'color:white;'
                            'min - width: 3px;'
                           'min - height: 10px;'
                            'border: 0px;'
                            'padding: 5px;}'
                            'QTabBar::tab: selected{'
                            'border - color: white;'
                            'background - color: rgb(238, 159, 0);'
                            'color: white;}'
                            'QTabBar::tab:!selecte{'
                            'margin - top: 5px;}'


                           'QTabBar::tab {border: none;'
                           'border-top-left-radius: 4px;'
                           'border-top-right-radius: 4px;'
                           'color: rgb(0, 0, 0);'
                           'background: rgb(255, 255, 255, 30);'
                           'height: 28px;'
                           'min-width: 85px;'
                           'margin-right: 5px;'
                           'padding-left: 5px;'
                           'padding-right: 5px;}'
                           'QTabBar::tab:hover {'
                           'background: rgb(0, 0, 255, 40);}'
                           'QTabBar::tab:selected {color: white;'
                           'background: rgb(0, 160, 230)'
                           '}')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    Monitor=GridWirless()
    print(type(GridWirless))
    Monitor.setWindowTitle('IPCAMERA')
    Monitor.setWindowIcon(QIcon('Icon/camera.png'))
    Monitor.setGeometry(40, 40, 1100, 600)
    Monitor.setStyleSheet(''
                       'QTableWidget{'
                       'color:#DCDCDC;'
                       'background:#444444;'
                       'border:1px solid #242424;'
                       'alternate-background-color:#525252;'
                       'gridline-color:#242424;}'
                       ' QTableWidget::item:selected{'
                       'color:#DCDCDC;'
                       'background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 #484848,stop:1 #383838)}'
                       'QTableWidget::item:hover{'
                       'background:#5B5B5B;}'
                       'QHeaderView::section{'
                       'text-align:center;'
                       'background:#5E5E5E;'
                       'padding:3px;'
                       'margin:0px;'
                       'color:#DCDCDC;'
                       'border:1px solid #242424;'
                       'border-left-width:0;}')
    Monitor.show()
    sys.exit(app.exec_())

