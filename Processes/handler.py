# -*- coding: utf-8 -*-

# ██████╗ ██████╗  ██████╗  ██████╗███████╗███████╗███████╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗██████╗ 
# ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔════╝    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔══██╗
# ██████╔╝██████╔╝██║   ██║██║     █████╗  ███████╗███████╗    ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ██████╔╝
# ██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝  ╚════██║╚════██║    ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ██╔══██╗
# ██║     ██║  ██║╚██████╔╝╚██████╗███████╗███████║███████║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗██║  ██║
# ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

# ======================================================== DEPENDENCIES

# Native:
import os 
import sys
import json
import time
import multiprocessing
from multiprocessing import Process
from multiprocessing import Value
from multiprocessing import Lock# Allows sharing variables between Threads
from datetime import datetime as Datetime
from datetime import date as Date

# Pauli SDK:
from pauli_sdk.Classes.response import Success
from pauli_sdk.Classes.response import Error
from pauli_sdk.Classes.response import Already_Handled_Exception
from pauli_sdk.Modules import log as _Log
from pauli_sdk.Modules import constants as _Pauli_Constants
from pauli_sdk.Modules import helper as _Pauli_Helper
from pauli_sdk.Modules import validating_engine as _Validating_Engine
from pauli_sdk.Modules import request_handler as _Request_Handler

# Development:
from General import config as _General_Config
from General import utilities as _Utilities
from General import constants as _Constants
from Processes import config as _Processes_Config

# ======================================================== MODULE CODE

cron_logger = _Utilities.get_logger('cron')
LOG_INDENT = _Constants.LOG_INDENT
PROCESS_HANDLER_CONFIG = _Processes_Config.process_handler

#  _   _       _ _     _       _       
# | | | |     | (_)   | |     | |      
# | | | | __ _| |_  __| | __ _| |_ ___ 
# | | | |/ _` | | |/ _` |/ _` | __/ _ \
# \ \_/ / (_| | | | (_| | (_| | ||  __/
#  \___/ \__,_|_|_|\__,_|\__,_|\__\___|

# Descriptions: functions to validate Forest-Cron calling data, availability an so on

def validate(process_name):
	try:
		validated = True
		# Forest-Croning functione existance:
		cron_logger.info(2*LOG_INDENT + 'Checking Forest-Cron function existance ... ')
		if not process_name in PROCESS_HANDLER_CONFIG:
			cron_logger.info(LOG_INDENT + 'Process ' + process_name + ' does not exists at Forest-Cron')
			return False
		else:
			process_instance = PROCESS_HANDLER_CONFIG[process_name]
			if process_instance is None:
				cron_logger.info(LOG_INDENT + 'Invalid process name ' + process_name)
				return False
		# Process availability:
		cron_logger.info(2*LOG_INDENT + 'Checking ' + process_name + ' availability ... ')
		process_availability = _Utilities.check_process_availability(process_name)
		if process_availability is not True:
			cron_logger.info(LOG_INDENT + 'Process ' + process_name + ' is not available')
			return False
		return True
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		cron_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# ___  ___      _ _   _                                   _             
# |  \/  |     | | | (_)                                 (_)            
# | .  . |_   _| | |_ _ _ __  _ __ ___   ___ ___  ___ ___ _ _ __   __ _ 
# | |\/| | | | | | __| | '_ \| '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |
# | |  | | |_| | | |_| | |_) | | | (_) | (_|  __/\__ \__ \ | | | | (_| |
# \_|  |_/\__,_|_|\__|_| .__/|_|  \___/ \___\___||___/___/_|_| |_|\__, |
#                      | |                                         __/ |
#                      |_|                                        |___/ 

# Desctiption: Functions for supportting process multithreading (i.e. each task could be executed in n threads according to its configuration)

def execute_with_multiprocessing(process_file_name=None,default_log={},threads=1,specific_process_logger=None,cron_logger_starting_message='Process Start',process_name='PROCESS',process_instance=None,specific_shared_variables=None,taxpayers=[]):
	try:
		cron_logger.info(LOG_INDENT + cron_logger_starting_message)
		specific_process_logger.info(' ',extra=default_log)
		specific_process_logger.info(' ',extra=default_log)
		specific_process_logger.info(' ',extra=default_log)
		specific_process_logger.info(' ',extra=default_log)
		# specific_process_logger.info(_Constants.LOG_SEPARATOR,extra=default_log)
		specific_process_logger.info(process_name.upper(),extra=default_log)
		# Process data:
		total_taxpayers = len(taxpayers)
		shared_variables = {
			'current_taxpayer' : Value('i',0),
			'total_taxpayers' : Value('i',total_taxpayers),
			'lock' : Lock()
		}# End of shared_variables
		if specific_shared_variables is not None:
			for specific_shared_variable_name in specific_shared_variables:
				specific_shared_variables_value = specific_shared_variables[specific_shared_variable_name]
				shared_variables[specific_shared_variable_name] = specific_shared_variables_value
		specific_process_logger.info('Process Summary Data:',extra=default_log)
		specific_process_logger.info(LOG_INDENT + 'Number of taxpayers:    ' + str(total_taxpayers),extra=default_log)
		specific_process_logger.info(LOG_INDENT + 'Number of threads:      ' + str(threads),extra=default_log)
		specific_process_logger.info('Process Execution:',extra=default_log)
		# Subprocesses:
		subprocesses = _Utilities.get_taxpayers_subprocesses(taxpayers,process_file_name,threads)
		_Utilities.log_taxpayers_subprocesses(subprocesses,specific_process_logger,indent=LOG_INDENT,default_log=default_log)
		starting_message = process_name.upper() + ' PROCESS DETAILS: '
		_Utilities.execute_taxpayers_subprocesses_in_parallel(subprocesses,process_instance,shared_variables=shared_variables,logger=specific_process_logger,starting_message=starting_message,default_log=default_log)
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		specific_process_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

#  _____                    _       
# |  ___|                  | |      
# | |____  _____  ___ _   _| |_ ___ 
# |  __\ \/ / _ \/ __| | | | __/ _ \
# | |___>  <  __/ (__| |_| | ||  __/
# \____/_/\_\___|\___|\__,_|\__\___|

def execute(process):
	try:
		process_name = process['name']
		process_params = process['params']
		cron_logger.info(LOG_INDENT + 'Validating process ... ')
		process_is_valid = validate(process_name)
		if process_is_valid:
			cron_logger.info(LOG_INDENT + 'Getting instance of ' + process_name)
			# Process data:
			SPECIFIC_PROCESS_CONFIG_DATA = PROCESS_HANDLER_CONFIG[process_name]
			specific_process_logger = SPECIFIC_PROCESS_CONFIG_DATA['specific_process_logger']
			process_instance = SPECIFIC_PROCESS_CONFIG_DATA['process_instance']
			default_log = SPECIFIC_PROCESS_CONFIG_DATA['default_log']
			cron_logger_starting_message = SPECIFIC_PROCESS_CONFIG_DATA['cron_logger_starting_message']
			process_name = SPECIFIC_PROCESS_CONFIG_DATA['process_name']
			process_file_name = SPECIFIC_PROCESS_CONFIG_DATA['process_file_name']
			threads = SPECIFIC_PROCESS_CONFIG_DATA['threads']
			specific_shared_variables = SPECIFIC_PROCESS_CONFIG_DATA['specific_shared_variables']
			# Get process at db:
			cron_logger.info(LOG_INDENT + 'Getting process ' + process_name + ' at db')
			process = _Utilities.get_db_process(process_name)
			from_taxpayer = None
			if 'current_taxpayer' in process:
				from_taxpayer = process['current_taxpayer']# If process fails or if it is stopped it will start from this taxpayer
				cron_logger.info(LOG_INDENT + 'This process will run from taxpayer ' + from_taxpayer)
			else:
				cron_logger.info(LOG_INDENT + 'This process will run for all taxpayers')
			# Set unavailable:
			cron_logger.info(LOG_INDENT + 'Setting process ' + process_name + ' unavailable')
			_Utilities.set_process_unavailable(process_name,logger=cron_logger)
			# Update default log
			default_log = _Utilities.add_defalut_data_to_default_log(default_log)
			# Logging:
			cron_logger.info(LOG_INDENT + 'Logging calling at cron procesess ... ')
			_Utilities.log_at_cron_processes(process)		
			cron_logger.info(LOG_INDENT + 'Getting taxpayers for this process ... ')
			taxpayers = _Utilities.get_taxpayers_for_a_specific_process(process_name,limit=50,from_taxpayer=from_taxpayer)
			# Multi-threading execution:
			cron_logger.info(LOG_INDENT + 'Executing ... ')
			cron_logger.info(2*LOG_INDENT + 'Process name: ' + process_name)
			cron_logger.info(2*LOG_INDENT + 'Threads:      ' + str(threads))
			cron_logger.info(2*LOG_INDENT + 'Taxpayers:    ' + str(len(taxpayers)))
			cron_logger.info(2*LOG_INDENT + 'Params:       ' + str(process_params))
			execute_with_multiprocessing(process_file_name=process_file_name,specific_process_logger=specific_process_logger,default_log=default_log,cron_logger_starting_message=cron_logger_starting_message,process_name=process_name,process_instance=process_instance,threads=threads,specific_shared_variables=specific_shared_variables,taxpayers=taxpayers)
			_Utilities.set_process_available(process_name,logger=cron_logger)
		# else:
		# 	cron_logger.info(LOG_INDENT + 'End of execution')
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		cron_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception
