# -*- coding: utf-8 -*-

# ██╗███╗   ██╗██╗████████╗██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗    ██╗      ██████╗  ██████╗ █████╗ ██╗     ███████╗
# ██║████╗  ██║██║╚══██╔══╝██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║    ██║     ██╔═══██╗██╔════╝██╔══██╗██║     ██╔════╝
# ██║██╔██╗ ██║██║   ██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║    ██║     ██║   ██║██║     ███████║██║     ███████╗
# ██║██║╚██╗██║██║   ██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║    ██║     ██║   ██║██║     ██╔══██║██║     ╚════██║
# ██║██║ ╚████║██║   ██║   ██║██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║    ███████╗╚██████╔╝╚██████╗██║  ██║███████╗███████║
# ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝
                                                                                                                                                                                                                                                                                              
# Description: contains initialization local functions (functions that are used in initialization's logics)

# ======================================================== DEPENDENCIES

# Native:
import sys
import multiprocessing
from multiprocessing import Process
from multiprocessing import Value
from multiprocessing import Lock# Allows sharing variables between Threads
from datetime import datetime as Datetime
from datetime import date as Date

# Pauli SDK dependency:
from pauli_sdk.Modules import constants as _Pauli_Constants
from pauli_sdk.Modules import helper as _Pauli_Helper
from pauli_sdk.Classes.response import Error
from pauli_sdk.Classes.response import Already_Handled_Exception

# Corebook SDK:
from corebook_sdk import corebook_sdk as _Corebook_SDK
Corebook_SDK_Error = _Corebook_SDK.Error

# Development:
from General import constants as _Constants
from General import utilities as _Utilities
from Processes.Initialization import config as _Initialization_config
INITIALIZATION_CONFIG = _Initialization_config.initialization
INITIALIZATION_LOGGING_CONFIG = INITIALIZATION_CONFIG['logging']

# ======================================================== CODE                                                                                                                                                                          

LOG_INDENT = _Constants.LOG_INDENT

# Cron logger (Main):
cron_logger = _Utilities.get_logger('cron')
initialization_logger = _Utilities.get_logger(INITIALIZATION_LOGGING_CONFIG['process_file_name'])

#  _                       _               
# | |                     (_)            _ 
# | |     ___   __ _  __ _ _ _ __   __ _(_)
# | |    / _ \ / _` |/ _` | | '_ \ / _` |  
# | |___| (_) | (_| | (_| | | | | | (_| |_ 
# \_____/\___/ \__, |\__, |_|_| |_|\__, (_)
#               __/ | __/ |         __/ |  
#              |___/ |___/         |___/   

# Dictionary to log initialization data:
def new_initialization_log(logger=None):
	try:
		initialization_log = {
			'forest_db' : {
				'before' : {
					'good' : 0,
					'pending' : 0
				},
				'after' : {
					'new' : 0,
					'pending_completed' : 0,
					'pending' : 0,
					'updated' : 0
				}
			},
			'firmware' : {
				'new' : 0,
				'update' : 0
			}
		}# End of initialization_log
		return initialization_log
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

INITIALIZATION_TABLE_TITLES = INITIALIZATION_LOGGING_CONFIG['table_titles']
INITIALIZATION_TABLE_FIELD_LENGTHS = INITIALIZATION_LOGGING_CONFIG['table_lengths']
DEFAULT_LOG = {}
for key in INITIALIZATION_TABLE_TITLES:
	DEFAULT_LOG[key] = ''

# Log at initialization main logs:
def log_initiliazation_thread_logs_at_initialization_main_logs(initialization_execution_log=None,initialization_logger=initialization_logger,cron_logger=cron_logger):
	try:
		current_taxpayer_index = initialization_execution_log['current_taxpayer_index']
		total_taxpayers = initialization_execution_log['total_taxpayers']
		end = initialization_execution_log['end']
		current_table_row = initialization_execution_log['current_table_row']
		lock = initialization_execution_log['lock']
		total_percentage_done = _Utilities.get_process_percentage_done(current_taxpayer_index,total_taxpayers)
		initialization_execution_log['percentage_done'] = total_percentage_done				
		with lock:
			current_table_row.value = current_table_row.value + 1
		if current_table_row.value >= INITIALIZATION_LOGGING_CONFIG['table_row_limit']:
			with lock: 
				current_table_row.value = 0
			begin_table_row = _Utilities.format_log(INITIALIZATION_TABLE_TITLES,INITIALIZATION_TABLE_FIELD_LENGTHS,begin=True)	
			initialization_logger.info('',extra=begin_table_row)
		initialization_execution_log = _Utilities.format_log(initialization_execution_log,INITIALIZATION_TABLE_FIELD_LENGTHS)
		initialization_logger.info('',extra=initialization_execution_log)
		if end is True:
			end_table_row = _Utilities.format_log(DEFAULT_LOG,INITIALIZATION_TABLE_FIELD_LENGTHS,end=True)
			initialization_logger.info('',extra=end_table_row)
			end_message = initialization_execution_log['end_message']
			initialization_logger.info(end_message,extra=DEFAULT_LOG)
	except Exception as e:
		initialization_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

