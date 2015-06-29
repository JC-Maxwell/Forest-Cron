# -*- coding: utf-8 -*-

# ███╗   ███╗ █████╗ ██╗███╗   ██╗
# ████╗ ████║██╔══██╗██║████╗  ██║
# ██╔████╔██║███████║██║██╔██╗ ██║
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
                                                                                                                
# Description: contains Forest-Cron main function (from here croning processes are spawn)

# ======================================================== DEPENDENCIES

# Native:
import os 
import sys
import json
import time
import multiprocessing
import getopt

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
from pauli_sdk.Modules import validating_engine as _Validating_Engine
from pauli_sdk.Modules import request_handler as _Request_Handler

# Development:
from General import config as _Config
from General import utilities as _Utilities
from General import constants as _Constants
from Processes import handler as _Processes_Handler
from Processes.Synchronization_layer_1 import config as _SL1_Config
from Processes.Equalization import config as _Equalization_Config

# Set environment:
os.environ['TZ'] = _Config.general['logging']['time_zone']
time.tzset()

# ======================================================== MODULE CODE

# Example of execution:
#  -> python main.py -n "synchronization_layer_1"
#  -> python main.py -n "synchronization_layer_1" -p '{ "key1" : "value1" }'

#  _____      _           _ _   _                   
# /  ___|    | |         | | | | |                _ 
# \ `--.  ___| |_    __ _| | | | | ___   __ _ ___(_)
#  `--. \/ _ \ __|  / _` | | | | |/ _ \ / _` / __|  
# /\__/ /  __/ |_  | (_| | | | | | (_) | (_| \__ \_ 
# \____/ \___|\__|  \__,_|_|_| |_|\___/ \__, |___(_)
#                                        __/ |      
#                                       |___/       

SL1_LOGGING_CONFIG = _SL1_Config.synchronization_layer_1['logging']
EQUALIZATION_LOGGING_CONFIG = _Equalization_Config.equalization['logging']
GENERAL_LOGGING_CONFIG = _Config.general['logging']


LOG_INDENT = _Constants.LOG_INDENT

# Initiliaze all project logs for this execution:
def set_all_loggers():
	try:
		# Register Fores-cron callings (calling, validation, errors and execution):
		cron_logger = _Utilities.setup_logger('cron')# Default 
		# Temporal log table of all the process executed:
		cron_processes_logger = _Utilities.setup_logger('cron_processes',file_name=GENERAL_LOGGING_CONFIG['processes_file_name'],format=GENERAL_LOGGING_CONFIG['processes_file_format'])
		# Process logs (every process has its logs). Also every process has subprocesses (threads) and each one of this subprocesses has its logs (this logs are created on each subprocess respectively):
		sl1_logger = _Utilities.setup_logger(SL1_LOGGING_CONFIG['process_file_name'],path=SL1_LOGGING_CONFIG['process_path'],file_name=SL1_LOGGING_CONFIG['process_file_name'] ,file_extension=SL1_LOGGING_CONFIG['file_extension'],format=SL1_LOGGING_CONFIG['format'],level=SL1_LOGGING_CONFIG['level'])
		equalization_logger = _Utilities.setup_logger(EQUALIZATION_LOGGING_CONFIG['process_file_name'],path=EQUALIZATION_LOGGING_CONFIG['process_path'],file_name=EQUALIZATION_LOGGING_CONFIG['process_file_name'] ,file_extension=EQUALIZATION_LOGGING_CONFIG['file_extension'],format=EQUALIZATION_LOGGING_CONFIG['format'],level=EQUALIZATION_LOGGING_CONFIG['level'])
	except Exception as e:
		print 'Error settion up all logs'
		print e
		raise e

# Get params (i.e. params given at command line execution)
def get_command_line_params(argv):
	try:
		process_name = ''
		process_params = {}
		try:
			cron_logger.debug(' - Getting options ... ')
			opts, args = getopt.getopt(argv,"hn:p:",["process_name=","process_params="])
		except Exception as e:
			error_message = e.message
			print error_message
			cron_logger.critical(error_message)
			sys.exit()
		cron_logger.debug(' - Iterating options ... ')
		for opt, arg in opts:
			if opt == '-h':
				error_message = 'main.py -n <process_name> -p <process_params>'
				print error_message
				cron_logger.debug(error_message)
				sys.exit()
			elif opt in ("-n", "--process_name"):
				cron_logger.debug(' - process_name option found ... ')
				process_name = arg
			elif opt in ("-p", "--process_params"):
				cron_logger.debug(' - process_params option found ... ')
				process_params = json.loads(arg)
		if process_name != '':
			cron_logger.debug(' - Building process ... ')
			process = {
				'name' : process_name,
				'params' : process_params
			}#End of process
			return process
		else:
			error_message = 'Invalid process_name or process_params'
			print error_message
			cron_logger.critical(error_message)
			sys.exit()
	except Exception as e:
		error_message = e.message
		print error_message
		cron_logger.critical(error_message)
		sys.exit()

# ___  ___      _       
# |  \/  |     (_)      
# | .  . | __ _ _ _ __  
# | |\/| |/ _` | | '_ \ 
# | |  | | (_| | | | | |
# \_|  |_/\__,_|_|_| |_|
                        
def main(argv):
	try:
		cron_logger.info('FOREST-CRON PROCESS CALLED')
		cron_logger.info(LOG_INDENT + 'Getting command line params ... ')
		process = get_command_line_params(argv)
		cron_logger.info(LOG_INDENT + 'Calling process handler ... ')
		_Processes_Handler.execute(process)
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		cron_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		return already_handled_exception

# Start a process execution: 
if __name__ == '__main__':
	# Main process name:
	multiprocessing.current_process().name = 'cron'
	# Set all loggers:
	set_all_loggers()
	# Init:
	cron_logger = _Utilities.get_logger('cron')
	cron_logger.info(' ')
	cron_logger.info(_Constants.LOG_SEPARATOR)
	# Process params:
	process = 'synchronization_layer_1'
	process_params = {
		'process' : process
	}#End of process_params
	# Exectuion:
	main(sys.argv[1:])
