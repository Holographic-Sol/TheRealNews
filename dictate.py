"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""
import os
import sys
import time
import win32api
import win32process
import win32con
import win32clipboard
from gtts import gTTS
from win32api import GetMonitorInfo, MonitorFromPoint
from PyQt5.QtCore import Qt, QThread, QSize, QPoint, QCoreApplication, QObject, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QDesktopWidget, QWidget, QGroupBox, QTextBrowser, QLineEdit
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5 import QtCore
import requests
from bs4 import BeautifulSoup
import re
import glob

print('initializing:')
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    print('-- AA_EnableHighDpiScaling: True')
elif not hasattr(Qt, 'AA_EnableHighDpiScaling'):
    print('-- AA_EnableHighDpiScaling: False')
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    print('-- AA_UseHighDpiPixmaps: True')
elif not hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    print('-- AA_UseHighDpiPixmaps: False')

priority_classes = [win32process.IDLE_PRIORITY_CLASS,
                    win32process.BELOW_NORMAL_PRIORITY_CLASS,
                    win32process.NORMAL_PRIORITY_CLASS,
                    win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                    win32process.HIGH_PRIORITY_CLASS,
                    win32process.REALTIME_PRIORITY_CLASS]
pid = win32api.GetCurrentProcessId()
print('-- process id:', pid)
handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
win32process.SetPriorityClass(handle, priority_classes[4])
print('-- win32process priority class:', priority_classes[4])

out_of_bounds = False
send_data_thread_bool = False
ln_edit_0_thread_bool = False
data_bool = False
glo_obj = []
prev_obj_eve = []
send_data_thread = ()
ln_edit_0_thread = ()
lbl_crawler_indic_thread = ()
lbl_gtts_indic_thread = ()
title = ''


