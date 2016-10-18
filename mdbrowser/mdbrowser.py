#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys

from PyQt4.QtWebKit import QWebView
from PyQt4.QtGui import QApplication, QSizePolicy
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QUrl
from PyQt4 import QtCore
import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from urlparse import urljoin, urlparse
import urllib2
import requests
import os
from requests_file import FileAdapter


class LocalPathExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {'path' : ['', 'absolute path']}
        super(LocalPathExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        extender = LocalPathExtender(md)
        extender.config = self.getConfigs()
        md.treeprocessors.add("localpathextender", extender, "_end")
        md.registerExtension(self)

class LocalPathExtender(Treeprocessor):
    def run(self, root):
        pictures = root.getiterator("img")
        for pic in pictures:
            if not (pic.attrib["src"].startswith('http://') or pic.attrib["src"].startswith('https://')):
		print "REPLACE!", pic.attrib["src"], urljoin(self.config["path"], pic.attrib["src"])
                pic.set("src", urljoin(self.config["path"], pic.attrib["src"]))


class ToolBar(QtGui.QWidget):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self, parent)

        self.layout = QtGui.QHBoxLayout()

	# Open file button
	self.openButton = QtGui.QPushButton("Open file...", self)
	#self.openButton.setMaximumWidth(30)
	self.openButton.setAutoDefault(False)

        # TOC button
	self.tocButton = QtGui.QPushButton("TOC", self)
	self.tocButton.setCheckable(True)
	self.tocButton.setAutoDefault(False)

        # combo box
	self.dialect = QtGui.QComboBox(self)
        self.dialect.addItem("Dialect: Standard markdown", None)
        self.dialect.addItem("Dialect: Github flavour", None)

	self.layout.addWidget(self.openButton)
	self.layout.addWidget(self.tocButton)
        self.layout.addWidget(self.dialect)
	self.layout.setMargin(3)
	self.layout.setSpacing(3)
	self.setLayout(self.layout)


class UrlBar(QtGui.QWidget):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self, parent)

        self.layout = QtGui.QHBoxLayout()

	# Back/Forward button
	self.backButton = QtGui.QPushButton("<", self)
	self.backButton.setMaximumWidth(30)
	self.backButton.setAutoDefault(False)
	self.forwardButton = QtGui.QPushButton(">", self)
	self.forwardButton.setMaximumWidth(30)
	self.forwardButton.setAutoDefault(False)

	# reload button
	self.reloadButton = QtGui.QPushButton("R", self)
	self.reloadButton.setAutoDefault(False)
	self.reloadButton.setMaximumWidth(30)

        # Textbox
        self.urlBox = QtGui.QLineEdit()
        self.urlBox.setObjectName("urlBox")
        self.urlBox.setPlaceholderText("Enter URL...")


	# Set layout
        self.layout.addWidget(self.backButton)
        self.layout.addWidget(self.forwardButton)
        self.layout.addWidget(self.reloadButton)
        self.layout.addWidget(self.urlBox)
	self.layout.setMargin(3)
	self.layout.setSpacing(3)
        self.setLayout(self.layout)
        


