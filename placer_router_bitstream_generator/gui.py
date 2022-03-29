import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import re
import ctypes
import execution_progress as ep
import oktane_bitstream_generator as obg

class Ide(QMainWindow):

    def __init__(self, parent = None):
        QMainWindow.__init__(self,parent)

        self.filename = ""
        
        self.initUI()

    def initToolbar(self):
        self.newAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\new.png"),"New",self)
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.setStatusTip("Create a new document from scratch.")
        self.newAction.triggered.connect(self.new)

        self.openAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\open.png"),"Open file",self)
        self.openAction.setStatusTip("Open existing document")
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.open)

        self.saveAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\save.png"),"Save",self)
        self.saveAction.setStatusTip("Save document")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.save)

        self.saveAsAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\save_as.png"),"SaveAs",self)
        self.saveAsAction.setStatusTip("Save As")
        self.saveAsAction.triggered.connect(self.save_as)

        self.cutAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\cut.png"),"Cut to clipboard",self)
        self.cutAction.setStatusTip("Delete and copy text to clipboard")
        self.cutAction.setShortcut("Ctrl+X")
        self.cutAction.triggered.connect(self.text.cut)

        self.copyAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\copy.png"),"Copy to clipboard",self)
        self.copyAction.setStatusTip("Copy text to clipboard")
        self.copyAction.setShortcut("Ctrl+C")
        self.copyAction.triggered.connect(self.text.copy)

        self.pasteAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\paste.png"),"Paste from clipboard",self)
        self.pasteAction.setStatusTip("Paste text from clipboard")
        self.pasteAction.setShortcut("Ctrl+V")
        self.pasteAction.triggered.connect(self.text.paste)

        self.undoAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\undo.png"),"Undo last action",self)
        self.undoAction.setStatusTip("Undo last action")
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(self.text.undo)

        self.redoAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\redo.png"),"Redo last undone thing",self)
        self.redoAction.setStatusTip("Redo last undone thing")
        self.redoAction.setShortcut("Ctrl+Y")
        self.redoAction.triggered.connect(self.text.redo)

        self.incSize = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\inc_font.png"),"Increase font size",self)
        self.incSize.setStatusTip("Increase font size")
        self.incSize.setShortcut("Ctrl+I")
        self.incSize.triggered.connect(self.inc_size)

        self.decSize = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\dec_font.png"),"Decrease font size",self)
        self.decSize.setStatusTip("Decrease font size")
        self.decSize.setShortcut("Ctrl+D")
        self.decSize.triggered.connect(self.dec_size)

        self.runAction = QAction(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\run.png"),"Run the code",self)
        self.runAction.setStatusTip("Run the code")
        self.runAction.setShortcut("Ctrl+R")
        self.runAction.triggered.connect(self.run)
        
        self.abtAction=QAction("About",self)
        self.abtAction.triggered.connect(self.about)

        self.toolbar = self.addToolBar("Options")
        self.toolbar.setMinimumSize(600,50)

        self.toolbar.addAction(self.newAction)
        self.toolbar.addAction(self.openAction)
        self.toolbar.addAction(self.saveAction)
        self.toolbar.addAction(self.saveAsAction)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.cutAction)
        self.toolbar.addAction(self.copyAction)
        self.toolbar.addAction(self.pasteAction)
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)

        self.toolbar.addAction(self.incSize)
        self.toolbar.addAction(self.decSize)
        self.toolbar.addSeparator()

        self.toolbar.addAction(self.runAction)

        # Makes the next toolbar appear underneath this one
        self.addToolBarBreak()
    
    def about(self):
        abt = QMessageBox(self)
        abt.setTextFormat(Qt.RichText)
        abt.setIconPixmap(QPixmap(r"D:\Oktane\placer_router_bitstream_generator\icons\dp.png"))
        abt.setWindowTitle("About")
        abt.setText("<br>Made by Skadoosh!<br>"+"<a href= 'https://github.com/Anvay-7'><center>Github</center><br/></a>")
        abt.setFont(self.font)
        abt.exec_()

    def inc_size(self):
        self.font_size +=2
        self.font.setPointSize(self.font_size)
        self.text.setFont( self.font )

    def dec_size(self):
        self.font_size -=2
        self.font.setPointSize(self.font_size)
        self.text.setFont( self.font )
        
    def stop_code_exec(self):  
        self.code_run_thd.quit()
        self.code_run_thd.wait()
        
    def run(self):     
        self.prgs_thd = QThread()
        # Step 3: Create a code_exec object
        self.exec_prgs = exec_prgs()
        # Step 4: Move exec_prgs to the thread
        self.exec_prgs.moveToThread(self.prgs_thd)
        # Step 5: Connect signals and slots
        self.prgs_thd.started.connect(self.exec_prgs.show_prog)
        self.exec_prgs.prog_exec_finished.connect(self.prgs_thd.quit)
        self.exec_prgs.prog_exec_finished.connect(self.exec_prgs.deleteLater)
        self.prgs_thd.finished.connect(self.prgs_thd.deleteLater)
        #self.exec_prgs.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.prgs_thd.start()
        
        
        # Step 2: Create a QThread object
        self.code_run_thd = QThread()
        # Step 3: Create a code_exec object
        self.code_exec = code_exec(self.exec_prgs,self.filename)
        # Step 4: Move code_exec to the thread
        self.code_exec.moveToThread(self.code_run_thd)
        # Step 5: Connect signals and slots
        self.code_run_thd.started.connect(self.code_exec.run_code)
        #self.code_exec.code_exec_finished.connect(self.stop_code_exec)
        self.code_exec.code_exec_finished.connect(self.code_run_thd.quit)
        self.code_exec.code_exec_finished.connect(self.code_exec.deleteLater)
        self.code_run_thd.finished.connect(self.code_run_thd.deleteLater)
        #self.code_exec.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.code_run_thd.start()  

    def initFormatbar(self):

        self.formatbar = self.addToolBar("Format")


    def initMenubar(self):

        menubar = self.menuBar()

        file = menubar.addMenu("File")
        edit = menubar.addMenu("Edit")
        run = menubar.addMenu("Run")
        menubar.addAction(self.abtAction)


        file.addAction(self.newAction)
        file.addAction(self.openAction)
        file.addAction(self.saveAction)


        edit.addAction(self.undoAction)
        edit.addAction(self.redoAction)
        edit.addAction(self.cutAction)
        edit.addAction(self.copyAction)
        edit.addAction(self.pasteAction)

        run.addAction(self.runAction)

    def initUI(self):

        self.font = QFont()
        self.font.setFamily( "Consolas" )
        self.font.setFixedPitch( True )
        self.font_size=15
        self.font.setPointSize(self.font_size)
        

        self.text = QTextEdit(self)
        self.text.setFont( self.font )
        self.text.insertPlainText("#Enter the AHDL code here...\n")
        #self.text.setStyleSheet("color: rgb(25, 176, 143);")
        _ = MyHighlighter( self.text)

        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        # Set the tab stop width to around 33 pixels which is
        # about 8 spaces
        self.text.setTabStopWidth(33)

        self.setCentralWidget(self.text)

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        # If the cursor position changes, call the function that displays
        # the line and column number
        self.text.cursorPositionChanged.connect(self.cursorPosition)

        # x and y coordinates on the screen, width, height
        self.setGeometry(100,100,1030,800)

        self.setWindowTitle("Oktane AHDL IDE")


        self.setWindowIcon(QIcon(r"D:\Oktane\placer_router_bitstream_generator\icons\code.png"))

    def new(self):
        spawn = Ide(self)
        spawn.show()

    def open(self):
        # Get filename and show only .writer files
        self.filename,_ = QFileDialog.getOpenFileName(self, 'Open File',".","(*.txt)")
        if self.filename:
            with open(self.filename,"rt") as file:
                self.text.setText(file.read())

    def save(self):
        # Only open dialog if there is no filename yet
        if not self.filename:
            self.filename,_ = QFileDialog.getSaveFileName(self, 'Save File')
        # Append extension if not there yet
        if not self.filename.endswith(".txt"):
            self.filename += ".txt"

        # We just store the contents of the text file along with the
        # format in html, which Qt does in a very nice way for us
        with open(self.filename,"wt") as file:
            file.write(self.text.toPlainText())

    def save_as(self):
        # Only open dialog if there is no filename yet
        filename,_ = QFileDialog.getSaveFileName(self, 'Save File')
        # Append extension if not there yet
        if not filename.endswith(".txt"):
            filename += ".txt"

        if not self.filename:
            self.filename=filename
            
        # We just store the contents of the text file along with the
        # format in html, which Qt does in a very nice way for us
        with open(filename,"wt") as file:
            file.write(self.text.toPlainText())

    def cursorPosition(self):

        cursor = self.text.textCursor()

        # Start indexing from 1
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()

        self.statusbar.showMessage("Line: {} | Column: {}".format(line,col))