class App(QMainWindow):
    cursorMove = QtCore.pyqtSignal(object)

    def __init__(self):
        super(App, self).__init__()
        global glo_obj

        self.setWindowIcon(QIcon('./icon.png'))
        self.title = 'The Real News'
        print('-- setting self.title as:', self.title)
        self.setWindowTitle(self.title)
        self.width = 760
        self.height = 800
        self.prev_width = ()
        self.prev_height = ()
        self.prev_pos_w = ()
        self.prev_pos_h = ()
        self.prev_pos = self.pos()
        pos_w = QDesktopWidget().availableGeometry().width()
        pos_h = QDesktopWidget().availableGeometry().height()
        pos_w = (pos_w / 2) - (self.width / 2)
        pos_h = (pos_h / 2) - (self.height / 2)
        print('-- setting window dimensions:', self.width, self.height)
        self.setGeometry(pos_w, pos_h, self.width, self.height)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setPalette(p)
        newfont = QFont("Times", 4)
        self.cursorMove.connect(self.handleCursorMove)
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.pollCursor)
        self.timer.start()
        self.cursor = None

        self.lbl_title_bg = QLabel(self)
        self.lbl_title_bg.move(0, 0)
        self.lbl_title_bg.resize(self.width - 200, 40)
        self.lbl_title_bg.setStyleSheet(
            """QLabel {background-color: rgb(0, 0, 0);
           border:0px solid rgb(35, 35, 35);}"""
        )
        print('-- created lbl_title_bg', self.lbl_title_bg)
        glo_obj.append(self.lbl_title_bg)

        self.btn_title_logo = QPushButton(self)
        self.btn_title_logo.move(0, 0)
        self.btn_title_logo.resize(40, 40)
        # self.btn_title_logo.setIcon(QIcon("./icon.png"))
        self.btn_title_logo.setIconSize(QSize(36, 36))
        self.btn_title_logo.setStyleSheet(
            """QPushButton{background-color: rgb(0, 0, 0);
               border:0px solid rgb(0, 0, 0);}"""
        )
        print('-- created btn_title_logo', self.btn_title_logo)
        glo_obj.append(self.btn_title_logo)

        self.lbl_main_bg = QLabel(self)
        self.lbl_main_bg.move(0, 40)
        self.lbl_main_bg.resize(self.width, (self.height - 60))
        self.lbl_main_bg.setStyleSheet(
            """QLabel {background-color: rgb(15, 15, 15);
           border:0px solid rgb(35, 35, 35);}"""
        )
        print('-- created lbl_main_bg', self.lbl_main_bg)
        glo_obj.append(self.lbl_main_bg)

        self.btn_quit = QPushButton(self)
        self.btn_quit.move((self.width - 40), 0)
        self.btn_quit.resize(40, 40)
        self.btn_quit.setIcon(QIcon("./image/img_close.png"))
        self.btn_quit.setIconSize(QSize(10, 10))
        self.btn_quit.clicked.connect(QCoreApplication.instance().quit)
        self.btn_quit.setStyleSheet(
            """QPushButton{background-color: rgb(0, 0, 0);
               border:0px solid rgb(0, 0, 0);}"""
        )
        print('-- created self.btn_quit', self.btn_quit)
        glo_obj.append(self.btn_quit)
        self.btn_minimize = QPushButton(self)
        self.btn_minimize.move((self.width - 80), 0)
        self.btn_minimize.resize(40, 40)
        self.btn_minimize.setIcon(QIcon("./image/img_minimize.png"))
        self.btn_minimize.setIconSize(QSize(40, 40))
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_minimize.setStyleSheet(
            """QPushButton{background-color: rgb(0, 0, 0);
               border:0px solid rgb(0, 0, 0);}"""
        )
        print('-- created self.btn_minimize', self.btn_minimize)
        glo_obj.append(self.btn_minimize)
        self.btn_apnd = QPushButton(self)
        self.btn_apnd.move(0, 45)
        self.btn_apnd.resize(20, 20)
        self.btn_apnd.clicked.connect(self.btn_apnd_func)
        self.btn_apnd.setStyleSheet(
            """QPushButton{background-color: rgb(0, 0, 255);
               color: rgb(0, 0, 255);
               border:0px solid rgb(0, 0, 255);}"""
        )
        print('-- created self.btn_apnd', self.btn_apnd)

        self.btn_clr = QPushButton(self)
        self.btn_clr.move((self.width - 20), 45)
        self.btn_clr.resize(20, 20)
        self.btn_clr.clicked.connect(self.btn_clr_func)
        self.btn_clr.setStyleSheet(
            """QPushButton{background-color: rgb(255, 0, 0);
               color: rgb(255, 0, 0);
               border:0px solid rgb(0, 0, 0);}"""
        )
        print('-- created self.btn_clr', self.btn_clr)

        self.btn_dict = QPushButton(self)
        self.btn_dict.move(0, 90)
        self.btn_dict.resize(20, 20)
        self.btn_dict.clicked.connect(self.btn_dict_func)
        self.btn_dict.setStyleSheet(
            """QPushButton{background-color: rgb(0, 0, 255);
               color: rgb(0, 0, 255);
               border:0px solid rgb(0, 0, 0);}"""
        )
        print('-- created self.btn_dict', self.btn_dict)

        self.btn_opn_rec = QPushButton(self)
        self.btn_opn_rec.move(0, 135)
        self.btn_opn_rec.resize(20, 20)
        self.btn_opn_rec.clicked.connect(self.btn_opn_rec_func)
        self.btn_opn_rec.setStyleSheet(
            """QPushButton{background-color: rgb(0, 0, 255);
               color: rgb(0, 0, 255);
               border:0px solid rgb(0, 0, 0);}"""
        )
        print('-- created self.btn_opn_rec', self.btn_opn_rec)
        self.lbl_gtts_indic = QLabel(self)
        self.lbl_gtts_indic.move(15, 90)
        self.lbl_gtts_indic.resize(5, 5)
        self.lbl_gtts_indic.setStyleSheet(
            """QLabel {background-color: rgb(0, 255, 0);
           border:0px solid rgb(35, 35, 35);}"""
        )
        print('-- created lbl_gtts_indic', self.lbl_gtts_indic)
        self.lbl_gtts_indic.hide()

        self.setStyleSheet("""
                    QScrollBar:vertical {width: 22px;
                    margin: 22px 0 22px 0;
                    background-color: black;
                    }
                    QScrollBar::handle:vertical {
                    background-color: black;
                    min-height: 22px;
                    }
                    QScrollBar::add-line:vertical {
                    background-color: black;
                    height: 22px;
                    subcontrol-position: bottom;
                    subcontrol-origin: margin;
                    }
                    QScrollBar::sub-line:vertical {
                    background-color: black;
                    height: 22px;
                    subcontrol-position: top;
                    subcontrol-origin: margin;
                    }
                    QScrollBar::up-arrow:vertical {
                    image:url('./image/small_img_menu_up.png');
                    height: 22px;
                    width: 22px;
                    }
                    QScrollBar::down-arrow:vertical {
                    image:url('./image/small_img_menu_down.png');
                    height: 22px;
                    width: 22px;
                    }
                    QScrollBar::add-page:vertical {
                    background: rgb(25, 25, 25);
                    }
                    QScrollBar::sub-page:vertical {
                    background: rgb(25, 25, 25);
                    }

                    QScrollBar:horizontal {
                    height: 22px;
                    margin: 0px 22px 0 22px;
                    background-color: black;
                    }
                    QScrollBar::handle:horizontal {
                    background-color: black;
                    min-width: 22px;
                    }
                    QScrollBar::add-line:horizontal {
                    background-color: black;
                    width: 22px;
                    subcontrol-position: right;
                    subcontrol-origin: margin;
                    }
                    QScrollBar::sub-line:horizontal {
                    background-color: black;
                    width: 22px;
                    subcontrol-position: top left;
                    subcontrol-origin: margin;
                    position: absolute;
                    }
                    QScrollBar::left-arrow:horizontal {
                    image:url('./image/small_img_menu_left.png');
                    height: 22px;
                    width: 22px;
                    }
                    QScrollBar::right-arrow:horizontal {
                    image:url('./image/small_img_menu_right.png');
                    height: 22px;
                    width: 22px;
                    }
                    QScrollBar::add-page:horizontal {
                    background: rgb(25, 25, 25);
                    }
                    QScrollBar::sub-page:horizontal {
                    background: rgb(25, 25, 25);
                    }
                    """)
        tb_0_position_h = 45
        tb_0_position_w = 22
        tb_0_height = self.height - 100
        self.tb_0 = QTextBrowser(self)
        self.tb_0.move(tb_0_position_w, tb_0_position_h)
        self.tb_0.resize((self.width - (tb_0_position_w * 2)), tb_0_height)
        self.tb_0.setObjectName("tb_0")
        self.tb_0.setStyleSheet(
            """QTextBrowser {background-color: black;
            border:0px solid rgb(30, 30, 30);
            selection-color: black;
            selection-background-color: rgb(0, 180, 0);
            color: rgb(0, 180, 0);}"""
        )
        self.tb_0.horizontalScrollBar().setValue(0)
        glo_obj.append(self.tb_0)
        self.ln_edit_0 = QLineEdit(self)
        self.ln_edit_0.move((tb_0_position_w + 85), (tb_0_position_h + tb_0_height + 5))
        self.ln_edit_0.resize((self.width - (tb_0_position_w * 2) - 85), 25)
        self.ln_edit_0.setReadOnly(False)
        font_ln_edit_0 = QFont("Times", 9)
        self.ln_edit_0.setFont(font_ln_edit_0)
        self.ln_edit_0.setStyleSheet(
            """QLineEdit {background-color: black;
            border:0px solid rgb(30, 30, 30);
            selection-color: black;
            selection-background-color: rgb(0, 255, 0);
            color: rgb(115, 255, 0);}"""
        )
        self.ln_edit_0.returnPressed.connect(self.ln_edit_0_function)
        self.url_lbl = QLabel(self)
        self.url_lbl.move(tb_0_position_w, (tb_0_position_h + tb_0_height + 5))
        self.url_lbl.resize(70, 25)
        self.url_lbl.setText("Enter URL:")
        self.url_lbl.setStyleSheet(
            """QLabel {background-color: rgb(15, 15, 15);
           color: rgb(0, 255, 0);
           border:0px solid rgb(35, 35, 35);}"""
        )
        print('-- created url_lbl', self.url_lbl)

        self.lbl_crawler_indic = QLabel(self)
        self.lbl_crawler_indic.move((self.width - 15), (self.height - 15))
        self.lbl_crawler_indic.resize(5, 5)
        self.lbl_crawler_indic.setStyleSheet(
            """QLabel {background-color: rgb(0, 255, 0);
           border:0px solid rgb(35, 35, 35);}"""
        )
        print('-- created lbl_crawler_indic', self.lbl_crawler_indic)
        self.lbl_crawler_indic.hide()

        self.initUI()

    def initUI(self):
        global send_data_thread, ln_edit_0_thread, lbl_crawler_indic_thread, lbl_gtts_indic_thread
        scaling_thread = ScalingClass(self.setGeometry, self.width, self.height, self.pos, self.frameGeometry,
                                      self.setFixedSize)
        scaling_thread.start()
        send_data_thread = SendDataClass(self.tb_0, self.lbl_gtts_indic)
        ln_edit_0_thread = LnEdit0Class(self.tb_0, self.lbl_gtts_indic, self.ln_edit_0, self.lbl_crawler_indic)

        lbl_crawler_indic_thread = lbl_crawler_indic_Class(self.lbl_crawler_indic)
        lbl_gtts_indic_thread = lbl_gtts_indic_Class(self.lbl_gtts_indic)

        print('\ndisplaying application:')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.prev_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.prev_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.prev_pos = event.globalPos()

    def pollCursor(self):
        pos = QCursor.pos()
        if pos != self.cursor:
            self.cursor = pos
            self.cursorMove.emit(pos)

    def handleCursorMove(self, pos):
        global out_of_bounds
        if pos.x() > self.x() and pos.x() < (self.x() + self.width) and\
                pos.y() < (self.y() + self.height) and pos.y() > self.y() and self.isMinimized() is False:
            out_of_bounds = False
        else:
            out_of_bounds = True
            glo_obj[2].setStyleSheet(
                """QLabel {background-color: rgb(15, 15, 15);
               border:0px solid rgb(35, 35, 35);}"""
            )
            glo_obj[3].setStyleSheet(
                """QPushButton{background-color: rgb(0, 0, 0);
                   border:0px solid rgb(0, 0, 0);}"""
            )
            glo_obj[4].setStyleSheet(
                """QPushButton{background-color: rgb(0, 0, 0);
                   border:0px solid rgb(0, 0, 0);}"""
            )

    def btn_opn_rec_func(self):
        print('-- btn_opn_rec: clicked')
        try:
            list_of_files = glob.glob('.\\data\\*')
            latest_file = max(list_of_files, key=os.path.getctime)
            print(latest_file)
            cwd = os.getcwd() + latest_file[1:]
            print(cwd)
            os.system(latest_file)
        except Exception as e:
            print(e)

    def btn_apnd_func(self):
        print('-- btnapnd: clicked')
        try:
            win32clipboard.OpenClipboard()
            cb = win32clipboard.GetClipboardData()
            print(cb)
            self.tb_0.append(cb)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(e)

    def btn_clr_func(self):
        global data_bool
        print('--btn_clr: clicked ')
        try:
            self.tb_0.setText('')
            data_bool = False
        except Exception as e:
            print(e)

    def btn_dict_func(self):
        global send_data_thread_bool
        global send_data_thread
        print('-- btn_dict: clicked')
        try:
            if send_data_thread_bool is False:
                print('-- send_data_thread: vacant')
                send_data_thread.start()
            elif send_data_thread_bool is True:
                print('-- send_data_thread: stopping')
                send_data_thread.stop_send_data()
        except Exception as e:
            print(e)

    def ln_edit_0_function(self):
        print('-- returnPressed: ln_edit_0')
        try:
            global ln_edit_0_thread, ln_edit_0_thread_bool
            if ln_edit_0_thread_bool is False:
                print('-- ln_edit_0_thread: vacant')
                self.tb_0.setText('')
                ln_edit_0_thread.start()
            elif ln_edit_0_thread_bool is True:
                print('-- ln_edit_0_thread: engaged, please wait or cancel operation...')
        except Exception as e:
            print(e)


