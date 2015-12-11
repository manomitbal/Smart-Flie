
import time
import sys
from threading import Thread
import logging

sys.path.append("../lib")
import cflib  # noqa
from cflib.crazyflie import Crazyflie  # noqa
import socket

TCP_IP = '192.168.2.23'#'192.168.2.8'
TCP_PORT = 1989
BUFFER_SIZE = 20  # Normally 1024, but we want fast response



# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2014 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.

"""
Simple example that connects to the first Crazyflie found, logs the Stabilizer
and prints it to the console. After 10s the application disconnects and exits.
"""

import sys
sys.path.append("../lib")

import cflib.crtp

import logging
import time
#from time import *
from threading import Timer

import collections

import random

import math

import cflib.crtp
from cfclient.utils.logconfigreader import LogConfig
from cflib.crazyflie import Crazyflie

import numpy 
from numpy import *


import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class LoggingExample:
	

	
	"""
	Simple logging example class that logs the Stabilizer from a supplied
	link uri and disconnects after 5s.
	"""
	def __init__(self, link_uri,results, size=(600,500)):
		self.thrust_mult = 1
		self.thrust_step = 500
		self.thrust = 20000
		self.pitch = 0
		self.roll = 0
		self.yawrate = 0 

		""" Initialize and run the example with the specified link_uri """
		#self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.s.setblocking(0)
		#self.s.bind((TCP_IP, TCP_PORT))
		# Create a Crazyflie object without specifying any cache dirs
		self._cf = Crazyflie()
		print "Result test: ",results
		# Connect some callbacks from the Crazyflie API
		self._cf.connected.add_callback(self._connected)
		self._cf.disconnected.add_callback(self._disconnected)
		self._cf.connection_failed.add_callback(self._connection_failed)
		self._cf.connection_lost.add_callback(self._connection_lost)

		print "Connecting to %s" % link_uri

		# Try to connect to the Crazyflie
		self._cf.open_link(link_uri)

		# Variable used to keep main loop occupied until disconnect
		self.is_connected = True
		# Unlock startup thrust protection
		self._cf.commander.send_setpoint(0, 0, 0, 0)

		self.app = QtGui.QApplication([])
		self.interval = int(0.1*1000)
		self.bufsize = 60
		self.databuffer = collections.deque([0,0]*self.bufsize, self.bufsize)
		self.x = [0.0 , 1.0]#linspace(0,1000,60)
		
		self.y = zeros(self.bufsize, dtype=float)
		
		self.plt = pg.plot(title = 'Real Time Sensor Evaluation')
		self.plt.resize(*size)
		self.plt.showGrid(x=True, y=True)
		#self.plt.setYRange(-20,30, padding = 0)
		self.curve = self.plt.plot(self.x,results,pen=(255,0,0))
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateplot)
		self.timer.start(0)

	def _connected(self, link_uri):
		""" This callback is called form the Crazyflie API when a Crazyflie
		has been connected and the TOCs have been downloaded."""
		print "Connected to %s" % link_uri

		# The definition of the logconfig can be made before connecting
		#changed
		#self._lg_stab = LogConfig(name="Stabilizer", period_in_ms=10)
		#self._lg_stab.add_variable("stabilizer.roll", "float")
		#self._lg_stab.add_variable("stabilizer.pitch", "float")
		#self._lg_stab.add_variable("stabilizer.yaw", "float")
		
		self._lg_stab = LogConfig(name="mb", period_in_ms=10)
		self._lg_stab.add_variable("mb.distance", "float")

		# Adding the configuration cannot be done until a Crazyflie is
		# connected, since we need to check that the variables we
		# would like to log are in the TOC.
		self._cf.log.add_config(self._lg_stab)
		if self._lg_stab.valid:
			# This callback will receive the data
			self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
			# This callback will be called on errors
			self._lg_stab.error_cb.add_callback(self._stab_log_error)
			# Start the logging
			self._lg_stab.start()
		else:
			print("Could not add logconfig since some variables are not in TOC")

		# Start a timer to disconnect in 10s
		t = Timer(1000000, self._cf.close_link)
		t.start()

	def _stab_log_error(self, logconf, msg):
		"""Callback from the log API when an error occurs"""
		print "Error when logging %s: %s" % (logconf.name, msg)
	def serv_listen(self):
		self.s.listen(1) 
		self.conn, self.addr = self.s.accept()
		self.data_buff = sel
		f.conn.recv(BUFFER_SIZE)
		#print self.data_buff
		return self.data_buff

	def updateplot(self):
		#self.databuffer.append(results)
		#self.y[:] = self.databuffer
		#self.y.append(data)
		results_plot = resultspyqt[-500:]
		x_plot = self.x[-500:]
		self.plt.setYRange(-30,30, padding = 0)
		self.curve.setData(x_plot,results_plot)
		self.app.processEvents() 

	def getdata(data):
		str1=data['mb.distance']
		num1=float(str1)
		num1=30-num1
		return num1

	def _stab_log_data(self, timestamp, data, logconf):
		"""Callback froma the log API when data arrives"""
		#print strftime("%H:%M:%S ", gmtime())
		str1=data['mb.distance']
		num1=float(str1)
		num1=30-num1

		#self.updateplot(num1)
		#print "test: ",num1
		#self.databuffer.append(num1)
		#self.y[:] = self.databuffer
		#self.curve.setData(x,num1)
		#self.app.processEvents()

		results.append(num1)
		resultspyqt.append(num1)
		self.x = list(range(0,len(resultspyqt)))
		
		
		
		print "[%d][%s]: %s" % (timestamp, logconf.name, data)
		
		#if not data: break
		data=self.serv_listen()
		if data>0:
			print "app: ",data
			if(int(data)<100):#we are in thrust
				print "thrust"
				print self.roll, self.pitch, self.yawrate, self.thrust 
				self.thrust=int(data)*600
				self._cf.commander.send_setpoint(self.roll, self.pitch, self.yawrate, self.thrust)
				#time.sleep(0.1)
			elif((int(data)>100)and(int(data)<200)):#we are in pitch
				print roll, pitch, yawrate, thrust 
				pitch=(int(data))/5-30
				self._cf.commander.send_setpoint(roll, (int(data))/5-30, yawrate, thrust)
				#time.sleep(0.1)
			elif(int(data)>200):#we are in roll
				print "add roll: ",150-(int(data))*3/5
				print roll, pitch, yawrate, thrust 
				roll=50-(int(data))/5
				self._cf.commander.send_setpoint(50-(int(data))/5, pitch, yawrate, thrust)
				#time.sleep(0.1)   
		if data == 'Hover':
			print "app: ",data
					

	def _connection_failed(self, link_uri, msg):
		"""Callback when connection initial connection fails (i.e no Crazyflie
		at the speficied address)"""
		print "Connection to %s failed: %s" % (link_uri, msg)
		self.is_connected = False

	def _connection_lost(self, link_uri, msg):
		"""Callback when disconnected after a connection has been made (i.e
		Crazyflie moves out of range)"""
		print "Connection to %s lost: %s" % (link_uri, msg)
		#print results

	def _disconnected(self, link_uri):
		"""Callback when the Crazyflie is disconnected (called in all cases)"""
		print "Disconnected from %s" % link_uri
		self.is_connected = False
		#print results

	def run(self):
		self.app.exec_()

if __name__ == '__main__':
	results=[0.,0.]
	resultspyqt=[0.,0.]
	print results
	# Initialize the low-level drivers (don't list the debug drivers)
	cflib.crtp.init_drivers(enable_debug_driver=False)
	# Scan for Crazyflies and use the first one found
	
	print "Scanning interfaces for Crazyflies..."
	available = cflib.crtp.scan_interfaces()
	print "Crazyflies found:"
	for i in available:
		print i[0]

	if len(available) > 0: 
		le = LoggingExample(available[0][0],results)
		le.run()
	else:
		print "No Crazyflies found, cannot run example"

	# The Crazyflie lib doesn't contain anything to keep the application alive,
	# so this is where your application should do something. In our case we
	# are just waiting until we are disconnected.
	#while le.is_connected:
	#	time.sleep(1)
	#print results, "done"  
 	
 	#m.run()
    
	fig = plt.figure()
	plt.plot(results)
	plt.show()
	

