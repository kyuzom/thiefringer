#!/usr/bin/env python
'''
ThiefRinger alarm system - Onion Omega specific python package, motion detection, SMS notification.
'''
from __future__ import print_function
import signal
import sys
import os
import argparse
import json
import threading
try:
	from Queue import Queue
except (ImportError, ModuleNotFoundError):
	from queue import Queue
import onionGpio
import gpydem

class ThiefRinger(object):
	'''
	ThiefRinger alarm object.
	'''
	def __init__(self, opt):
		self.opt = opt
		with open(self.opt.config, 'r') as f:
			config = json.load(f)
		self.main_ctl = threading.Event()
		self.thread_ctl = threading.Event()
		self.thread_msgq = Queue()
		self.threads = []
		# setup OS signal handlers
		signal.signal(signal.SIGINT, self.signal_terminate)
		signal.signal(signal.SIGTERM, self.signal_terminate)
		#signal.signal(signal.SIGKILL, self.signal_terminate)
		# config defaults
		self.cfg_PIR = config.get('PIR', {})
		self.cfg_GSM = config.get('GSM', {})

	def run(self):
		'''
		Run alarm system main loop - blocking.
		Start alarm system, wait for external signal, stop alarm system.
		'''
		if self.opt.verbose:
			print('run')
		self.stop_threads()
		self.start_threads()
		while not self.main_ctl.wait(1.0):
			pass
		self.stop_threads()

	def terminate(self):
		'''
		Terminate alarm system main loop - nonblocking.
		'''
		if self.opt.verbose:
			print('terminate')
		self.main_ctl.set()

	def signal_terminate(self, *args):
		'''
		Catch process exit signals.
		@param *args: [list] List of additional arguments
		'''
		if self.opt.verbose:
			print('signal_terminate')
		self.terminate()

	def start_threads(self):
		'''
		Start alarm system - nonblocking.
		'''
		if self.opt.verbose:
			print('start_threads')
		self.thread_ctl.clear()
		self.thread_msgq = Queue()#self.thread_msgq.clear()
		self.threads = [
			threading.Thread(target=self.PIR_motion, args=(self.cfg_PIR, self.thread_ctl, self.thread_msgq), name='PIR_motion'),
			threading.Thread(target=self.GSM_modem,  args=(self.cfg_GSM, self.thread_ctl, self.thread_msgq), name='GSM_modem')
		]
		self.threads.append(
			threading.Thread(target=self.thread_heartbeat, args=(self.threads, self.thread_ctl))
		)
		if self.opt.verbose:
			print('num of threads: %d' % len(self.threads))
		for t in self.threads:
			t.start()

	def stop_threads(self):
		'''
		Stop alarm system - nonblocking.
		'''
		if self.opt.verbose:
			print('stop_threads')
		self.thread_ctl.set()
		self.thread_msgq.join()	# wait until all alarms are sent
		for t in self.threads:
			t.join()

	def PIR_motion(self, cfg, ctl, msgq):
		'''
		PIR motion detector main loop.
		@param cfg: [dict] Configurations
		@param ctl: [object] Threading control object (Event)
		@param msgq: [object] Message Queue
		'''
		if self.opt.verbose:
			print('PIR_motion')
		# config defaults
		cfg_pin = cfg.get('pin', -1)
		cfg_active_value = cfg.get('active_value', '0')
		cfg_alarm = cfg.get('alarm', {})
		cfg_alarm_number = cfg_alarm.get('number', '')
		cfg_alarm_message = cfg_alarm.get('message', 'ALERT')
		if sys.version_info[0] == 2:
			cfg_alarm_number = str(cfg_alarm_number)
			cfg_alarm_message = str(cfg_alarm_message)
		# PIR motion detector GPIO pin init
		gpio = onionGpio.OnionGpio(cfg_pin)
		if gpio.setInputDirection():
			raise RuntimeError("Could not set GPIO direction to input!")
		prev_value = '0' if cfg_active_value == '1' else '1'
		# infinite loop
		while not ctl.wait(0.1):
			value = gpio.getValue().strip()
			if prev_value != value:
				if value == cfg_active_value:
					if self.opt.verbose:
						print("PIR_motion ALERT: motion detected!")
					msgq.put((cfg_alarm_number, cfg_alarm_message), block=True, timeout=1.0)
				prev_value = value
		if self.opt.verbose:
			print('PIR_motion exit')

	def GSM_modem(self, cfg, ctl, msgq):
		'''
		GSM 3G USB modem main loop.
		@param cfg: [dict] Configurations
		@param ctl: [object] Threading control object (Event)
		@param msgq: [object] Message Queue
		'''
		if self.opt.verbose:
			print('GSM_modem')
		# config defaults
		cfg_modem_type = cfg.get('modem_type', '')
		cfg_dev_id = cfg.get('dev_id', '/dev/ttyS0')
		cfg_baudrate = cfg.get('baudrate', 9600)
		cfg_PIN = cfg.get('PIN', '')
		cfg_re_timeout = cfg.get('re_timeout', 1.0)
		# GSM 3G USB modem serial port init
		gsm = gpydem.Modem.get(cfg_modem_type, cfg_dev_id, baudrate=cfg_baudrate, PIN=cfg_PIN, re_timeout=cfg_re_timeout)
		# infinite loop
		while not ctl.wait(1.0):
			if not msgq.empty():
				number, message = msgq.get(block=True, timeout=1.0)
				msgq.task_done()
				if self.opt.verbose:
					print('GSM_modem sending SMS: {0}, {1}'.format(number, message))
				gsm.sendSMS(number, message)
				if self.opt.verbose:
					print('GSM_modem SMS sent.')
		if self.opt.verbose:
			print('GSM_modem exit')

	def thread_heartbeat(self, threads, ctl):
		'''
		Thread heartbeat main loop.
		@param threads: [list] Threads to check periodically
		@param ctl: [object] Threading control object (Event)
		'''
		if self.opt.verbose:
			print('thread_heartbeat')
		# infinite loop
		while not ctl.wait(1.0):
			for t in threads:
				if not t.is_alive():
					print('Thread {0} is dead! See previous messages for more details.'.format(t.name), file=sys.stderr)
					self.terminate()
		if self.opt.verbose:
			print('thread_heartbeat exit')

def main():
	'''
	Main ThiefRinger function.
	'''
	arg_parser = argparse.ArgumentParser(description='ThiefRinger alarm system.')
	arg_parser.add_argument('-c', '--config',  type=str, default=os.path.join(os.path.abspath(os.path.dirname(__file__)), '.thiefringer.json'), help='Config file')
	arg_parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity')
	opt = arg_parser.parse_args()
	try:
		alarm = ThiefRinger(opt)
		rc = alarm.run()
	except KeyboardInterrupt:
		alarm.terminate()
	except Exception as e:
		print(str(e), file=sys.stderr)
		print("\033[91mUnexpected error happened! Please see the details above.\033[0m", file=sys.stderr)
		sys.exit(1)
	else:
		sys.exit(rc)

if __name__ == '__main__':
	main()