class lbl_crawler_indic_Class(QThread):
    def __init__(self, lbl_crawler_indic):
        QThread.__init__(self)
        self.lbl_crawler_indic = lbl_crawler_indic

    def run(self):
        print('-- thread started: lbl_crawler_indic_Class(QThread).run(self)')
        global ln_edit_0_thread_bool
        while ln_edit_0_thread_bool is True:
            self.lbl_crawler_indic.show()
            time.sleep(0.5)
            self.lbl_crawler_indic.hide()
            time.sleep(0.5)


class lbl_gtts_indic_Class(QThread):
    def __init__(self, lbl_gtts_indic):
        QThread.__init__(self)
        self.lbl_gtts_indic = lbl_gtts_indic

    def run(self):
        print('-- thread started: lbl_gtts_indic_Class(QThread).run(self)')
        global send_data_thread_bool
        print('send_data_thread_bool', send_data_thread_bool)
        while send_data_thread_bool is True:
            self.lbl_gtts_indic.show()
            time.sleep(0.5)
            self.lbl_gtts_indic.hide()
            time.sleep(0.5)


class LnEdit0Class(QThread):
    def __init__(self, tb_0, lbl_gtts_indic, ln_edit_0, lbl_crawler_indic):
        QThread.__init__(self)
        self.tb_0 = tb_0
        self.lbl_gtts_indic = lbl_gtts_indic
        self.ln_edit_0 = ln_edit_0
        self.lbl_crawler_indic = lbl_crawler_indic

    def run(self):
        print('-- thread started: LnEdit0Class(QThread).run(self)')
        global send_data_thread_bool, ln_edit_0_thread_bool, title, data_bool, lbl_crawler_indic_thread
        global lbl_gtts_indic_thread
        ln_edit_0_thread_bool = True
        lbl_crawler_indic_thread.start()

        try:
            dgt = 0
            dgt_item = []
            for dirName, subdirList, fileList in os.walk(".\\data"):
                for fname in fileList:
                    if fname.endswith(".mp3") and fname.startswith("audio_"):
                        try:
                            name = fname.strip()
                            name = name.replace("audio_", "")
                            name = name.replace(".mp3", "")
                            if name.isdigit():
                                dgt_item.append(name)
                        except Exception as e:
                                print(e)
        except Exception as e:
            print(e)

        try:
            if len(dgt_item) >= 1:
                max_dgt = int(max(dgt_item))
                dgt = (max_dgt + 1)
        except Exception as e:
            print(e)

        try:
            out_name = "audio_" + str(dgt)
            print(out_name)
            ln_edit_0_text = self.ln_edit_0.text()
            print('-- ln_edit_0_text:', ln_edit_0_text)
            txt_var = ''
        except Exception as e:
            print(e)

        try:
            idx0 = ln_edit_0_text.rfind('/') + 1
            title = ln_edit_0_text[idx0:]
            if len(title) is 0:
                title = out_name
            re.sub(r'\W+', '', title)
            print('-- Title:', title)
            rHead = requests.get(ln_edit_0_text)
            data = rHead.text
            soup = BeautifulSoup(data, features="html")
            for row in soup.find_all('p'):
                text = row.get_text()
                text = re.sub(r'\[.*?\]', '', text)
                print(text)
                txt_var = txt_var + text
            self.tb_0.append(txt_var)
            self.tb_0.verticalScrollBar().setValue(0)
            self.ln_edit_0.setText('')
        except Exception as e:
            print(e)
        ln_edit_0_thread_bool = False
        data_bool = False
        print('-- crawler finished')


