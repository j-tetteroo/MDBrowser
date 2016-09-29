#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys

from PyQt4.QtWebKit import QWebView
from PyQt4.QtGui import QApplication
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QUrl
from markdown import markdown
import urllib2
'''
# Qt4 app
app = QApplication(sys.argv)

win = QWidget()
win.setWindowTitle('MDBrowser')




# open url
opener = urllib2.build_opener()
req=urllib2.Request("http://pantoff0l.nl:8080", data=None, headers={'Content-Type': 'text/markdown'})
response = opener.open(req)
md=response.read()

# parse markdown
html = markdown(md)

# add stylesheet
html += "<link href='https://gist.githubusercontent.com/tuzz/3331384/raw/d1771755a3e26b039bff217d510ee558a8a1e47d/github.css' rel='stylesheet' type='text/css'>"

# render markdown
browser = QWebView()
browser.setHtml(html)
#browser.load(QUrl(sys.argv[1]))
browser.show()

app.exec_()
'''
class TabDialog(object):
    def setupUi(self, Dialog):
        tab1 = QtGui.QWidget()
        tab2 = QtGui.QWidget()

        vBoxlayout = QtGui.QVBoxLayout()



class BrowserDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("MDBrowser")
        Dialog.resize(1024, 768)
	 
	self.layout =  QtGui.QVBoxLayout()
	self.tabLayout = QtGui.QVBoxLayout()

        self.renderPage = QWebView()
        self.renderPage.setGeometry(QtCore.QRect(0, 200, 1020, 711))
        self.renderPage.setObjectName("renderPage")

        # Textbox
        self.urlBox = QtGui.QLineEdit()
        self.urlBox.setGeometry(QtCore.QRect(10, 20, 1000, 25))
        self.urlBox.setObjectName("urlBox")

	# Tabwidget
        self.tabs = QtGui.QTabWidget()
	self.tabs.setGeometry(QtCore.QRect(10, 30, 1000, 180))
	self.tab1 = QtGui.QWidget()

        self.tabLayout.addWidget(self.urlBox)
        self.tabLayout.addWidget(self.renderPage)
        self.tab1.setLayout(self.tabLayout)

	self.tabs.addTab(self.tab1,"Tab 1")
	
	self.layout.addWidget(self.tabs)

	Dialog.setLayout(self.layout)
 
        Dialog.setWindowTitle("MDBrowser")
 

class MDBrowser(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        QWebView.__init__(self)
        self.ui = BrowserDialog()
        self.ui.setupUi(self)
        self.ui.urlBox.returnPressed.connect(self.loadURL)
 
    def loadURL(self):
        address = str(self.ui.urlBox.text())
        opener = urllib2.build_opener()
        req=urllib2.Request(address, data=None, headers={'Content-Type': 'text/markdown'})
        response = opener.open(req)
        md=response.read()

        # parse markdown
        html = markdown(md)

        # add stylesheet
        html += "<link href='https://gist.githubusercontent.com/tuzz/3331384/raw/d1771755a3e26b039bff217d510ee558a8a1e47d/github.css' rel='stylesheet' type='text/css'>"

        self.ui.renderPage.setHtml(html)
        self.ui.renderPage.show()


        #url = self.ui.urlBox.text()
        #self.ui.qwebview.load(QUrl(url))
        #self.show()  
        #self.ui.lineEdit.setText("")


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MDBrowser()
    #myapp.ui.renderPage.load(QUrl('http://www.appels.nl'))
    myapp.show()
    sys.exit(app.exec_())