#  _   _                 _ _          _______                         _       _        
# | | | |               | | |        / / ___ \                       | |     | |       
# | |_| | __ _ _ __   __| | | ___   / /| |_/ /_ _ _ __ ___  ___    __| | __ _| |_ __ _ 
# |  _  |/ _` | '_ \ / _` | |/ _ \ / / |  __/ _` | '__/ __|/ _ \  / _` |/ _` | __/ _` |
# | | | | (_| | | | | (_| | |  __// /  | | | (_| | |  \__ \  __/ | (_| | (_| | || (_| |
# \_| |_/\__,_|_| |_|\__,_|_|\___/_/   \_|  \__,_|_|  |___/\___|  \__,_|\__,_|\__\__,_|                                                                                       

# Get synchronization layer 1 data:
def get_initialization_data(taxpayer,logger=None):
	try:
		initialization_data_backup = taxpayer['data']['initialization']
		new_initialization_data = dict(initialization_data_backup)
		year = None
		month = None
		for year in initialization_data_backup:
			months_of_this_year_to_initialize = new_initialization_data[year]
			if len(months_of_this_year_to_initialize) > 0:
				month = months_of_this_year_to_initialize.pop()
				new_initialization_data[year] = months_of_this_year_to_initialize
				break
			else:
				del new_initialization_data[year]
				year = None
		if year is None and month is None:
			initialization_dat = {
				'initialized' : True,
				'new_initialization_data' : new_initialization_data
			}# End of initialization_dat
		else:
			begin_date = Datetime(int(year),int(month),1)
			end_date = Datetime(int(year),int(month),_Utilities.get_month_days(month))
			initialization_dat = {
				'initialized' : False,
				'new_initialization_data' : new_initialization_data,
				'year' : year,
				'month' : month,
				'begin_date' : begin_date,
				'end_date' : end_date
			}# End of initialization_dat
		return initialization_dat
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

#  _   _           _       _   _               _____                                      
# | | | |         | |     | | (_)             |_   _|                                     
# | | | |_ __   __| | __ _| |_ _ _ __   __ _    | | __ ___  ___ __   __ _ _   _  ___ _ __ 
# | | | | '_ \ / _` |/ _` | __| | '_ \ / _` |   | |/ _` \ \/ / '_ \ / _` | | | |/ _ \ '__|
# | |_| | |_) | (_| | (_| | |_| | | | | (_| |   | | (_| |>  <| |_) | (_| | |_| |  __/ |   
#  \___/| .__/ \__,_|\__,_|\__|_|_| |_|\__, |   \_/\__,_/_/\_\ .__/ \__,_|\__, |\___|_|   
#       | |                             __/ |                | |           __/ |          
#       |_|                            |___/                 |_|          |___/           

# Get synchronization layer 1 data:
def get_initialization_percentage_done(taxpayer,logger=None):
	try:
		total_months_to_initialize = taxpayer['data']['total_months_to_initialize']
		months_initialized = taxpayer['data']['months_initialized']
		percentage_done = _Utilities.get_percentage_done(months_initialized,total_months_to_initialize,logger=logger)
		return percentage_done		
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

# Update taxpayer initialization status
def update_taxpayer_initialization_status(taxpayer,new_initialization_data,logger=None,initialized=False):
	try:
		taxpayer['data']['initialization'] = new_initialization_data
		if initialized == True:
			taxpayer['status'] = _Constants.SYNCHRONIZATION
		else:
			taxpayer['data']['months_initialized'] = taxpayer['data']['months_initialized'] + 1
		percentage_initialized = get_initialization_percentage_done(taxpayer)
		taxpayer['data']['percentage_initialized'] = percentage_initialized
		forest_db = _Utilities.set_connection_to_forest_db()
		db_Taxpayer = forest_db['Taxpayer']
		db_Taxpayer.save(taxpayer)
		return taxpayer	
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

STATUS_DATES = _Constants.STATUS_DATES

def update_initialization_data_for_taxpayer(taxpayer,initialization_execution_log,logger=None):
	try:
		forest_db = _Utilities.set_connection_to_forest_db()
		db_Taxpayer = forest_db['Taxpayer']
		# Update sl1 success execution date:
		init_date = STATUS_DATES['initialization']
		initialization_date = Datetime.now()
		taxpayer[init_date] = initialization_date
		# Update synchronization logs:
		identifier = taxpayer['identifier']
		begin_date = taxpayer['start_date']#Since taxpayer claim to be synchronized
		begin_date = begin_date.replace(hour=0, minute=0)
		end_date = initialization_date# Until now
		cfdis_in_forest_db_count = _Utilities.get_cfdis_count_in_forest_for_this_taxpayer_at_period(taxpayer,begin_date,end_date)
		initialization_log = {
			'temporal_data' : {
				'completed_date' : initialization_date,
				'period' : {
					'year' : int(initialization_execution_log['year_initialized']),
					'month' : int(initialization_execution_log['month_initialized'])
				},
			},
			'cfdis' : {
				'new' : initialization_execution_log['stored'],
				'updated' : 0,
				'total' : cfdis_in_forest_db_count
			}# End of synchronization_log
		}# End of initialization_log
		taxpayer_logs = taxpayer['logs'] if 'logs' in taxpayer else {}
		taxpayer_initialization_logs = taxpayer_logs[_Constants.INITIALIZATION] if _Constants.INITIALIZATION in taxpayer_logs else []
		taxpayer_initialization_logs.append(initialization_log)
		taxpayer_logs[_Constants.INITIALIZATION] = taxpayer_initialization_logs
		taxpayer['logs'] = taxpayer_logs
		db_Taxpayer.save(taxpayer)		
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception


