class SendDataClass(QThread):
    def __init__(self, tb_0, lbl_gtts_indic):
        QThread.__init__(self)
        self.tb_0 = tb_0
        self.lbl_gtts_indic = lbl_gtts_indic

    def run(self):
        global send_data_thread_bool, title, data_bool, lbl_gtts_indic_thread
        send_data_thread_bool = True
        lbl_gtts_indic_thread.start()
        print('-- thread started: SendDataClass(QThread).run(self)')
        try:
            if not os.path.exists('./' + title + '.mp3'):
                print('-- SendDataClass: adding new audio file,', title)
                text = self.tb_0.toPlainText()
                print('-- SendDataClass: sending text to google servers')
                tts = gTTS(text=text, lang='en')
                tts.save("./data/" + title + ".mp3")
                time.sleep(1)
                send_data_thread_bool = False
                data_bool = True
                print('-- SendDataClass: finished')
            elif os.path.exists('./' + title + '.mp3'):
                print('-- SendDataClass: audio already exists,', title)
                send_data_thread_bool = False
                data_bool = False
        except Exception as e:
            print(e)
        send_data_thread_bool = False

    def stop_send_data(self):
        try:
            global send_data_thread_bool, data_bool
            send_data_thread_bool = False
            data_bool = False
            self.lbl_gtts_indic.hide()
            self.terminate()
        except Exception as e:
            print(e)


