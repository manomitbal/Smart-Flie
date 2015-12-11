# Bitcraze code from https://github.com/bitcraze/crazyflie-clients-python/blob/develop/examples/basiclog.py

"""
Autonomously controls the CF with the purpose of makign it hover. Uses PIDs to balance the CF. 
"""

import sys
sys.path.append("../lib")

import cflib.crtp

import logging
import time
from threading import Timer

import cflib.crtp
from cfclient.utils.logconfigreader import LogConfig
from cflib.crazyflie import Crazyflie

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class Hover:
	"""
	This will both hover the CF and log/print data concerning the roll,pitch,yaw, etc.
	There are 3 separate PID functions to control: pitch, yaw, and roll. Eventually there will be a 4th to control height (or directly: thrust)
	"""

	def __init__(self, link_uri):
		""" The link_uri is the 'radio address' of the crazyflie """

		#All of the global variables needed for the PID functions
		self.rollsetpoint=0.0
		self.pitchsetpoint=0.0
		self.yawsetpoint=0.0
		self.altitudesetpoint= 20.0
		self.thrust=20000
		
		#Calculated errors
		self.iroll=0.0
		self.droll=0.0
		self.ipitch=0.0
		self.dpitch=0.0
		self.iyaw=0.0
		self.dyaw=0.0
		self.ialtitude=0.0
		self.daltitude=0.0
		
		#The last recorded timestamp (used for dt determination)
		self.lastTime=0
		self.lastRollError=0.0
		self.lastPitchError=0.0
		self.lastYawError=0.0
		self.lastAltitudeError=0.0
		
		#PID coefficients
		self.kp_roll=0.#1.5#1.75
		self.kp_pitch=0.#0.75#2.3#2.5
		self.kp_yaw=0.0
		self.kp_altitude=0.
		self.ki_yaw=0.0
		self.ki_roll=0.0
		self.ki_pitch=0.0#0.000005#0.00000012
		self.ki_altitude=0.0
		self.kd_roll=0.0
		self.kd_pitch=0.0
		self.kd_altitude=0.0
		self.lastVal=7.0

		
		# Create a Crazyflie object
		self._cf = Crazyflie()

		# Connect some callbacks from the Crazyflie API
		self._cf.connected.add_callback(self._connected)
		self._cf.disconnected.add_callback(self._disconnected)
		self._cf.connection_failed.add_callback(self._connection_failed)
		self._cf.connection_lost.add_callback(self._connection_lost)

		print "Connecting to %s" % link_uri

		# Connect to the Crazyflie
		self._cf.open_link(link_uri)

		# Variable used to keep main loop occupied until disconnect
		self.is_connected = True

	def _connected(self, link_uri):
		""" This callback is called form the Crazyflie API when a Crazyflie
		has been connected and the TOCs have been downloaded."""
		print "Connected to %s" % link_uri
		# The definition of the logconfig can be made before connecting
		self._lg_stab = LogConfig(name="HoverLog", period_in_ms=10)
		self._lg_stab.add_variable("stabilizer.pitch", "float")
		self._lg_stab.add_variable("stabilizer.roll","float")
		self._lg_stab.add_variable("stabilizer.yaw", "float")
		self._lg_stab.add_variable("stabilizer.thrust", "float")
		# self._lg_stab.add_variable("gyro.x","float")
		# self._lg_stab.add_variable("gyro.y","float")
		#self._lg_stab.add_variable("gyro.z","float")
		#self._lg_stab.add_variable("baro.aslLong","float")
		
		#self._lg_stab = LogConfig(name="mb", period_in_ms=10)
		self._lg_stab.add_variable("mb.distance","float")

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
		# Unlock startup thrust protection
		self._cf.commander.send_setpoint(0, 0, 0, 0)
		# Start a timer to disconnect the crazyflie in 25 seconds
		t = Timer(25,self._cf.close_link)
		t.start()

	def _stab_log_error(self, logconf, msg):
		"""Callback from the log API when an error occurs"""
		print "Error when logging %s: %s" % (logconf.name, msg)

	#The following is all of the PID functions. 
	#They have been adopted from the general form given in: 
	#"http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/" """


	def pid_roll(self,dataroll,dt):
	
		#Calculate the errors for p,i, and d
		error=self.rollsetpoint-dataroll
		self.iroll+=(error*dt)
		self.droll=(error-self.lastRollError)/dt

		#setup for next time
		self.lastRollError=error

		#return the pid value
		return self.kp_roll*error+self.ki_roll*self.iroll+self.kd_roll*self.droll
	
	def pid_pitch(self,datapitch,dt):
	
	#Calculate the errors for p,i, and d
		error=self.pitchsetpoint-datapitch
	
		self.ipitch+=(error*dt)
		self.dpitch=(error-self.lastPitchError)/dt

	#set up the last error for the next iteration
		self.lastPitchError=error

		#return the pid value
		return (self.kp_pitch*error+self.ki_pitch*self.ipitch+self.kd_pitch*self.dpitch)

	def pid_yaw(self,datayaw,dt):
	
	#Calculate the errors for p,i, and d
		error=self.yawsetpoint-datayaw
		self.iyaw+=(error*dt)
		self.dyaw=(error-self.lastYawError)/dt

	#set up the last error for the next iteration
		self.lastYawError=error

		#return the pid value
		return self.kp_yaw*error+self.ki_yaw*self.iyaw+0*self.dyaw

