# -*- coding: utf-8 -*-

# ██████╗ ██████╗  ██████╗  ██████╗███████╗███████╗███████╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗██████╗ 
# ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔════╝    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔══██╗
# ██████╔╝██████╔╝██║   ██║██║     █████╗  ███████╗███████╗    ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ██████╔╝
# ██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝  ╚════██║╚════██║    ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ██╔══██╗
# ██║     ██║  ██║╚██████╔╝╚██████╗███████╗███████║███████║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗██║  ██║
# ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

# ======================================================== DEPENDENCIES

# Native:
from __future__ import division
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

def validate(process_name,mode=None,server_index=None,debug_execution=False):
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
		if debug_execution is True:
			return validated
		if mode == _Constants.BALANCER_MODE:
			cron_logger.info(2*LOG_INDENT + 'Balancer mode, checking processs ' + process_name + ' availability ... ')
			process_availability = _Utilities.check_process_availability(process_name)
			if process_availability is not True:
				cron_logger.info(LOG_INDENT + 'Process ' + process_name + ' is not available')
				return False
			return True
		elif mode == _Constants.SERVER_MODE:
			cron_logger.info(2*LOG_INDENT + 'Server mode, checking processs ' + process_name + ' availability ... ')
			process_availability = _Utilities.check_process_availability(process_name)
			if process_availability is False:
				cron_logger.info(2*LOG_INDENT + 'Checking server ' + str(server_index) + ' of process ' + process_name + ' availability ... ')
				server_availability = _Utilities.check_process_server_availability(process_name,server_index)
				if server_availability is not True:
					cron_logger.info(LOG_INDENT + 'Server ' + str(server_index) + ' of process ' + process_name + ' is not available')
					return False
				return True
			cron_logger.info(2*LOG_INDENT + 'Process ' + process_name + ' is available (then server processes are not available) ... ')
			return False
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

# This update is for balancing each thread in a different server (introduced on May 3rd 2016) -- each process will run in a different server --
# Code logic was splitted in two modes in order to achieve this

