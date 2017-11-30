import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon
from pyEyeRpt_Read import getData, ptRemove, getDataAcc
import os
from bs4 import BeautifulSoup
import pandas as pd
import codecs

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.openFileNameDialog()
        #self.openFileNamesDialog()
        #self.saveFileDialog()
        # self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        #fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
        #                                          "All Files (*);;Python Files (*.py)", options=options)

        dir = QFileDialog.getExistingDirectory()
        df_keys = {'corner': [], 'Scope Model': [], 'CDR_Setting': [],
                   'Tie_PP': [], 'Cycle_num': [], 'RJstd': [],
                   'TJpp': [], 'DJpp': [], 'DCD': []}
        if dir:
            print(dir)
            for file in os.listdir(dir):
                if file.endswith(".mht"):
                    # print(os.path.join("SR3596_AB", file))
                    fname = dir + '\\' + file
                    #print(fname)
                    #soup = BeautifulSoup(open(fname, encoding='utf-8'), "lxml")
                    soup = BeautifulSoup(codecs.open(fname, "r",encoding='utf-8', errors='ignore'), "lxml")
                    data = getData(soup, file)
                    print(data)
                    for keys in data.keys():
                        df_keys[keys].append(data[keys])
                        # print(df_keys)
                    # print(data)
                    df = pd.DataFrame(df_keys, index=df_keys['corner'])
                    print(df)
                    df.to_csv(os.path.join(dir, 'eye_sum.csv'))
        return dir


    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())