import sys
from PyQt5.QtWidgets import (QApplication,
							 QWidget,
							 QLabel,
							 QGridLayout,
							 QAction,
							 QMainWindow,
							 QPushButton,
							 QMessageBox,
							 QFileDialog,
							 QSizePolicy)
from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import QCoreApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolBar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import reader
from scipy import signal
from numpy import fft, log10


class Example(QMainWindow):

	def __init__(self):
		super().__init__()
		self.interface = QWidget(
			self)  # grid layout don't working with QMainWindow, so I attached all buttons, labels, etc.. to @interface
		self.init_ui()

	def init_ui(self):
		self.statusBar().showMessage('Ready')
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')

		openFile = QAction('Open', self)
		openFile.setShortcut('Ctrl+O')
		openFile.setStatusTip('Load data')
		openFile.triggered.connect(self.load_file)
		fileMenu.addAction(openFile)

		# exitAction = QAction('&Quit', self)
		# exitAction.setShortcut('Ctrl+Q')
		# exitAction.triggered.connect(self.closeEvent)
		# exitAction.setStatusTip('Leave the program')
		# fileMenu.addAction(exitAction)

		helpMenu = menubar.addMenu('&Help')
		aboutAction = QAction('&About', self)
		aboutAction.setShortcut('F1')
		aboutAction.triggered.connect(self.on_about)
		aboutAction.setStatusTip('About the program')
		helpMenu.addAction(aboutAction)

		# ----------------------
		# setting the @interface
		# ----------------------
		self.setCentralWidget(self.interface)

		self.interface.load_btn = QPushButton('Load File', self.interface)
		self.interface.plot_btn = QPushButton('Plot data', self.interface)
		self.interface.topFileName = QLabel(self.interface)
		self.interface.dataLabel = QLabel(self.interface)
		self.interface.timeLabel = QLabel(self.interface)
		self.interface.vectorDraw_btn = QPushButton('Enable vector drowing', self.interface)
		self.interface.tempLabel = QLabel('Two selected points\' vector:	', self.interface)
		self.interface.detrend_btn = QPushButton('Plot detrended', self.interface)
		self.interface.FFT_btn = QPushButton('FFT All data', self.interface)

		self.grid = QGridLayout(self.interface)
		self.grid.setSpacing(5)
		self.grid.addWidget(self.interface.load_btn, 0, 0)
		self.grid.addWidget(self.interface.topFileName, 1, 0)
		self.grid.addWidget(self.interface.plot_btn, 2, 0)
		self.grid.addWidget(self.interface.dataLabel, 3, 0)
		self.grid.addWidget(self.interface.timeLabel, 4, 0)
		self.grid.addWidget(self.interface.vectorDraw_btn, 5, 0)
		self.grid.addWidget(self.interface.tempLabel, 6, 0)
		self.grid.addWidget(self.interface.detrend_btn, 7, 0)
		self.grid.addWidget(self.interface.FFT_btn, 8, 0)
		self.setLayout(self.grid)

		self.interface.plot_btn.clicked.connect(self.plot)
		self.interface.load_btn.clicked.connect(self.load_file)
		self.interface.vectorDraw_btn.clicked.connect(self.vdb)
		self.interface.detrend_btn.clicked.connect(self.detrend)
		self.interface.FFT_btn.clicked.connect(self.FFTWindow)

		self.setWindowTitle('ELF Data GUI')
		self.setWindowIcon(QIcon('icon.png'))
		self.show()

	def vdb(self):
		if self.interface.vectorDraw_btn.text() == 'Enable vector drowing':
			self.interface.vectorDraw_btn.setText('Disable vector drowing')
		else:
			self.interface.vectorDraw_btn.setText('Enable vector drowing')

	def detrend(self):
		if self.channel1_1:
			self.channel1_1 = signal.detrend(self.channel1_1)
			self.channel1_2 = signal.detrend(self.channel1_2)
			self.channel2_1 = signal.detrend(self.channel2_1)
			self.channel2_2 = signal.detrend(self.channel2_2)
			self.plot()

	def FFTWindow(self):
		sp11 = fft.fft(self.channel1_1)
		sp12 = fft.fft(self.channel1_2)
		freq1 = fft.fftfreq(len(self.channel1_1))
		sp21 = fft.fft(self.channel2_1)
		sp22 = fft.fft(self.channel2_2)
		freq2 = fft.fftfreq(len(self.channel2_1))
		plt.subplot(211)
		plt.grid(True)
		plt.plot(log10(sp11), color='red')
		plt.plot(log10(sp12))
		plt.subplot(212)
		plt.grid(True)
		plt.plot(log10(sp21), color='red')
		plt.plot(log10(sp22))
		plt.show()

	def closeEvent(self, event):  # it is template QWidget function
		reply = QMessageBox.question(self, 'Message',
									 "Are you sure to quit?",
									 QMessageBox.Yes | QMessageBox.No)
		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

	def load_file(self):
		self.interface.plot_btn.setText('Plot data')
		fname1 = QFileDialog.getOpenFileName(self, 'Load data')[0]
		if fname1:
			self.channel1_1, self.channel1_2, self.header1 = reader.read_data_from_file(fname1)
			fname1 = fname1.split('/')
			fname2 = fname1
			if fname1[-2] == '7':
					fname2[-2] = '10'
			else:
				fname2[-2] = '7'
			fname2 = '/'.join(fname2)
			self.channel2_1, self.channel2_2, self.header2 = reader.read_data_from_file(fname2)
			fname1 = fname1[-1]

			self.interface.topFileName.setText('Loaded data: <b>' + fname1 + '</b>. Rows: <b>'
											   + str(len(self.channel1_1)) + '/' + str(len(self.channel2_1)) + '</b>')
			self.interface.topFileName.resize(self.interface.topFileName.sizeHint())
			self.interface.dataLabel.setText('DATE: <b>' + fname1[:8] + '</b>')
			self.interface.dataLabel.resize(self.interface.dataLabel.sizeHint())
			self.interface.timeLabel.setText('TIME: <b>' + fname1[8:10] + ':' + fname1[10:12] + '</b>')
			self.interface.timeLabel.resize(self.interface.timeLabel.sizeHint())

	def plot(self):
		self.interface.tempLabel.setText('Two selected points\' vector:	')
		self.interface.plotToolBar = None
		self.interface.graph = PlotCanvas(self.channel1_1, self.channel1_2,
										  self.channel2_1, self.channel2_2,
										  self.header1, self.header2,
										  self.interface, width=16, height=12)
		self.interface.plotToolBar = NavigationToolBar(self.interface.graph, self.interface)
		self.grid.addWidget(self.interface.graph, 0, 1, 10, 1)
		self.grid.addWidget(self.interface.plotToolBar, 10, 1)
		self.interface.plot_btn.setText('Reset plot')

	def on_about(self):
		msg = """
v1.0.1
Now you can press and release mouse button to draw single vector on the figure
		"""
		QMessageBox.about(self, "About the ELF-gui", msg.strip())