class TabDialog(QtGui.QWidget):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self, parent)

        self.layout = QtGui.QVBoxLayout()
        self.webViewLayout = QtGui.QVBoxLayout()

	self.frame = QtGui.QFrame()

        # page memory
        self.backwardqueue = []
        self.forwardqueue = []
        self.current = None

	# urlbar
        self.urlBar = UrlBar(self)
        self.urlBar.setObjectName("urlBar")

	# toolbar
        self.toolBar = ToolBar(self)
        self.toolBar.setObjectName("toolBar")

	# webview
	self.renderPage = QWebView(self)
        self.renderPage.setObjectName("renderPage")
        self.renderPage.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

	# Set layout
        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.urlBar)
        
        self.webViewLayout.addWidget(self.renderPage)
        self.frame.setLayout(self.webViewLayout)

        self.layout.addWidget(self.frame)
	self.layout.setMargin(3)
	self.layout.setSpacing(3)

        self.setLayout(self.layout)
	self.renderPage.setHtml("<h1 style='font-family: sans-serif'>Oh Hai</h1>")

	# event handler
        self.urlBar.urlBox.returnPressed.connect(self.goCurrent)
	self.urlBar.forwardButton.clicked.connect(self.goForward)
	self.urlBar.backButton.clicked.connect(self.goBackward)
        self.urlBar.reloadButton.clicked.connect(self.goReload)
        self.toolBar.openButton.clicked.connect(self.loadFile)
	stylesheet = """ 
	    QFrame {
	        background: #fff;	
		border: 1px solid #cccccc;
	        border-radius: 10px;
		margin: 0px;
                padding-top: 0px;
	    }
	    """

	self.frame.setStyleSheet(stylesheet)


    # load forward page
    def goForward(self):
	print "FORWARD"
        if self.forwardqueue:
            url = self.forwardqueue.pop()
            self.urlBar.urlBox.setText(url.geturl())

            self.backwardqueue.append(self.current)
            self.current = url

            self.loadUrl(url)

    # load backward page
    def goBackward(self):
        print "BACKWARD"
        if self.backwardqueue:
            url = self.backwardqueue.pop()
            self.urlBar.urlBox.setText(url.geturl())

            self.forwardqueue.append(self.current)
            self.current = url

            self.loadUrl(url)

    # reload current url
    def goReload(self):
	print "RELOAD"
	if (self.current != None):
            self.urlBar.urlBox.setText(self.current.geturl())
            self.loadUrl(self.current)

    # go to the current url in the urlbox
    def goCurrent(self):
        print "CURRENT" 
        parseUrl = urlparse(str(self.urlBar.urlBox.text()))
	print "GO!", parseUrl.geturl()

	if (self.current != None):
            if (parseUrl.geturl() != self.current.geturl()):
                self.backwardqueue.append(self.current)

	self.current = parseUrl
        self.loadUrl(parseUrl)


    def renderErrorPage(self, header, message):
        html = "<html><head><style>body { font-family: sans-serif; }</style></head><body>"
        html += "<h1>" + header + "</h1>"
        html += "<p>" + message + "</p></body></html>"
        print html
        return html
        

    # load a local file with a file dialog
    def loadFile(self):
        global currentFileDir
        fileDialog = QtGui.QFileDialog(self)
        fileDialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        fileDialog.setOption(0)
        filename = fileDialog.getOpenFileName(self, 'Open file', str(currentFileDir), "MD Files (*.md);;Text Files (*.txt);;All Files (*.*)")
        if len(filename) == 0:
            return

        # store new dir as open file base path
        currentFileDir = os.path.dirname(str(filename))

        filename = "file://" + str(filename)
        self.urlBar.urlBox.setText(filename)
        self.goCurrent()

        
    # load a file from url into renderpage
    def loadUrl(self, url):
	extender = LocalPathExtension(path=url.geturl())
	markdownParser = markdown.Markdown(extensions=[extender, 'markdown.extensions.toc'])

        address = url.geturl()

	session = requests.Session()
	session.mount('file://', FileAdapter())
        try:
            response = session.get(address, headers={'Content-Type': 'text/markdown'}, timeout=15)
 	    response.raise_for_status()
        except requests.exceptions.ConnectionError as e: 
            self.renderPage.setHtml(self.renderErrorPage("Connection Error", str(e.message)))
	except requests.exceptions.HTTPError as e:
            self.renderPage.setHtml(self.renderErrorPage("HTTP Error", str(e.message)))
	except requests.exceptions.ProxyError as e:
            self.renderPage.setHtml(self.renderErrorPage("Proxy Error", str(e.message)))
        except requests.exceptions.SSLError as e:
            self.renderPage.setHtml(self.renderErrorPage("SSL Error", str(e.message)))
        except requests.exceptions.Timeout as e:
            self.renderPage.setHtml(self.renderErrorPage("Timeout exceeded", str(e.message)))
        except requests.exceptions.ConnectTimeout as e:
            self.renderPage.setHtml(self.renderErrorPage("Connection Timeout", str(e.message)))
        except requests.exceptions.ReadTimeout as e:
            self.renderPage.setHtml(self.renderErrorPage("Read Timeout", str(e.message)))
        except requests.exceptions.URLRequired as e:
            self.renderPage.setHtml(self.renderErrorPage("URL Required", str(e.message)))
        except requests.exceptions.TooManyRedirects as e:
            self.renderPage.setHtml(self.renderErrorPage("Too Many Redirects", str(e.message))) 
        except requests.exceptions.RequestException as e:
            self.renderPage.setHtml(self.renderErrorPage("General Error", str(e.message)))
        else:
            html = markdownParser.convert(response.text)
            html += "<link href='https://gist.githubusercontent.com/tuzz/3331384/raw/d1771755a3e26b039bff217d510ee558a8a1e47d/github.css' rel='stylesheet' type='text/css'>"

            self.renderPage.setHtml(html)
            print(html)
        finally:
  	    session.close()
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
		self.tabs.widget(index).deleteLater()
                self.tabs.removeTab(index)
            else:
                self.tabs.widget(index).deleteLater()
                self.tabs.removeTab(index)


 

class MDBrowser(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        QWebView.__init__(self)

        global currentFileDir 
        currentFileDir = os.getcwd()

        self.ui = BrowserDialog()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MDBrowser()
    #myapp.ui.renderPage.load(QUrl('http://www.appels.nl'))
    myapp.show()
    sys.exit(app.exec_())
