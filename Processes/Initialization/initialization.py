# -*- coding: utf-8 -*-

# ██╗███╗   ██╗██╗████████╗██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██║████╗  ██║██║╚══██╔══╝██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██║██╔██╗ ██║██║   ██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██║██║╚██╗██║██║   ██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ██║██║ ╚████║██║   ██║   ██║██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

# Description: contains initialization process. Initialization means synchronization from start date

# ======================================================== DEPENDENCIES

# Native:
import sys
from datetime import datetime as Datetime
from datetime import date as Date
import multiprocessing

# Pauli SDK dependency:
from pauli_sdk.Modules import constants as _Pauli_Constants
from pauli_sdk.Modules import helper as _Pauli_Helper
from pauli_sdk.Classes.response import Error
from pauli_sdk.Classes.response import Already_Handled_Exception

# Development:
from General import constants as _Constants
from General import utilities as _Utilities
from General import firmware as _Firmware

from Processes.Initialization import config as _Initialization_config
from Processes.Initialization import locals as _Locals
INITIALIZATION_CONFIG = _Initialization_config.initialization
INITIALIZATION_LOGGING_CONFIG = INITIALIZATION_CONFIG['logging']

# ======================================================== CODE                                                                                                                                                                          

LOG_INDENT = _Constants.LOG_INDENT
INITIALIZATION_PROCESS_NAME = 'INITIALIZATION'

# Cron logger (Main):
cron_logger = _Utilities.get_logger('cron')
initialization_logger = _Utilities.get_logger(INITIALIZATION_LOGGING_CONFIG['process_file_name'])

# Notes:
# cron_logger    -> log at cron main level execution
# initialization_logger     -> log at cron-initialization process level execution
# process_logger -> log at cron-init-n subprocess level execution (n subprocesses every one has its log file)