def execute_with_multiprocessing(process_file_name=None,default_log={},threads=1,specific_process_logger=None,cron_logger_starting_message='Process Start',process_name='PROCESS',process_instance=None,specific_shared_variables=None,taxpayers=[],mode=_Constants.BALANCER_MODE):
	try:
		cron_logger.info(LOG_INDENT + cron_logger_starting_message)
		if mode == _Constants.SERVER_MODE:
			specific_process_logger.info(' ',extra=default_log)
			specific_process_logger.info(' ',extra=default_log)
			specific_process_logger.info(' ',extra=default_log)
			specific_process_logger.info(' ',extra=default_log)
			specific_process_logger.info(_Constants.LOG_SEPARATOR,extra=default_log)
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
		if mode == _Constants.SERVER_MODE:
			specific_process_logger.info('Process Summary Data:',extra=default_log)
			specific_process_logger.info(LOG_INDENT + 'Number of taxpayers:    ' + str(total_taxpayers),extra=default_log)
			specific_process_logger.info(LOG_INDENT + 'Number of threads:      ' + str(threads),extra=default_log)
			specific_process_logger.info('Process Execution:',extra=default_log)
		# Subprocesses:
		subprocesses = _Utilities.get_taxpayers_subprocesses(taxpayers,process_file_name,threads)
		if mode == _Constants.BALANCER_MODE and process_name is not _Constants.EQUALIZATION:
			cron_logger.info(LOG_INDENT + 'Running in BALANCER mode')
			server_index = 0
			server_identifiers_loaded = 0
			for subprocess in subprocesses:
				server_index = server_index + 1
				subprocess_taxpayers = subprocess['taxpayers']
				identifiers = []
				for taxpayer in subprocess_taxpayers:
					identifier = taxpayer['identifier']
					identifiers.append(identifier)
				server_index_updating =	_Utilities.update_taxpayers_server_index(identifiers,server_index,logger=cron_logger)
				server_identifiers = server_index_updating['n']
				cron_logger.info(2*LOG_INDENT + 'Server ' + str(server_index) + ' loaded with ' + str(server_identifiers) + ' taxpayers')
				server_identifiers_loaded = server_identifiers_loaded + server_identifiers
			cron_logger.info(2*LOG_INDENT + 'Total taxpayers loaded: ' + str(server_identifiers_loaded))
		if mode == _Constants.SERVER_MODE or process_name is _Constants.EQUALIZATION:
			cron_logger.info(LOG_INDENT + 'Running in SERVER mode')
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
		start_time = time.time()
		process_name = process['name']
		process_params = process['params']
		debug_execution = process['debug']
		cron_logger.info(LOG_INDENT + 'Validating CRON Process')
		process_availability = _Utilities.check_process_availability('cron',debug_execution=debug_execution)
		if process_availability is not True:
			cron_logger.info(LOG_INDENT + 'CRON is suspended')
			suspended_at = Datetime.now()
			_Utilities.update_cron_process_log('cron',logger=cron_logger,suspended_at=suspended_at,debug_execution=debug_execution)
			return False
		cron_logger.info(LOG_INDENT + 'Validating process ... ')
		forest_mode = PROCESS_HANDLER_CONFIG['forest_mode']
		server_index = PROCESS_HANDLER_CONFIG['server_index']# The index related to this server (in case it is configured in SERVER mode)
		process_is_valid = validate(process_name,forest_mode,server_index,debug_execution=debug_execution)
		if process_is_valid:
			cron_logger.info(LOG_INDENT + 'Updating cron db log ... ')
			_Utilities.update_cron_process_log(process_name,logger=cron_logger,debug_execution=debug_execution)
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
			cron_logger.info(LOG_INDENT + 'Running in mode: ' + str(forest_mode))
			specific_shared_variables = SPECIFIC_PROCESS_CONFIG_DATA['specific_shared_variables']
			# Get process at db:
			cron_logger.info(LOG_INDENT + 'Getting process ' + process_name + ' at db')
			process = _Utilities.get_db_process(process_name)
			from_taxpayer = None
			if debug_execution is True:
				cron_logger.info(LOG_INDENT + 'This process will run in debugging mode')
			elif 'current_taxpayer' in process:
				from_taxpayer = process['current_taxpayer']# If process fails or if it is stopped it will start from this taxpayer
				cron_logger.info(LOG_INDENT + 'This process will run from taxpayer ' + from_taxpayer)
			else:
				cron_logger.info(LOG_INDENT + 'This process will run for all taxpayers')
			# Update default log
			default_log = _Utilities.add_defalut_data_to_default_log(default_log)
			# Logging:
			if debug_execution is not True:
				cron_logger.info(LOG_INDENT + 'Logging calling at cron procesess ... ')
				_Utilities.log_at_cron_processes(process)		
			cron_logger.info(LOG_INDENT + 'Getting taxpayers for this process ... ')
			taxpayers = _Utilities.get_taxpayers_for_a_specific_process(process_name,limit=None,from_taxpayer=from_taxpayer,logger=cron_logger,debug_execution=debug_execution,server_index=server_index,mode=forest_mode)
			# Set unavailable:
			if forest_mode == _Constants.SERVER_MODE:
				cron_logger.info(2*LOG_INDENT + 'Setting server ' + str(server_index) + ' unavailable for ' + process_name)
				_Utilities.set_process_server_unavailable(process_name,server_index,logger=cron_logger)
			elif forest_mode == _Constants.BALANCER_MODE:
				cron_logger.info(LOG_INDENT + 'Setting process ' + process_name + ' unavailable')
				process_availability = _Utilities.set_process_unavailable(process_name,taxpayers=taxpayers,logger=cron_logger,debug_execution=debug_execution,threads=threads)
				cron_logger.info(LOG_INDENT + process_name + ' availability: ' + str(process_availability))
			# Multi-threading execution:
			cron_logger.info(LOG_INDENT + 'Executing ... ')
			cron_logger.info(2*LOG_INDENT + 'Process name: ' + process_name)
			if forest_mode == _Constants.BALANCER_MODE:
				cron_logger.info(2*LOG_INDENT + 'Servers:      ' + str(threads))
			elif forest_mode == _Constants.SERVER_MODE:
				cron_logger.info(2*LOG_INDENT + 'Threads:      ' + str(threads))
			else:
				cron_logger.info(2*LOG_INDENT + 'UNAVAILABLE MODE')
				return
			cron_logger.info(2*LOG_INDENT + 'Taxpayers:    ' + str(len(taxpayers)))
			cron_logger.info(2*LOG_INDENT + 'Params:       ' + str(process_params))
			execute_with_multiprocessing(process_file_name=process_file_name,specific_process_logger=specific_process_logger,default_log=default_log,cron_logger_starting_message=cron_logger_starting_message,process_name=process_name,process_instance=process_instance,threads=threads,specific_shared_variables=specific_shared_variables,taxpayers=taxpayers,mode=forest_mode)
			end_time = time.time()
			process_duration = (end_time - start_time)/3600# in hours
			log_process_duration = False
			if len(taxpayers) > 0:
				log_process_duration = True
			if forest_mode == _Constants.SERVER_MODE:
				cron_logger.info(2*LOG_INDENT + 'Setting server ' + str(server_index) + ' available for ' + process_name)
				_Utilities.set_process_server_available(process_name,server_index,logger=cron_logger)
				# BALANCER MODE is set available once all servers are available:
				all_servers_are_available = _Utilities.check_process_servers_availability(process_name,logger=cron_logger)
				cron_logger.info(2*LOG_INDENT + 'All servers availability ' + str(all_servers_are_available))
				if all_servers_are_available:
					cron_logger.info(2*LOG_INDENT + 'Setting process available for ' + process_name)
					_Utilities.set_process_available(process_name,process_duration=process_duration,logger=cron_logger,log_process_duration=log_process_duration,debug_execution=debug_execution)
			if process_name == _Constants.EQUALIZATION:
				cron_logger.info(2*LOG_INDENT + 'Setting process available for ' + process_name)
				_Utilities.set_process_available(process_name,process_duration=process_duration,logger=cron_logger,log_process_duration=log_process_duration,debug_execution=debug_execution)
		else:
			cron_logger.info(LOG_INDENT + 'End of execution')
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		cron_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception
