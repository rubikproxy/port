from PyQt5.QtWidgets import *
from PyQt5 import uic

class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI,self).__init__()
        uic.loadUi("mail.ui",self)
        self.show()
        
        self.pushButton.clicked.connect(self.login)
        self.pushButton_2.clicked.connect(self.attach_sth)
        self.pushButton_3.clicked.connect(self.send_mail)
    def login(self):
        print("hello")
    def attach_sth(self):
        pass
    def send_mail(self):
        pass

app = QApplication([])
window = MyGUI
app.exec_()
