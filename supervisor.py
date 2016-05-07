# -*- coding: utf-8 -*-

import os 
import sys
import json
import time
import multiprocessing
import getopt
from datetime import datetime as Datetime
from dateutil.relativedelta import *
import telegram

# Load SDK:
pauli_storage_path = '/usr/local/lib'
pauli_storage_absolute_path = os.path.abspath(pauli_storage_path)
sys.path.append(pauli_storage_absolute_path)
from pauli_sdk.Classes.response import Success
from pauli_sdk.Classes.response import Error
from pauli_sdk.Classes.response import Already_Handled_Exception
from pauli_sdk.Modules import log as _Log
from pauli_sdk.Modules import constants as _Pauli_Constants
from pauli_sdk.Modules import helper as _Pauli_Helper

# Development:
from General import utilities as _Utilities
from General import constants as _Constants
from General import config as _General_Config
from Processes import config as _Processes_Config

# Set environment:
os.environ['TZ'] = _General_Config.general['logging']['time_zone']
time.tzset()

FOREST_MODE = _Processes_Config.process_handler['forest_mode']
SERVER_INDEX = _Processes_Config.process_handler['server_index']
PATH_TO_LOGS = _General_Config.general['logging']['path']
SL1_LOGS = PATH_TO_LOGS + '/SL1/Threads/sl1-1.log'
HOURS_AGO = 15
LOG_INDENT = _Constants.LOG_INDENT

def get_last_line(file_name):
	with open(file_name, "rb") as f:
	    first = f.readline()      # Read the first line.
	    f.seek(-2, 2)             # Jump to the second last byte.
	    while f.read(1) != b"\n": # Until EOL is found...
	        f.seek(-2, 1)         # ...jump back the read byte plus one more.
	    last = f.readline()       # Read last line.
	return last

def get_time_of_last_line(last_line):
	time_length = 19
	line_length = len(last_line)
	begin_of_time = line_length - time_length - 1
	time = last_line[begin_of_time:line_length-1]
	return time

def get_processes_in_this_mode():
	processes = _Constants.PROCESSES_RUN_MODE[str(FOREST_MODE)]
	return processes

def get_process_logs_file(process_name):
	return PATH_TO_LOGS + _Constants.PROCESS_LOGS[process_name]

def get_last_log_time_of_a_process(process_name):
	log_file = get_process_logs_file(process_name)
	last_line = get_last_line(log_file)
	time = get_time_of_last_line(last_line)
	time = Datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
	return time

def get_a_date_from_hours_ago(hours):
	hours_ago = Datetime.now() - relativedelta(hours=hours)
	return hours_ago

# Check the log date and returns true if is ok (is up to date) or false if not:
def is_everything_ok(log_date):
	if log_date is True:
		return True
	hours_ago = get_a_date_from_hours_ago(HOURS_AGO)
	everything_ok = False
	if log_date > hours_ago:
		everything_ok = True
	return everything_ok

CHANGITO = '\xF0\x9F\x99\x88'
HAPPY_FACE = '\xF0\x9F\x98\x83'

def get_command_line_params(argv):
	hey = False
	try:
		opts, args = getopt.getopt(argv,"hn:p:d",["process_name=","process_params=","debug="])
	except Exception as e:
		error_message = e.message
		print error_message
		sys.exit()
	for opt, arg in opts:
		if opt == '-h':
			hey = True
			break
	return hey

def main(argv):
	hey_execution = get_command_line_params(argv)
	cron_logger = _Utilities.setup_logger('cron')
	current_hour = Datetime.now().hour
	chat_id = None
	if hey_execution:
		message = HAPPY_FACE + ' Ya acabe de sincronizar a todos los contribuyentes carnal y va de nuez'
		_Utilities.send_message_to_forest_telegram_contacts(message)
		return
		hey = _Utilities.hey(logger=cron_logger,server_index=SERVER_INDEX)
		if hey is False:
			return
		chat_id = hey
	cron_logger.info('------------------------------------------------------------------------')
	cron_logger.info(LOG_INDENT + 'Performing Forest Supervision')
	processes = get_processes_in_this_mode()
	for process in processes:
		if process == _Constants.INITIALIZATION:
			taxpayers = _Utilities.get_taxpayers_for_a_specific_process(process)
			taxpayers_in_init = len(taxpayers)
			if taxpayers_in_init > 0:
				last_log_date = get_last_log_time_of_a_process(process)
			else:
				last_log_date = True
		else:
			last_log_date = get_last_log_time_of_a_process(process)		
		everything_ok = is_everything_ok(last_log_date)	
		cron_logger.info(LOG_INDENT + process.upper())
		current_date = Datetime.now()
		year = current_date.year
		month = current_date.month
		day = current_date.day
		begin_of_the_day = Datetime(year,month,day)		
		if last_log_date > begin_of_the_day:
			last_log_date_hour = str(last_log_date)[11:11+8]
		else:
			last_log_date_hour = str(last_log_date)
		if everything_ok:
			message = HAPPY_FACE + 'Todo chido con ' + process + ' en Forest_' + str(SERVER_INDEX) + '. Tengo el ultimo registro a las ' + str(last_log_date_hour)
			cron_logger.info(2*LOG_INDENT + 'Everyting ok. Last log was at: ' + str(last_log_date_hour))
			if chat_id is not None:
				_Utilities.send_message_to_forest_telegram_contacts(message,chat_ids=[chat_id])
			else:
				_Utilities.send_message_to_forest_telegram_contacts(message)
		else:
			message = 'Tengo un ' + 3*telegram.Emoji.PILE_OF_POO + 1*CHANGITO + ' en Forest_' + str(SERVER_INDEX) + '. El ultimo registro a las ' + str(last_log_date_hour)
			cron_logger.info(2*LOG_INDENT + 'There is a PROBLEM. Last log was at: ' + str(last_log_date_hour))
			if chat_id is not None:
				_Utilities.send_message_to_forest_telegram_contacts(message,chat_ids=[chat_id])
			else:
				_Utilities.send_message_to_forest_telegram_contacts(message)

main(sys.argv[1:])







