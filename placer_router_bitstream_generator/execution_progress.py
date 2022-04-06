import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

StyleSheet = '''
#RedProgressBar {
    text-align: center;
}
#RedProgressBar::chunk {
    background-color: #F44336;
}
#GreenProgressBar {
    min-height: 12px;
    max-height: 12px;
    border-radius: 6px;
}
#GreenProgressBar::chunk {
    border-radius: 6px;
    background-color: #009688;
}
#BlueProgressBar {
    border: 2px solid #17e8b0;
    border-radius: 5px;
    background-color: #E0E0E0;
}
#BlueProgressBar::chunk {
    background-color: #17e8b0;
    width: 45px; 
    margin: 0.5px;
}
'''

class pg_bar(QObject):
    pg_bar_value = pyqtSignal(int)
    pg_bar_finished=pyqtSignal()
    def __init__(self,pbar):
        super(pg_bar, self).__init__(pbar)
        self.pbar=pbar
        
    def signal_accept(self, msg):
        self.pbar.setValue(int(msg))

                        
class ProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super(ProgressBar, self).__init__(*args, **kwargs)



class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.setWindowTitle('Code execution status')

        self.pbar = ProgressBar(self, minimum=0, maximum=5, textVisible=False,objectName="BlueProgressBar")
        self.pbar.setFixedWidth(225)
        self.pbar.setValue(0)
        self.resize(500, 100)
        
        
        self.txt=QTextEdit(self)
        self.txt.csr=self.txt.textCursor()
        self.txt.setStyleSheet("color: rgb(25, 176, 143);")

        self.txt.setReadOnly(True)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.pbar,alignment=Qt.AlignCenter)
        self.vbox.addWidget(self.txt)
        self.setLayout(self.vbox)
        
        self.pg_bar_thd=QThread()
        self.pg_bar = pg_bar(self.pbar)
        self.pg_bar.moveToThread(self.pg_bar_thd)
        self.pg_bar.pg_bar_value.connect(self.pg_bar.signal_accept)
        self.pg_bar.pg_bar_finished.connect(self.pg_bar_thd.quit)
        self.pg_bar.pg_bar_finished.connect(self.pg_bar_thd.deleteLater)
        self.pg_bar_thd.finished.connect(self.pg_bar_thd.deleteLater)
        
        self.pg_bar_thd.start()
        
        self.show()
                        
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()