class code_exec(QObject):
    code_exec_finished = pyqtSignal()
    
    def __init__(self,progress,file_name):
        super(code_exec,self).__init__()
        self.progress=progress
        self.file_name = file_name

    def run_code(self):
        """Long-running task."""

        obg.main(self.progress,self.file_name)
        
        self.progress.w.pg_bar.pg_bar_finished.emit()
        self.progress.prog_exec_finished.emit()
        self.code_exec_finished.emit()

class exec_prgs(QObject):
 
    prog_exec_finished = pyqtSignal()
    def __init__(self):
        super(exec_prgs,self).__init__()
        self.w=ep.Example()
            
    def show_prog(self):
        self.w.show()
        
class HighlightingRule():
    def __init__( self, pattern, format ):
        self.pattern = pattern
        self.format = format

class MyHighlighter( QSyntaxHighlighter ):
    def __init__( self, parent):
        QSyntaxHighlighter.__init__( self, parent )
        self.parent = parent
        keyword = QTextCharFormat()
        logical_operators = QTextCharFormat()
        port_assignment_operator = QTextCharFormat()
        brackets = QTextCharFormat()
        expr_assignment_operator = QTextCharFormat()
        number = QTextCharFormat()
        comment = QTextCharFormat()
        sync_async_operator = QTextCharFormat()
        ff_edge = QTextCharFormat()
        expr_inputs_1=QTextCharFormat()
        expr_inputs_2=QTextCharFormat()
        expr_output=QTextCharFormat()
        port_inputs_l=QTextCharFormat()
        port_inputs_r=QTextCharFormat()
        ports = QTextCharFormat()
        
        self.highlightingRules = []

        # keyword
        brush = QBrush( Qt.darkMagenta, Qt.SolidPattern )
        pattern =r"(MODE)"
        keyword.setForeground( brush )
        keyword.setBackground(Qt.yellow)
        keyword.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, keyword )
        self.highlightingRules.append( rule )
        
        #logical expr_assignment_operator
        brush = QBrush( Qt.green, Qt.SolidPattern )
        pattern = r"([\^&~|])" 
        logical_operators.setForeground( brush )
        logical_operators.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, logical_operators )
        self.highlightingRules.append( rule )
        
        # port assignment Operator
        brush = QBrush( Qt.red, Qt.SolidPattern )
        pattern = r"(-->)" 
        port_assignment_operator.setForeground( brush )
        port_assignment_operator.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, port_assignment_operator )
        self.highlightingRules.append( rule )
        
        # brackets
        brush = QBrush( Qt.darkGreen, Qt.SolidPattern )
        pattern = r"([\)\(]+|[\{\}]+|[][]+)" 
        brackets.setForeground( brush )
        brackets.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, brackets )
        self.highlightingRules.append( rule )
        
        # expression assignment Operator
        brush = QBrush( Qt.cyan, Qt.SolidPattern )
        pattern = r"(=)" 
        expr_assignment_operator.setForeground( brush )
        expr_assignment_operator.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, expr_assignment_operator )
        self.highlightingRules.append( rule )
        
        # number
        brush = QBrush( Qt.darkGray, Qt.SolidPattern )  
        pattern = r"(\b[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b)" 
        # pattern.setMinimal( True )
        number.setForeground( brush )
        number.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, number )
        self.highlightingRules.append( rule )
        
        # comment
        brush = QBrush( Qt.lightGray, Qt.SolidPattern )
        pattern = r"(#[^\n]*)" 
        comment.setForeground( brush )
        rule = HighlightingRule( pattern, comment )
        self.highlightingRules.append( rule )
        
        # sync_async_operator
        brush = QBrush( Qt.darkYellow, Qt.SolidPattern )
        pattern = r"(<)"
        sync_async_operator.setForeground( brush )
        sync_async_operator.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, sync_async_operator )
        self.highlightingRules.append( rule )
        
        # ff_edge
        brush= QBrush( Qt.darkRed, Qt.SolidPattern )
        pattern = r"(!)"
        # pattern.setMinimal( True )
        ff_edge.setForeground( brush )
        ff_edge.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, ff_edge )
        self.highlightingRules.append( rule )
        
        #expr_inputs_1
        brush= QBrush( Qt.darkMagenta, Qt.SolidPattern )
        pattern = r"[\^&~\(\)|=] *(\w+)"
        expr_inputs_1.setForeground( brush )
        expr_inputs_1.setFontItalic(True)
        rule = HighlightingRule( pattern, expr_inputs_1 )
        self.highlightingRules.append( rule )
        
        #expr_inputs_2
        brush= QBrush( Qt.darkBlue, Qt.SolidPattern )
        pattern = r"< *(\b\w+\b) *="
        # pattern.setMinimal( True )
        expr_inputs_2.setForeground( brush )
        expr_inputs_2.setFontWeight( QFont.Bold )
        expr_inputs_2.setFontItalic(True)
        rule = HighlightingRule( pattern, expr_inputs_2 )
        self.highlightingRules.append( rule )

        #expr_output
        brush= QBrush( Qt.darkGreen, Qt.SolidPattern )
        pattern = r"(?<!<)(\b\w+\b) *!?<? *\w* *="
        expr_output.setForeground( brush )
        rule = HighlightingRule( pattern, expr_output )
        self.highlightingRules.append( rule )
            
        #port_inputs_l
        brush= QBrush( Qt.darkCyan, Qt.SolidPattern )
        pattern = r"\b(\w+)\b *-->"
        port_inputs_l.setForeground( brush )
        port_inputs_l.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, port_inputs_l )
        self.highlightingRules.append( rule )   
                
        #port_inputs_r
        brush= QBrush( Qt.darkCyan, Qt.SolidPattern )
        pattern = r"--> *\b(\w+)\b"
        port_inputs_r.setForeground( brush )
        port_inputs_r.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, port_inputs_r )
        self.highlightingRules.append( rule )
        
        # ports
        brush = QBrush( Qt.blue, Qt.SolidPattern )
        pattern = r"\b(p\d{1,2})\b" 
        ports.setForeground( brush )
        ports.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, ports )
        self.highlightingRules.append( rule )

    def highlightBlock( self, text ):
        for rule in self.highlightingRules:
            expression=re.compile(rule.pattern)
            for match in re.finditer(expression, text):
                index = match.start(1)
                length = match.end(1) - index
                self.setFormat( index, length, rule.format )
        self.setCurrentBlockState( 0 )

def main():
    #needed to get icon working on windows taskbar
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary sync_async_operator
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QApplication(sys.argv)
    app.setStyleSheet(ep.StyleSheet)
    ide_window = Ide()
    ide_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