class ScalingClass(QThread):
    def __init__(self, setGeometry, width, height, pos, frameGeometry, setFixedSize):
        QThread.__init__(self)
        self.setGeometry = setGeometry
        self.width = width
        self.height = height
        self.pos = pos
        self.frameGeometry = frameGeometry
        self.setFixedSize = setFixedSize

    def run(self):
        print('-- thread started: ScalingClass(QThread).run(self)')

        # Store Work Area Geometry For Comparison
        monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
        work_area = monitor_info.get("Work")
        scr_geo0 = work_area[3]

        while True:
            try:
                time.sleep(0.1)

                # Get Work Area Geometry Each Loop
                monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
                work_area = monitor_info.get("Work")
                scr_geo1 = work_area[3]

                # Compare Current Work Area Geometry To Stored Work Area Geometry
                if scr_geo0 != scr_geo1:

                    # I Use This To Compliment AA_EnableHighDpiScaling, I Find Moving the Window Helps Update Re-Scaling
                    print('-- ScalingClass(QThread).run(self) ~ refreshing geometry')
                    self.setGeometry(self.pos().x(), self.pos().y(), self.width, self.height)

                    # Store Current Work Area Geometry Again Since It Has Changed
                    scr_geo0 = scr_geo1
            except Exception as e:
                print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