class PlotCanvas(FigureCanvas):
	def __init__(self, channel1_1, channel1_2, channel2_1, channel2_2, header1, header2, parent=None, width=4, height=3, dpi=100):
		self.figure = Figure(figsize=(width, height), dpi=dpi)
		self.channel1_1 = channel1_1
		self.channel1_2 = channel1_2
		self.channel2_1 = channel2_1
		self.channel2_2 = channel2_2
		self.header1 = header1
		self.header2 = header2
		FigureCanvas.__init__(self, self.figure)
		self.mpl_connect('motion_notify_event', self.onMotion)
		self.mpl_connect('button_press_event', self.onPress)
		self.mpl_connect('button_release_event', self.onRelease)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.plot()

	def plot(self):
		x1 = []
		x2 = []
		if len(self.channel1_1) < 53000:
			for i in range(len(self.channel1_1)):
				x1.append((i)/175.95)
			for i in range(len(self.channel2_1)):
				x2.append((i)/887.7841)
		else:
			for i in range(len(self.channel1_1)):
				x1.append((i)/887.7841)
			for i in range(len(self.channel2_1)):
				x2.append((i)/175.95)

		self.ax1 = self.figure.add_subplot(211)
		self.ax1.clear()
		self.ax1.grid()
		self.ax1.plot(x1, self.channel1_1, color='red')
		self.ax1.plot(x1, self.channel1_2)
		self.ax2 = self.figure.add_subplot(212,  sharex=self.ax1)
		self.ax2.clear()
		self.ax2.grid()
		self.ax2.plot(x2, self.channel2_1, color='red')
		self.ax2.plot(x2, self.channel2_2)
		self.figure.tight_layout(pad=1.65)
		self.draw()

	def onMotion(self, event):
		self.parent().parent().statusBar().showMessage('%.6s, %.8s' %(event.xdata, event.ydata))

	def onPress(self, event):
		self.point1 = [event.xdata, event.ydata]
		if event.inaxes:
			self.checkedAxis = event.inaxes

	def onRelease(self, event):
		self.point2 = [event.xdata, event.ydata]
		if event.inaxes == self.checkedAxis:
			x_dist = self.point2[0] - self.point1[0]
			y_dist = self.point2[1] - self.point1[1]
			if self.parent().parent().interface.vectorDraw_btn.text() == 'Disable vector drowing':
				event.inaxes.plot([self.point1[0], self.point2[0]], [self.point1[1], self.point2[1]], 'm--')
				event.canvas.draw()
			self.parent().parent().interface.tempLabel.setText('Two selected points\' vector:	' + '%.6s, %.8s' %(x_dist, y_dist))



if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())