import sys
import threading
import os
import you_get
import globals_varible as g
from Pyqt_IDM.threads import MultiThreadDownload, ParseVideoLink
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from ui.UI import Ui_MainWindow


class MyMain(QMainWindow):
    def __init__(self, parent=None):
        super(MyMain, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.chooseLocation.clicked.connect(self.choose)
        self.ui.startButton.clicked.connect(self.start_download)
        self.ui.stopButton.clicked.connect(self.stop_download)
        self.ui.pushButton.clicked.connect(self.setting)
        self.multidownload = MultiThreadDownload(self.show_download_info)
        self.multidownload.download_info_signal.connect(self.show_download_info)

    def choose(self):
        if self.ui.checkBox.isChecked():
            if not os.path.exists('route.txt'):
                QMessageBox.information(self, '警告', '您未曾选择过默认路径\n请前往设置界面设置路径\n或者取消选择默认路径下载')
            else:
                f = open('route.txt', 'r')
                dir_path = f.read()
                f.close()
                self.ui.lineEdit_2.setText(dir_path + '/')
        else:
            dir_path = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", "/:")
            self.ui.lineEdit.setText(dir_path + '/')

    def show_download_info(self, info, value):
        if value > 0.0:
            self.ui.MainprogressBar.setValue(int(value/g.file_size*100))
            self.ui.Download_info.undo()
            self.ui.Download_info.appendPlainText(info)
        else:
            self.ui.Download_info.appendPlainText(info)

    def setting(self):
        dir_path = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", "/:")
        self.ui.lineEdit_2.setText(dir_path)
        with open('route/route.txt', 'w') as f:
            f.write(dir_path)

    def start_download(self):
        self.ui.Download_info.setPlainText("")
        g.filepath = self.ui.lineEdit.text()
        if self.ui.DownloadType.currentText() == 'URL':
            g.url = self.ui.URLlineEdit.text()
            g.filename = g.url.split('?')[0].split('/')[-1]
            g.Type = 'URL'
        elif self.ui.DownloadType.currentText() == 'BVid':
            g.BVid = self.ui.URLlineEdit.text()
            g.Type = 'Bilibili'
        g.threads_num = self.ui.horizontalSlider.value()
        self.multidownload.start()
        QMessageBox.show("多线程下载已启动")

    def stop_download(self):
        self.multidownload.stop()
        self.ui.Download_info.appendPlainText('成功结束下载！')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MyMain()
    MainWindow.show()
    sys.exit(app.exec_())
