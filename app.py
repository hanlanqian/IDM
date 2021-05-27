import sys
import os
import globals_variable as g
from Pyqt_IDM.threads import MultiThreadDownload
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from UI import Ui_MainWindow

StopFlag = False
saveDir = 'route.txt'


class MyMain(QMainWindow):
    def __init__(self, parent=None):
        super(MyMain, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.chooseLocation.clicked.connect(self.choose)
        self.ui.startButton.clicked.connect(self.start_download)
        self.ui.pause_button.clicked.connect(self.pause_download)
        self.ui.stopButton.clicked.connect(self.stop_download)
        self.ui.pushButton.clicked.connect(self.setting)
        self.multidownload = MultiThreadDownload(self.show_download_info)
        self.multidownload.download_info_signal.connect(self.show_download_info)
        if os.path.exists(saveDir):
            with open(saveDir) as f:
                self.ui.lineEdit.setText(f.read())
        else:
            with open(saveDir, 'x') as f:
                pass

    def choose(self):
        if self.ui.checkBox.isChecked():
            if not os.path.exists(saveDir):
                QMessageBox.information(self, '警告', '您未曾选择过默认路径\n请前往设置界面设置路径\n或者取消选择默认路径下载')
            else:
                with open(saveDir, 'r') as f:
                    dir_path = f.read()
                self.ui.filepathEdit.setText(dir_path + '/')
        else:
            dir_path = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", "/:")
            self.ui.filepathEdit.setText(dir_path + '/')

    def show_download_info(self, info):
        if 'info' in info.keys():
            self.ui.Download_info.appendPlainText(info['info'])
            if 'value' in info.keys():
                if info['value'] < 0.0:
                    QMessageBox.information(self, "出错啦", "解析链接失败")
                elif info['value'] > 0.0:
                    QMessageBox.information(self, "Bilibili error", "BV号解析失败")
        else:
            self.ui.Download_info.undo()
            self.ui.MainprogressBar.setValue(int(info['downloaded'] / g.globals_variable.file_size * 100))
            download_info = ""
            for thread_id, process in info['sub_downloaded'].items():
                if process > 100:
                    process = 100
                    QMessageBox.information(self, "成功！", "您的下载已经完成")
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
        g.globals_variable.__init__()
        self.ui.Download_info.setPlainText("")
        self.ui.MainprogressBar.setValue(0)
        g.globals_variable.filepath = self.ui.filepathEdit.text()
        if self.ui.DownloadType.currentText() == 'URL':
            g.globals_variable.url = self.ui.URLlineEdit.text()
            g.globals_variable.filename = g.globals_variable.url.split('?')[0].split('/')[-1]
            g.globals_variable.Type = 'URL'
        elif self.ui.DownloadType.currentText() == 'BVid':
            g.globals_variable.BVid = self.ui.URLlineEdit.text()
            g.globals_variable.Type = 'Bilibili'
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
            QMessageBox.information(self, "错误", "你还没有开始下载！")
        else:
            self.multidownload.stop()
            self.ui.Download_info.appendPlainText('成功结束下载！')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MyMain()
    MainWindow.show()
    sys.exit(app.exec_())