#Modification to replace Barometer with Sonar Range Finder and optimize thrust using that. 
	#def thrust_from_sonar(self,dataSonar):




#Based on the "target altitude" argument sent in from the console this is a PID loop based on that setpoint
	# def thrust_from_barometer(self,aslLong,dt):
	# """old  thrust formulation
	# base = int(sys.argv[1])
	# return 15000+(base-aslLong)*800
	# """
	# #Calculate the errors for p,i, and d
	# 	error=self.altitudesetpoint-aslLong
	# 	print "error: ",error
	# 	self.ialtitude+=(error*dt)
	# 	self.datitude=(error-self.lastAltitudeError)/dt

	# #set up the last error for the next iteration
	# 	self.lastAltitudeError=error

	# 	#return the pid value
	# 	if (((self.kp_altitude*error+self.ki_altitude*self.ialtitude+0*self.daltitude)*200+self.altitudesetpoint*1000)>60000):
	# 		return 55000
	# 	elif (((self.kp_altitude*error+self.ki_altitude*self.ialtitude+0*self.daltitude)*200+self.altitudesetpoint*1000)<20000):
	# 		return 25000
	# 	return (self.kp_altitude*error+self.ki_altitude*self.ialtitude+0*self.daltitude)*200+self.altitudesetpoint*1000

	def _stab_log_data(self, timestamp, data, logconf):
		"""Callback from the log API when data arrives."""
		
		#Print the log data
		print "[%d][%s]: %s" % (timestamp, logconf.name, data)
		#print self.pid_pitch(data['stabilizer.pitch'],dt)	
		#calculate the dt for this iteration. Should be close to 10ms
		now = timestamp
		dt = timestamp-self.lastTime
		print (self.altitudesetpoint-data['mb.distance'])*200+(self.altitudesetpoint*1000)+25000
		#set the controls of the CF
		if  (abs(self.altitudesetpoint-data['mb.distance'])>8):
		# and \
		# 	(self.lastVal>(((self.altitudesetpoint-data['mb.distance'])*200+(self.altitudesetpoint*1000)+25000)*0.8))and \
		# 	(self.lastVal>(((self.altitudesetpoint-data['mb.distance'])*200+(self.altitudesetpoint*1000)+25000)*0.8)):
			self.thrust=(self.altitudesetpoint-data['mb.distance'])*200+(self.altitudesetpoint*1000)+25000
		#lif (abs(self.altitudesetpoint-data['mb.distance'])>20):
			#self.thrust=(self.altitudesetpoint-data['mb.distance'])*300+(self.altitudesetpoint*1000)+25000

		self._cf.commander.send_setpoint(self.pid_roll(data['stabilizer.roll'],dt),-1*self.pid_pitch(data['stabilizer.pitch'],dt),
			self.pid_yaw(data['stabilizer.yaw'],dt),self.thrust)
		self.lastVal=self.thrust
		#set up the lastTime for the next iteration
		self.lastTime=now

	def _connection_failed(self, link_uri, msg):
		"""Callback when connection initial connection fails (i.e no Crazyflie
		at the speficied address)"""
		print "Connection to %s failed: %s" % (link_uri, msg)
		self.is_connected = False

	def _connection_lost(self, link_uri, msg):
		"""Callback when disconnected after a connection has been made (i.e
		Crazyflie moves out of range)"""
		print "Connection to %s lost: %s" % (link_uri, msg)

	def _disconnected(self, link_uri):
		"""Callback when the Crazyflie is disconnected (called in all cases)"""
		print "Disconnected from %s" % link_uri
		self.is_connected = False

if __name__ == '__main__':
	# Initialize the low-level drivers (don't list the debug drivers)
	cflib.crtp.init_drivers(enable_debug_driver=False)
	# Scan for Crazyflies and use the first one found
	print "Scanning interfaces for Crazyflies..."
	available = cflib.crtp.scan_interfaces()
	print "Crazyflies found:"
	for i in available:
		print i[0]

	if len(available) > 0:
		h = Hover(available[0][0])
	else:
		print "No Crazyflies found, cannot run example"

	# The Crazyflie lib doesn't contain anything to keep the application alive,
	# so this is where your application should do something. In this case we
	# are just waiting until we are disconnected.
	while h.is_connected:
		time.sleep(1)

