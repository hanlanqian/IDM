import sys
import os

from PyQt5 import QtGui
import re
import globals_variable as g
from Pyqt_IDM.threads import MultiThreadDownload
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from UI import Ui_MainWindow

StopFlag = False
saveDir = 'route.txt'
logDir = './log.txt'
logDirPath = './logPath.txt'


class MyMain(QMainWindow):
    def __init__(self, parent=None):
        global logDir, logDirPath
        super(MyMain, self).__init__(parent)
        self.setObjectName('MainWindow')
        self.Success = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initPath()
        self.ui.logPathEdit.setText(logDir)
        self.ui.chooseLocation.clicked.connect(self.choose)
        self.ui.startButton.clicked.connect(self.start_download)
        self.ui.pause_button.clicked.connect(self.pause_download)
        self.ui.stopButton.clicked.connect(self.stop_download)
        self.ui.pushButton.clicked.connect(self.setting)
        self.ui.chooseBT.clicked.connect(self.logPath)
        self.ui.log_button.clicked.connect(self.showLog)
        self.multidownload = MultiThreadDownload(self.show_download_info)
        self.multidownload.download_info_signal.connect(self.show_download_info)

    def initPath(self):
        global logDir, logDirPath
        # 默认下载文件位置
        if os.path.exists(saveDir):
            with open(saveDir) as f:
                self.ui.lineEdit.setText(f.read())
        else:
            with open(saveDir, 'x') as f:
                pass
        if os.path.exists(logDirPath):
            with open(logDirPath) as f:
                logDir = f.read()+'/log.txt'
        else:
            pass

    # 重写主窗口关闭事件，实现对本次软件使用的日志导入
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        global logDir, logDirPath
        if self.ui.log_checkBox.isChecked() and not self.ui.log_checkBox2.isChecked():
            with open(logDir, 'a') as f:
                f.write('此次运行日志为：\n')
                f.write(self.ui.Download_info.toPlainText())
                f.write('\n\n\n')

    def choose(self):
        if self.ui.checkBox.isChecked():
            if not os.path.exists(saveDir):
                QMessageBox.warning(self, '警告', '您未曾选择过默认路径\n请前往设置界面设置路径\n或者取消选择默认路径下载')
            else:
                with open(saveDir, 'r') as f:
                    dir_path = f.read()
                self.ui.filepathEdit.setText(dir_path + '/')
        else:
            dir_path = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", "/:")
            if dir_path:
                self.ui.filepathEdit.setText(dir_path + '/')

    def logPath(self):
        # 默认日志位置为./log.txt
        if self.ui.log_checkBox.isChecked():
            logDir = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", "/:")
            with open(logDirPath, 'w') as f:
                f.write(logDir)
            self.ui.logPathEdit.setText(logDir)
        else:
            QMessageBox.critical(self, '错误', '您还没有启用日志功能')

    def showLog(self):
        global logDir
        if self.ui.log_checkBox.isChecked():
            if os.path.exists(logDir):
                with open(logDir, 'r') as f:
                    self.ui.log_plainEdit.setPlainText(f.read())
            else:
                QMessageBox.critical(self, '错误', '第一次使用暂无日志文件')
        else:
            QMessageBox.critical(self, '错误', '您还没有启用日志功能')

    def show_download_info(self, info):
        if 'info' in info.keys():
            self.ui.Download_info.appendPlainText(info['info'])
            if 'value' in info.keys():
                if info['value'] < 0.0:
                    QMessageBox.critical(self, "出错啦", "暂不支持多分p视频下载")
                elif info['value'] > 0.0:
                    QMessageBox.critical(self, "Bilibili error", "BV号解析失败")
        else:
            self.ui.Download_info.undo()
            percent = int(info['downloaded'] / g.globals_variable.file_size * 100)
            self.ui.MainprogressBar.setValue(percent)
            if percent == 100 and self.Success:
                self.Success = True
                QMessageBox.information(self, "成功", "您的下载已经成功完成")
            download_info = ""
            for thread_id, process in info['sub_downloaded'].items():
                if process > 100:
                    process = 100
                download_info += 'INFO: {' + thread_id + '}' + str(round(process, 3)) + '%' + '\n'
            self.ui.Download_info.appendPlainText(download_info)
            self.ui.Download_info.moveCursor(QTextCursor.End)

    def setting(self):
        dir_path = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", "/:")
        if dir_path:
            self.ui.lineEdit.setText(dir_path)
            with open(saveDir, 'w') as f:
                f.write(dir_path)
            QMessageBox.information(self, '提示', '默认保存位置已写入route文件')

    def start_download(self):
        StartFlag = True
        g.globals_variable.__init__()
        self.ui.Download_info.setPlainText("")
        self.ui.MainprogressBar.setValue(0)
        g.globals_variable.filepath = self.ui.filepathEdit.text()
        if self.ui.DownloadType.currentText() == 'URL':
            if not re.match(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', self.ui.URLlineEdit.text()):
                QMessageBox.warning(self, '警告', '您输入的链接格式错误')
                StartFlag = False
            else:
                g.globals_variable.url = self.ui.URLlineEdit.text()
                g.globals_variable.filename = g.globals_variable.url.split('?')[0].split('/')[-1]
                g.globals_variable.Type = 'URL'
        elif self.ui.DownloadType.currentText() == 'BVid':
            if not re.match(r'BV[A-Za-z0-9]{10}', self.ui.URLlineEdit.text()):
                QMessageBox.warning(self, '警告', '您输入的BV号格式错误')
                StartFlag = False
            else:
                g.globals_variable.BVid = self.ui.URLlineEdit.text()
                g.globals_variable.Type = 'Bilibili'
        if StartFlag:
            g.globals_variable.threads_num = self.ui.horizontalSlider.value()
            self.multidownload.start()

    def pause_download(self):
        self.multidownload.pause()
        if self.ui.pause_button.text() == '暂停下载':
            self.ui.pause_button.setText('继续下载')
        else:
            self.ui.pause_button.setText('暂停下载')

    def stop_download(self):
        if not self.multidownload.isRunning():
            QMessageBox.critical(self, "错误", "你还没有开始下载！")
        else:
            self.multidownload.stop()
            self.multidownload.terminate()
            self.ui.Download_info.appendPlainText('成功结束下载！')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MyMain()
    MainWindow.show()
    sys.exit(app.exec_())
