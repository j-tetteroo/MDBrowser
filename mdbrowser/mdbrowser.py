#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys

from PyQt4.QtWebKit import QWebView
from PyQt4.QtGui import QApplication
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QUrl
from PyQt4 import QtCore
from markdown import markdown
import urllib2


class TabDialog(QtGui.QWidget):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self, parent)

        self.layout = QtGui.QVBoxLayout()

	# webview
	self.renderPage = QWebView()
        self.renderPage.setObjectName("renderPage")

        # Textbox
        self.urlBox = QtGui.QLineEdit()
        self.urlBox.setObjectName("urlBox")

	# Set layout
        self.layout.addWidget(self.urlBox)
	self.layout.addWidget(self.renderPage)
        self.setLayout(self.layout)

	# event handler
        self.urlBox.returnPressed.connect(self.loadURL)
	stylesheet = """ 
	    QWebView {
	    border-top-left-radius: 40px;
		    border-top-right-radius: 40px;
	    }
	    """

	self.renderPage.setStyleSheet(stylesheet) 



    def loadURL(self):
        address = str(self.urlBox.text())
        opener = urllib2.build_opener()
        req=urllib2.Request(address, data=None, headers={'Content-Type': 'text/markdown'})
        response = opener.open(req)
        md=response.read()

        # parse markdown
        html = markdown(md)

        # add stylesheet
        html += "<link href='https://gist.githubusercontent.com/tuzz/3331384/raw/d1771755a3e26b039bff217d510ee558a8a1e47d/github.css' rel='stylesheet' type='text/css'>" 
        #html += "<link href='file:///home/jt/MDBrowser/mdbrowser/github.css' rel='stylesheet' type='text/css'>"

        self.renderPage.setHtml(html)
        self.renderPage.show()



class TabAddButton(QtGui.QWidget):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self, parent)





class BrowserDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("MDBrowser")
        Dialog.resize(1024, 768)
	 
	self.layout =  QtGui.QVBoxLayout()

	# Tabwidget
        self.tabs = QtGui.QTabWidget()
	self.tabs.setGeometry(QtCore.QRect(10, 30, 1000, 180))
        self.tabs.setTabsClosable(True)
	self.tab1 = QtGui.QWidget()

        self.tab1 = TabDialog()
	self.tab2 = TabDialog()
        self.tabAddButton = TabAddButton()
        self.tabAddButton.setObjectName("addButton")

	self.tabs.addTab(self.tab1,"Tab 1")
        self.tabs.addTab(self.tab2,"Tab 2")
        self.tabs.addTab(self.tabAddButton, "+")

	# disable close button on addtab button
        self.tabs.tabBar().setTabButton(2, QtGui.QTabBar.RightSide,None)

	# layout	
	self.layout.addWidget(self.tabs)

	Dialog.setLayout(self.layout)
 
        Dialog.setWindowTitle("MDBrowser")

	# event handler
	self.tabs.currentChanged.connect(self.handleTabChange)
        self.tabs.tabCloseRequested.connect(self.handleClose)

	# add button stylesheet
	stylesheet = """ 
	    QTabBar::tab:last {
		    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.0 #c1e1f5, stop: 1.0 #8fcaee);
		    border: 1px solid #73bde9;
		    border-top-left-radius: 4px;
		    border-top-right-radius: 4px;
		    padding-left: 10px;
                    padding-right: 10px;
		    margin-left: 3px;
                    bottom: -3px;
	    }
	    """

	self.tabs.setStyleSheet(stylesheet) 

    # handle added tab button
    def handleTabChange(self, index):
        maxIndex = max(0, self.tabs.count()-1)
        if (index == maxIndex):
            tabNew = TabDialog()
	    self.tabs.insertTab(maxIndex, tabNew, "Tab " + str(maxIndex+1))
            self.tabs.setCurrentIndex(maxIndex)

    # handle tab close
    def handleClose(self, index):
        maxIndex = max(0, self.tabs.count()-1)
        if (index < maxIndex):
            if (self.tabs.count() == 2):
                return
            if (self.tabs.currentIndex() == index):
                self.tabs.setCurrentIndex(index-1)
                self.tabs.removeTab(index)
            else:
                self.tabs.widget(index).deleteLater()
                self.tabs.removeTab(index)


 

class MDBrowser(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        QWebView.__init__(self)
        self.ui = BrowserDialog()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MDBrowser()
    #myapp.ui.renderPage.load(QUrl('http://www.appels.nl'))
    myapp.show()
    sys.exit(app.exec_())
