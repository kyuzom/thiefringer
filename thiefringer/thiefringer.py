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
import onionGpio

class ThiefRinger(object):
	'''
	ThiefRinger alarm object.
	'''
	def __init__(self, opt):
		self.opt = opt
		with open(self.opt.config, 'r') as f:
			self.config = json.load(f)
		self.main_ctl = threading.Event()
		self.thread_ctl = threading.Event()
		self.threads = []
		signal.signal(signal.SIGINT, self.signal_terminate)
		signal.signal(signal.SIGTERM, self.signal_terminate)
		#signal.signal(signal.SIGKILL, self.signal_terminate)

	def run(self):
		'''
		Run alarm system main loop - blocking.
		Start alarm system, wait for external signal, stop alarm system.
		'''
		if self.opt.verbose:
			print('run')
		self.stop_threads()
		self.main_ctl.clear()
		self.start_threads()
		while not self.main_ctl.wait(1):
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
		self.threads = [
			threading.Thread(target=self.detect_motion, args=(self.config.get('motion', {}), self.thread_ctl))
		]
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
		for t in self.threads:
			t.join()

	def detect_motion(self, cfg, ctl):
		'''
		Motion detection main loop.
		@param cfg: [dict] Configurations
		@param ctl: [object] Threading control object (Event)
		'''
		if self.opt.verbose:
			print('detect_motion')
		# config defaults
		cfg_pin = cfg.get('pin', -1)
		cfg_active_value = cfg.get('active_value', "0")
		cfg_timeout_sec = cfg.get('timeout_sec', 0.1)
		# Pin init
		gpio = onionGpio.OnionGpio(cfg_pin)
		if gpio.setInputDirection():
			raise RuntimeError("Could not set GPIO direction to input!")
		prev_value = '0' if cfg_active_value == '1' else '1'
		# infinite loop
		while not ctl.wait(cfg_timeout_sec):
			value = gpio.getValue().strip()
			if prev_value != value:
				if value == cfg_active_value:
					if self.opt.verbose:
						print("ALARM: motion detected")
					# WHAT TO DO ???
				prev_value = value
		if self.opt.verbose:
			print('detect_motion exit')

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
