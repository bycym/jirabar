######################################################################
# Author : Aaron Benkoczy
######################################################################

import os
import os.path
import re
import jira_issues

import time
import threading
import queue
import webbrowser       
import datetime


# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import qdarkstyle

WAIT_TIME=10*60  # 10 minutes wait
CACHE_FILE="jira_noti.cache"
WINDOWS_OPACITY=0.7


class ExtendedComboBox(QComboBox):
  def __init__(self, parent=None):
    super(ExtendedComboBox, self).__init__(parent)

    self.setFocusPolicy(Qt.StrongFocus)
    self.setEditable(True)

    # add a filter model to filter matching items
    self.pFilterModel = QSortFilterProxyModel(self)
    self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
    self.pFilterModel.setSourceModel(self.model())

    # add a completer, which uses the filter model
    self.completer = QCompleter(self.pFilterModel, self)
    # always show all (filtered) completions
    self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
    self.setCompleter(self.completer)

    # connect signals
    self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
    self.completer.activated.connect(self.on_completer_activated)


  # on selection of an item from the completer, select the corresponding item from combobox 
  def on_completer_activated(self, text):
    if text:
      index = self.findText(text)
      self.setCurrentIndex(index)
      self.activated[str].emit(self.itemText(index))


  # on model change, update the models of the filter and completer as well 
  def setModel(self, model):
    super(ExtendedComboBox, self).setModel(model)
    self.pFilterModel.setSourceModel(model)
    self.completer.setModel(self.pFilterModel)


  # on model column change, update the model column of the filter and completer as well
  def setModelColumn(self, column):
    self.completer.setCompletionColumn(column)
    self.pFilterModel.setFilterKeyColumn(column)
    super(ExtendedComboBox, self).setModelColumn(column)  



class GuiPart(QMainWindow):
  def __init__(self, master, queue, endCommand):
    self.queue = queue
    self.endCommand = endCommand;
    
    super().__init__()

    # setting title
    self.setWindowTitle("Python ")

    self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)


    ## change alpha of the tool
    self.setWindowOpacity(WINDOWS_OPACITY)

    ### dark mod ################################################
    # setup stylesheet
    self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # or in new API
    self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    #################################################################

    # setting geometry
    screenSize = (master.primaryScreen().size().width())
    appSize = 600
    self.setGeometry(round(screenSize/2 - appSize/2, 0), 0, int(appSize), 30)

    # calling method
    self.UiComponents()
    
    # showing all the widgets
    self.show()

  def closeEvent(self, event):
    print("closeEvent")
    print( "User has clicked the red x on the main window")
    self.endCommand()
    self.running = 0
    # event.accept()
    QCoreApplication.quit()

      # method for widgets
  def UiComponents(self):
    print("UiComponents")


    self.button1 = QPushButton(self)
    self.button1.setText("X")
    self.button1.move(0,0)
    self.button1.setGeometry(0,0,30,30)
    self.button1.clicked.connect(self.closeEvent)
    # creating a combo box widget
    self.combo_box = ExtendedComboBox(self)

    # setting geometry of combo box
    self.combo_box.setGeometry(30, 0, 570, 30)
    self.combo_box.setFocusPolicy(Qt.StrongFocus)      
    self.combo_box.setFocus()

    self.addCacheItems()

    # creating a editable combo box
    self.combo_box.setEditable(True)

    shortcut = QShortcut(QKeySequence(Qt.Key_Return), self.combo_box, activated=self.onActivated)


  def addCacheItems(self):
    print("addCacheItems")

    if not os.path.isfile(CACHE_FILE):
      with open(CACHE_FILE, 'w'): pass

    with open(CACHE_FILE, "r") as f:
      stored_issues = f.read()
    if(len(stored_issues) > 0):
      contentList = stored_issues.split("\n")
      for i, line in enumerate(contentList):
        self.combo_box.addItem(line)
    else:
      self.combo_box.addItem("No jira issue (no cache) Connection error!!")

  # hit enter
  def onActivated(self):
    print("onActivated")
    line = str(self.combo_box.currentText())
    link=""
    if (re.search("href=", line)):
      issue_text = line[0:line.find("|")]
      link = line[line.find("=")+1:len(line)]
    if (len(link) > 0):
      print ("===============================================================")
      print (link)
      webbrowser.open_new(link)
      print ("===============================================================")


  def processIncoming(self):
    print("processIncoming")
    # Handle all messages currently in the queue, if any.
    while self.queue.qsize(  ):
      try:
        issues = self.queue.get(0)
        self.RefreshCombobox(issues)
      except queue.Empty:
        pass

    logFile = ""

  def RefreshCombobox(self,content):
    print("RefreshCombobox")
    self.combo_box.clear()
    self.GetData(content)

  def GetData(self, content):
    print("GetData")
    contentList = content.split("\n")

    # iterate throu the splitted elements
    for i, line in enumerate(contentList):
      self.combo_box.addItem(line)



class ThreadedClient:
  def __init__(self, master):
    self.master = master

    # Create the queue
    self.queue = queue.Queue(  )

    # Set up the GUI part
    self.gui = GuiPart(master, self.queue, self.endApplication)

    # Set up the thread to do asynchronous I/O
    # More threads can also be created and used, if necessary
    self.running = 1
    self.thread1 = threading.Thread(target=self.workerThread1)
    self.thread1.start(  )

    self.timer = QTimer()
    self.timer.setInterval(10000)
    self.timer.timeout.connect(self.periodicCall)
    self.timer.start()

  def periodicCall(self):
    print("periodicCall")
    self.gui.processIncoming(  )
    if not self.running:
      import sys
      self.timer.stop()
      self.thread1.exit()
      sys.exit(1)
      

  def workerThread1(self):
    print("workerThread1")
    while self.running:
      print(">> start call >> ", datetime.datetime.now())
      issues = jira_issues.getParsedIssues()
      self.queue.put(issues)
      print("<< end << ", datetime.datetime.now())
      time.sleep(WAIT_TIME)

  def endApplication(self):
    print("endApplication")
    self.running = 0
    import sys
    self.timer.stop()
    self.exit(0)
    sys.exit(1)

if __name__ == "__main__":

    App = QApplication(sys.argv)
    myapp = ThreadedClient(App)
    # myapp.show()
    ret = App.exec_()
    sys.exit(ret)