from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from designer import *
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.result = 0
        self.operation = None

    def add0(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'0')

    def add1(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'1')

    def add2(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'2')

    def add3(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'3')

    def add4(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'4')

    def add5(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'5')

    def add6(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'6')

    def add7(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'7')

    def add8(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'8')

    def add9(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text()+'9')

    def equal(self):
        self.ui.lineEdit.setText(str(eval(self.result+self.operation+self.ui.lineEdit.text())))

    def plus(self):
        self.operation = '+'
        self.result = self.ui.lineEdit.text()
        self.ui.lineEdit.setText('')

    def sub(self):
        self.operation = '-'
        self.result = self.ui.lineEdit.text()
        self.ui.lineEdit.setText('')

    def times(self):
        self.operation = '*'
        self.result = self.ui.lineEdit.text()
        self.ui.lineEdit.setText('')

    def divide(self):
        self.operation = '/'
        self.result = self.ui.lineEdit.text()
        self.ui.lineEdit.setText('')

    def clear(self):
        self.ui.lineEdit.setText('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