# Each initialization thread (i.e. subprocess) executes this function. Contains initialization process for a set of taxpayers
def excute_initialization(taxpayers,shared_variables):# Taxpayers are the ones splitted for this specific subprocess
	try:
		# Shared variables:
		current_taxpayer = shared_variables['current_taxpayer']
		total_taxpayers = shared_variables['total_taxpayers']
		current_table_row = shared_variables['current_table_row']
		lock = shared_variables['lock']
		# Process:
		process_name = multiprocessing.current_process().name
		total_taxpayers_for_this_subprocess = len(taxpayers)
		# Process logger:
		process_logger = _Utilities.get_subprocess_logger(process_name,INITIALIZATION_LOGGING_CONFIG,logger=initialization_logger)
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(_Constants.LOG_SEPARATOR)
		process_logger.info(INITIALIZATION_PROCESS_NAME + ' - ' + process_name.upper())
		taxpayers_initialized_counter = 0
		process_logger.info(LOG_INDENT + 'Taxpayers: ' + str(total_taxpayers_for_this_subprocess))
		for taxpayer in taxpayers:
			_Utilities.update_current_taxpayer(_Constants.INITIALIZATION,taxpayer['identifier'],current_taxpayer.value+1,logger=process_logger)
			percentage_of_initialization_done = _Utilities.get_process_percentage_done(taxpayers_initialized_counter,total_taxpayers_for_this_subprocess)
			taxpayers_initialized_counter = taxpayers_initialized_counter + 1# Specific taxpayers (this thread's counter)
			process_logger.info(LOG_INDENT + '-> (' + str(taxpayers_initialized_counter) + '/' + str(total_taxpayers_for_this_subprocess)  + ') ' + taxpayer['identifier'] + ' --- ' + percentage_of_initialization_done)
			initialization_execution_data = excute_initialization_for_taxpayer(taxpayer=taxpayer,process_logger=process_logger)
			with lock:
				current_taxpayer.value = current_taxpayer.value + 1
			current_date = Datetime.now()
			initialization_execution_log = {
				'date' : str(current_date)[:10],
				'hour' : str(current_date)[10:-7],
				'process_name' : process_name,
				'current_taxpayer_index' : current_taxpayer.value,
				'total_taxpayers' : total_taxpayers.value,
				'identifier' : taxpayer['identifier'],
				'new' : initialization_execution_data['new'],
				'stored' : initialization_execution_data['stored'],
				'year_initialized' : initialization_execution_data['year_initialized'],
				'month_initialized' : initialization_execution_data['month_initialized'],
				'percentage_initialized' : initialization_execution_data['percentage_initialized'],
				'initialized' : initialization_execution_data['initialized'],
				# 'new' : 0,
				# 'stored' : 0,
				# 'year_initialized' : '2015',
				# 'month_initialized' : '02',
				# 'percentage_initialized' : 0,
				'lock' : lock,
				'current_table_row' : current_table_row
			}# End of initialization_execution_log
			if initialization_execution_log['current_taxpayer_index'] == initialization_execution_log['total_taxpayers']:
				initialization_execution_log['end'] = True
				initialization_execution_log['end_message'] = INITIALIZATION_PROCESS_NAME + ' DONE SUCCESSFULLY \\0/'
			else:
				initialization_execution_log['end'] = False
			_Locals.log_initiliazation_thread_logs_at_initialization_main_logs(initialization_execution_log=initialization_execution_log,initialization_logger=initialization_logger,cron_logger=cron_logger)
			process_logger.info(2*LOG_INDENT + 'Updating initialization data for taxpayer ... ')
			_Locals.update_initialization_data_for_taxpayer(taxpayer,initialization_execution_log,logger=process_logger)
			process_logger.info(2*LOG_INDENT + 'Synchronized successfully. Logged at SL1 main logs')
		process_logger.info(INITIALIZATION_PROCESS_NAME + ' - ' + process_name.upper() + ' DONE SUCCESSFULLY \0/')
		process_logger.info(_Constants.LOG_SEPARATOR)
		return 'OK'
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		initialization_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Contains initialization process for a single taxpayer:
def excute_initialization_for_taxpayer(taxpayer=None,process_logger=None):
	try:
		initialization_data = _Locals.get_initialization_data(taxpayer,logger=process_logger)
		initialized = initialization_data['initialized']
		if initialized == False:
			initialization_log = _Locals.new_initialization_log(logger=process_logger)
			# Get CFDIs from DB:
			process_logger.info(2*LOG_INDENT + 'RETRIEVING DATA FROM FOREST DB ... ')
			process_logger.info(3*LOG_INDENT + 'Year: ' + str(initialization_data['year']) + ' Month: ' + str(initialization_data['month']))
			process_logger.info(3*LOG_INDENT + 'From ' + str(initialization_data['begin_date']) + ' to ' + str(initialization_data['end_date']))
			cfdis_in_db = _Utilities.get_cfdis_in_forest_for_this_taxpayer_at_period(taxpayer,initialization_data['begin_date'],initialization_data['end_date'],limit=None)
			# Manage or format CFDis data:
			existing_cfdi_uuids = _Utilities.get_existing_uuids_in_forest_db(cfdis_in_db=cfdis_in_db,logger=process_logger)
			# Log Forest data:
			process_logger.info(3*LOG_INDENT + 'Existing:           ' + str(len(existing_cfdi_uuids)))
			# Get CFDIs from firmware:
			get_sat_updates_params = {
				'identifier' : taxpayer['identifier'],
				'password' : taxpayer['password'],
				'year' : initialization_data['year'],
				'months' : [initialization_data['month']],
				'uuids' : existing_cfdi_uuids
			}# End of get_sat_update_params
			# -------------------------------------------------------------------
			# bugSolved 12/Ago/15 
			# Event: timeout value was becoming longer and longer because of connection problems (firmware servers could not be reached due to connection problems instead of logic problems)
			# firmware_timeout = taxpayer['firmware_timeout'] if 'firmware_timeout' in taxpayer and taxpayer['firmware_timeout'] is not None else _Constants.DEFAULT_FIRMWARE_TIMEOUT
			firmware_timeout = _Constants.DEFAULT_FIRMWARE_TIMEOUT
			# -------------------------------------------------------------------
			process_logger.info(2*LOG_INDENT + 'RETRIEVING DATA FROM FIRMWARE (SAT) timeout = ' + str(firmware_timeout) + ' secs')
			sat_updates = _Firmware.isa(instruction='get_sat_updates',params=get_sat_updates_params,log=initialization_log,logger=process_logger,timeout=firmware_timeout,taxpayer=taxpayer)
			new_cfdis = sat_updates['new']
			process_logger.info(3*LOG_INDENT + 'CFDI new:           ' + str(initialization_log['firmware']['new']))
			process_logger.info(3*LOG_INDENT + 'CFDI to-update:     ' + str(initialization_log['firmware']['update']))
			# Update Forest DB -> NEW OR COMPLETED:
			process_logger.info(2*LOG_INDENT + 'UPDATING FOREST DB ... ')
			n = 0
			for new_cfdi in new_cfdis:
				uuid = new_cfdi['uuid']
				_Utilities.create_cfdi(new_cfdi,logger=process_logger,log=initialization_log)
				n = n + 1
				process_logger.info(3*LOG_INDENT + str(n) + '. ' + uuid + ' stored in Forest DB')
			process_logger.info(2*LOG_INDENT + 'SUMMARY ... ')
			process_logger.info(3*LOG_INDENT + 'New stored:         ' + str(initialization_log['forest_db']['after']['new']))
			process_logger.info(3*LOG_INDENT + 'Pending:            ' + str(initialization_log['forest_db']['after']['pending']))
			initialization_result = {
				'new' : initialization_log['firmware']['new'],
				'stored' : initialization_log['forest_db']['after']['new'],
				'year_initialized' : initialization_data['year'],
				'month_initialized' : initialization_data['month']
			}# End of initialization_result
		else:
			initialization_result = {
				'new' : _Constants.ZLATAN,
				'stored' : _Constants.ZLATAN,
				'year_initialized' : _Constants.ZLATAN,
				'month_initialized' : _Constants.ZLATAN
			}# End of initialization_result
		# Update taxpayer:
		new_initialization_data = initialization_data['new_initialization_data']
		taxpayer = _Locals.update_taxpayer_initialization_status(taxpayer,new_initialization_data,logger=process_logger,initialized=initialized)
		initialization_result['percentage_initialized'] = taxpayer['data']['percentage_initialized']
		initialization_result['initialized'] = initialized
		process_logger.info(3*LOG_INDENT + 'Percentage initialized:            ' + str(initialization_result['percentage_initialized']))
		return initialization_result
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		process_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception
