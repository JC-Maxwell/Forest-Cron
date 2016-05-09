# -*- coding: utf-8 -*-

# ██╗   ██╗████████╗██╗██╗     ██╗████████╗██╗███████╗███████╗
# ██║   ██║╚══██╔══╝██║██║     ██║╚══██╔══╝██║██╔════╝██╔════╝
# ██║   ██║   ██║   ██║██║     ██║   ██║   ██║█████╗  ███████╗
# ██║   ██║   ██║   ██║██║     ██║   ██║   ██║██╔══╝  ╚════██║
# ╚██████╔╝   ██║   ██║███████╗██║   ██║   ██║███████╗███████║
#  ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝   ╚═╝   ╚═╝╚══════╝╚══════╝

# Description: set of general functions and utilities for Forest-Cron

# ======================================================== DEPENDENCIES

# Native:
from __future__ import division
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import math
import multiprocessing
from datetime import datetime as Datetime
from datetime import date as Date
import signal
import datetime
from dateutil.relativedelta import *

# Pauli SDK dependency:
from pauli_sdk.Modules import constants as _Pauli_Constants
from pauli_sdk.Modules import helper as _Pauli_Helper
from pauli_sdk.Classes.response import Error
from pauli_sdk.Classes.response import Already_Handled_Exception

# Development:
from General import constants as _Constants
from General import config as _General_Config
from Processes.Synchronization_layer_1 import config as _SL1_Config
from Processes.Equalization import config as _Equalization_Config
SL1_LOGGING_CONFIG = _SL1_Config.synchronization_layer_1['logging']
EQUALIZATION_LOGGING_CONFIG = _Equalization_Config.equalization['logging']
# External:
from pymongo import MongoClient 
import telegram

FOREST_BOT_TELEGRAM_TOKEN = _Constants.FOREST_BOT_TELEGRAM_TOKEN
telegram_forest_bot = telegram.Bot(token=FOREST_BOT_TELEGRAM_TOKEN)

# ======================================================== CODE

LOG_INDENT = _Constants.LOG_INDENT

# ______           _                       _             
# |  ___|         | |                     (_)            
# | |_ ___  _ __  | |     ___   __ _  __ _ _ _ __   __ _ 
# |  _/ _ \| '__| | |    / _ \ / _` |/ _` | | '_ \ / _` |
# | || (_) | |    | |___| (_) | (_| | (_| | | | | | (_| |
# \_| \___/|_|    \_____/\___/ \__, |\__, |_|_| |_|\__, |
#                               __/ | __/ |         __/ |
#                              |___/ |___/         |___/ 

# Description: functions that supports write/update/read logs

LOGGING_LEVELS = _Constants.LOGGING_LEVELS
CRON_LOGGING_CONFIG = _General_Config.general['logging']

# Set up a logger (where to log)
def setup_logger(name,path=CRON_LOGGING_CONFIG['path'],file_name=CRON_LOGGING_CONFIG['file_name'],file_extension=CRON_LOGGING_CONFIG['file_extension'],format=CRON_LOGGING_CONFIG['format'],level=CRON_LOGGING_CONFIG['level']):
	try:
		# Logger data:
		file_name = file_name + file_extension
		complete_file_name = path + '/' + file_name
		logging_level = LOGGING_LEVELS[level]
		if format is not None:
			formatter = logging.Formatter(format,'%Y-%m-%d %H:%M:%S')
		else:
			formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(module)s - %(funcName)s:%(lineno)d - %(message)s','%Y-%m-%d %H:%M:%S')	
		# Defines logging handler:
		logging_handler = TimedRotatingFileHandler(complete_file_name, when='midnight')
		logging_handler.setFormatter(formatter)
		# Get logger:
		logger = logging.getLogger(name)
		logger.setLevel(logging_level)		
		logger.addHandler(logging_handler)
		return logger		
	except Exception as e:
		print 'Error setting up logger'
		print e
		raise e

# Get a logger (wher to log)
def get_logger(name):
	try:
		logger = logging.getLogger(name)
		return logger
	except:
		print 'Error getting logger'
		print e
		raise e

# Get specific process logger:
def get_subprocess_logger(process_name,_Process_Config,logger=None):
	try:
		subprocess_logger_path = _Process_Config['process_path'] + _Constants.THREADS_DIR
		setup_logger(process_name,path=subprocess_logger_path,file_name=process_name)
		subprocess_logger = get_logger(process_name)
		return subprocess_logger
	except Exception as e:
		logger.critical('Logger for subprocess ' + process_name + ' could not be obtained')
		logger.critical(e)
		raise e

CRON_PROCESSES_TABLE_TITLES = CRON_LOGGING_CONFIG['table_titles']
CRON_PROCESSES_TABLE_FIELD_LENGTHS = CRON_LOGGING_CONFIG['table_lengths']
CRON_PROCESSES_DEFAULT_LOG = {}
for key in CRON_PROCESSES_TABLE_TITLES:
	CRON_PROCESSES_DEFAULT_LOG[key] = ''
COMPLETED = CRON_LOGGING_CONFIG['completed_symbol']

# Update table log for all Forest-Cron processes called:
def log_at_cron_processes(process):
	try:
		process_name = process['name']
		# Log table:
		forest_db = set_connection_to_forest_db()
		db_Process = forest_db['Process']
		cron_processes_logger = get_logger('cron_processes')
		cron_processes_log = get_db_process(_Constants.CRON_PROCESSES)
		cron_processes_log['table_row_counter'] = cron_processes_log['table_row_counter'] + 1
		if cron_processes_log['table_row_counter'] >= CRON_LOGGING_CONFIG['table_row_limit']:
			cron_processes_log['table_row_counter'] = 0
			begin_table_row = format_log(CRON_PROCESSES_TABLE_TITLES,CRON_PROCESSES_TABLE_FIELD_LENGTHS,begin=True)	
			cron_processes_logger.info('',extra=begin_table_row)
		db_Process.save(cron_processes_log)
		cron_processes_execution_log = add_defalut_data_to_default_log(CRON_PROCESSES_DEFAULT_LOG)
		cron_processes_execution_log[process_name] = COMPLETED
		cron_processes_execution_log = format_log(cron_processes_execution_log,CRON_PROCESSES_TABLE_FIELD_LENGTHS)
		cron_processes_logger.info('',extra=cron_processes_execution_log)
	except Exception as e:
		cron_processes_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

DEFAULT_LOG_DATA = {
	'date' : 13,
	'hour' : 10,
	'process_name' : 12
}# End of DEFAULT_LOG_DATA

def add_defalut_data_to_default_log(default_log,logger=None):
	try:
		current_date = Datetime.now()
		default_log['date'] = str(current_date)[:10]
		default_log['hour'] = str(current_date)[10:-7]
		default_log['process_name'] = multiprocessing.current_process().name
		for key in DEFAULT_LOG_DATA:
			if key in default_log:
				value = default_log[key]
				value = str(value)
				value_length = DEFAULT_LOG_DATA[key]
				value = value.center(value_length,' ')
				default_log[key] = value
		return default_log
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
			already_handled_exception = Already_Handled_Exception(e.message)
			raise already_handled_exception

def format_log(execution_log,table_field_lengths,end=False,begin=False):
	try:
		execution_log_formated = {}
		for key in table_field_lengths:
			value = execution_log[key]
			value = str(value)
			value_length = table_field_lengths[key]
			if end == True or begin == True:
				value = value.center(value_length,'-')
			else:
				value = value.center(value_length,' ')
			execution_log_formated[key] = value
		if 'end_message' in execution_log:
			execution_log_formated['end_message'] = execution_log['end_message']
		if 'end' in execution_log:
			execution_log_formated['end'] = execution_log['end']
		return execution_log_formated
	except Exception as e:
		equalization_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

# ______                           _ _   _                                   _               
# |  ___|                         | | | (_)                                 (_)            _ 
# | |_ ___  _ __   _ __ ___  _   _| | |_ _ _ __  _ __ ___   ___ ___  ___ ___ _ _ __   __ _(_)
# |  _/ _ \| '__| | '_ ` _ \| | | | | __| | '_ \| '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  
# | || (_) | |    | | | | | | |_| | | |_| | |_) | | | (_) | (_|  __/\__ \__ \ | | | | (_| |_ 
# \_| \___/|_|    |_| |_| |_|\__,_|_|\__|_| .__/|_|  \___/ \___\___||___/___/_|_| |_|\__, (_)
#                                         | |                                         __/ |  
#                                         |_|                                        |___/   

# Description: functions that supports multiprocesses (multithreading)

# Receives taxpayers and spread them into taxpayers subprocesses (dictionaries) that contains data for executing in parallel eventually:
def get_taxpayers_subprocesses(taxpayers,process_name,number_of_subprocesses):
	try:
		taxpayers_subprocesses = []
		total_taxpayers = len(taxpayers)
		taxpayers_per_subprocess = math.ceil(total_taxpayers/number_of_subprocesses)
		if taxpayers_per_subprocess == 0:
			taxpayers_per_subprocess = 1
		subprocess_index = 0
		while subprocess_index < number_of_subprocesses:
			subprocess_taxpayers = []
			taxpayer_begin_index = int(subprocess_index*taxpayers_per_subprocess)
			taxpayer_end_index = int(taxpayer_begin_index + taxpayers_per_subprocess)
			if taxpayer_end_index > total_taxpayers:
				taxpayer_end_index = total_taxpayers# Fix range in the last iteration
			for taxpayer_index in range(taxpayer_begin_index,taxpayer_end_index):
				taxpayer = taxpayers[taxpayer_index]
				subprocess_taxpayers.append(taxpayer)
				taxpayers_in_this_subprocess = len(subprocess_taxpayers)
				missing_taxpayers = total_taxpayers - taxpayer_end_index
				if taxpayers_in_this_subprocess == taxpayers_per_subprocess:
					break
			if len(subprocess_taxpayers) > 0:
				subprocess_name = process_name + '-' + str(subprocess_index+1)
				taxpayer_subprocess = new_taxpayers_subprocess(subprocess_taxpayers,subprocess_name)
				taxpayers_subprocesses.append(taxpayer_subprocess)
			subprocess_index = subprocess_index + 1
		return taxpayers_subprocesses
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Creates a new taxpayer subprocess (dictionary with subprocess data):
def new_taxpayers_subprocess(taxpayers,subprocess_name):
	try:
		subprocess = {
			'taxpayers' : taxpayers,
			'name' : subprocess_name
		}# End of subprocess
		return subprocess
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Log taxpayer subprocesses
def log_taxpayers_subprocesses(processes,logger,indent=LOG_INDENT,default_log={}):
	try:
		logger.info(indent + 'Building threads ...  ',extra=default_log)
		for subprocess in processes:
			# Subprocess params:
			taxpayers = subprocess['taxpayers']
			number_of_taxpayers_in_this_process = len(taxpayers)
			subprocess_name = subprocess['name']
			logger.info(indent + indent + str(subprocess_name) + ' with ' + str(number_of_taxpayers_in_this_process) + ' taxpayers',extra=default_log)
	except Exception as e:
		logger.critical(e.message,extra=default_log)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Execute subprocesses in parallel:
def execute_taxpayers_subprocesses_in_parallel(processes,process_function,shared_variables={},starting_message=None,logger=None,indent=LOG_INDENT,default_log={}):
	try:
		if starting_message is None:
			starting_message = 'PROCESS DETAILS: '
		if logger is not None:
			logger.info(indent + 'Executing ' + str(len(processes)) + ' in parallel ... ',extra=default_log)
		python_processes = []
		i = 0
		for subprocess in processes:
			i = i + 1
			# Subprocess params:
			target = process_function# Execute this function
			taxpayers = subprocess['taxpayers']# With this taxpayers
			subprocess_name = subprocess['name']# With this name (just for control)
			args = (taxpayers,shared_variables,)
			if logger is not None:
				logger.info(indent + indent + str(i) + '. ' + str(subprocess_name),extra=default_log)
			python_multiprocess = multiprocessing.Process(name=subprocess_name,target=target,args=args)
			python_multiprocess.start()
			python_processes.append(python_multiprocess)
		i = 0
		if logger is not None:
			# logger.info(' ')
			# logger.info(_Constants.LOG_SEPARATOR,extra=default_log)
			logger.info(starting_message,extra=default_log)
			# logger.info(' ')
			# logger.info(indent + 'Waiting for processes: ')
		for python_process in python_processes:
			i = i + 1
			# if logger is not None:
				# logger.info(indent + indent + str(i) + '. ' + str(python_process.name))
			python_process.join()# Wait for all processes to finish
	except Exception as e:
		logger.critical(e.message,extra=default_log)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# ______                  _    ____________   
# |  ___|                | |   |  _  \ ___ \_ 
# | |_ ___  _ __ ___  ___| |_  | | | | |_/ (_)
# |  _/ _ \| '__/ _ \/ __| __| | | | | ___ \  
# | || (_) | | |  __/\__ \ |_  | |/ /| |_/ /_ 
# \_| \___/|_|  \___||___/\__| |___/ \____/(_)                                         
                            
# Description: Fores't connection

# Set connection to forest's db:
def set_connection_to_forest_db():
	try:
		DB_HOST = 'mongodb://mikemachine:kikinazul@ds033121-a0.mongolab.com:33121,ds033121-a1.mongolab.com:33121/forest'# Domain of our DB or mongoDB URI
		DB_PORT = 33121# DB port (a number)
		DB_NAME = 'forest'# Mongo data base name
		mongo = MongoClient(DB_HOST,DB_PORT)
		db = mongo[DB_NAME]
		return db# Mongo db object
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# ______           _____                                            
# |  ___|         |_   _|                                         _ 
# | |_ ___  _ __    | | __ ___  ___ __   __ _ _   _  ___ _ __ ___(_)
# |  _/ _ \| '__|   | |/ _` \ \/ / '_ \ / _` | | | |/ _ \ '__/ __|  
# | || (_) | |      | | (_| |>  <| |_) | (_| | |_| |  __/ |  \__ \_ 
# \_| \___/|_|      \_/\__,_/_/\_\ .__/ \__,_|\__, |\___|_|  |___(_)
#                                | |           __/ |                
#                                |_|          |___/                 

# Description: Functions for handling taxpayers

FILTERS_BY_PROCESS_NAMES = _Constants.FILTERS_BY_PROCESS_NAMES

def update_taxpayer_firmware_timeout(taxpayer,logger=None):
	try:
		forest_db = set_connection_to_forest_db()
		db_Taxpayer = forest_db['Taxpayer']
		current_timeout = taxpayer['firmware_timeout'] if 'firmware_timeout' in taxpayer else _Constants.DEFAULT_FIRMWARE_TIMEOUT
		new_timeout = int(current_timeout*_Constants.UPDATING_FIRMWARE_TIMEOUT_RATE)
		if logger is not None:
			logger.info(3*LOG_INDENT + 'Updating timeout from ' + str(current_timeout) + 'secs to ' + str(new_timeout) + ' secs')
		taxpayer['firmware_timeout'] = new_timeout
		db_Taxpayer.save(taxpayer)
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def validate_forcing_identifiers(forcing_identifiers,process_name,logger=None):
	try:
		print 'Validating identifiers ... '
		if logger is not None:
			logger.info(LOG_INDENT + 'Validating identifiers ... ')
		process_name_filter = FILTERS_BY_PROCESS_NAMES[process_name]
		forest_db = set_connection_to_forest_db()
		db_Taxpayer = forest_db['Taxpayer']
		all_are_valid = True
		i = 0
		for identifier in forcing_identifiers:
			i = i + 1
			process_name_filter['identifier'] = identifier
			it_exists = db_Taxpayer.find(process_name_filter).count()
			if it_exists and it_exists == 1:
				all_are_valid = all_are_valid and True
				message = 2*LOG_INDENT + str(i) + '. ' + identifier + ' is valid'
				if logger is not None:
					logger.info(message)
				print message
			else:
				all_are_valid = all_are_valid and False
				message = 2*LOG_INDENT + str(i) + '. ' + identifier + ' is not valid'
				if logger is not None:
					logger.info(message)
				print message
		return all_are_valid
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def validate_params(process_params,logger=None):
	try:
		is_month = 'month' in process_params
		is_year = 'year' in process_params
		if is_month or is_year:
			if is_month and is_year:
				month = process_params['month']
				year = process_params['year']
				months = range(1,13)
				current_year = Datetime.now().year
				years = range(2013,current_year+1)
				if month not in months:
					print 'Invalid month param equal to ' + str(month) + ', it must be in ' + str(months)
					return False
				if year not in years:
					print 'Invalid year param equal to ' + str(year) + ', it must be in ' + str(years)
					return False
				process_params['month'] = u"%02d" % (process_params['month'],)
				process_params['year'] = unicode(process_params['year'])
				return True	
			else:
				print 'Month and year params must exist (both of them)'
				return False
		else:
			return True
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Retrieve all taxpayers that must be iterated in a specific process (i.e. syncrhonizing, initializing, updating and so on)
def get_taxpayers_for_a_specific_process(process_name,forcing_identifiers=None,limit=None,from_taxpayer=None,logger=None,debug_execution=False,server_index=None,mode=None):
	try:
		process_name_filter = FILTERS_BY_PROCESS_NAMES[process_name]
		if debug_execution is True:
			if logger is not None:
				logger.info(LOG_INDENT + 'Retrieving debug taxpayers for ' + process_name + ' process')
			process_name_filter['debug'] = True
		if process_name == 'equalization' or process_name == 'synchronization_layer_1':
			last_session_lower_limit = datetime.datetime.now() - relativedelta(months=2)
			if logger is not None:
				logger.info(LOG_INDENT + 'Adding last session filter to ' + str(last_session_lower_limit))
			process_name_filter['last_session'] = { '$gt' : last_session_lower_limit }
		if forcing_identifiers is not None:
			if logger is not None:
				logger.info(LOG_INDENT + 'Adding forcing taxpayers filter')
			process_name_filter['identifier'] = {
				'$in' : forcing_identifiers
			}#End of forcing_identifiers
		forest_db = set_connection_to_forest_db()
		db_Taxpayer = forest_db['Taxpayer']
		if limit is not None and from_taxpayer is None:
			db_taxpayers = db_Taxpayer.find(process_name_filter).limit(limit).sort('created_at',1)
		else:
			db_taxpayers = db_Taxpayer.find(process_name_filter).sort('created_at',1)
		taxpayers = []
		from_taxpayer = None#from taxpayer was deprecated in multi-server version 0.1 (may 4 2016)
		if logger is not None:
			logger.info(LOG_INDENT + 'From taxpayer is DEPRECATED')	
		if from_taxpayer is not None:
			from_here = False
			for db_taxpayer in db_taxpayers:
				if db_taxpayer['identifier'] == from_taxpayer:# Functions because they are sorted
					from_here = True
				if from_here:
					taxpayer = create_new_taxpayer(db_taxpayer,logger=logger)
					taxpayers.append(taxpayer)
					if limit is not None:
						if len(taxpayers) > limit:
							break
		else:
			for db_taxpayer in db_taxpayers:
				taxpayer = create_new_taxpayer(db_taxpayer,logger=logger)
				taxpayers.append(taxpayer)
		if logger is not None:
			logger.info(LOG_INDENT + 'Total taxpayers: ' + str(len(taxpayers)))	
		if forcing_identifiers is not None:
			if logger is not None:
				logger.info(LOG_INDENT + 'Forcing execution will not be filtered')
			return taxpayers
		# In balancer mode all taxpayers must be retrieved, they are just filtered if process is in server mode
		if mode is not _Constants.BALANCER_MODE and server_index is not None and process_name is not _Constants.EQUALIZATION:# Once taxpayers were retrieved and filtered according to "from_taxpayer" param they are filtered by server index, Equalization process only runs at BALANCER mode (in balancer server)
			if logger is not None:
				logger.info(LOG_INDENT + 'Total taxpayers pending: ' + str(len(taxpayers)))	
			if logger is not None:
				logger.info(LOG_INDENT + 'Filtering for server: ' + str(server_index))
			server_taxpayers = []
			for taxpayer in taxpayers:
				if 'server_index' in taxpayer and taxpayer['server_index'] == server_index:
					server_taxpayers.append(taxpayer)
			if logger is not None:
				logger.info(LOG_INDENT + 'Total taxpayers pending on this server: ' + str(len(server_taxpayers)))
			taxpayers = server_taxpayers
		if process_name is _Constants.EQUALIZATION:
			if logger is not None:
				logger.info(LOG_INDENT + 'Equalization process will not be filtered')
		return taxpayers
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Create a new taxpayer dict:
def create_new_taxpayer(db_taxpayer,logger=None):
	try:
		new_taxpayer = {# Building a new dict avoids cursor invalidation at server
			'_id' : db_taxpayer['_id'],
			'status' : db_taxpayer['status'],
			'password' : db_taxpayer['password'],
			'identifier' : db_taxpayer['identifier'],
			'logs' : db_taxpayer['logs'] if 'logs' in db_taxpayer else None,
			'created_at' : db_taxpayer['created_at'],
			'last_sl1' : db_taxpayer['last_sl1'] if 'last_sl1' in db_taxpayer else None,
			'firmware_timeout' : db_taxpayer['firmware_timeout'] if 'firmware_timeout' in db_taxpayer else None,
			'initialized_at' : db_taxpayer['initialized_at'] if 'initialized_at' in db_taxpayer else None,
			'data' : db_taxpayer['data'] if 'data' in db_taxpayer else None,
			'start_date' : db_taxpayer['start_date'],
			'server_index' : db_taxpayer['server_index'] if 'server_index' in db_taxpayer else None
		}#End of new_taxpayer
		if 'last_session' in db_taxpayer:
			new_taxpayer['last_session'] = db_taxpayer['last_session']
		if 'debug' in db_taxpayer:
			new_taxpayer['debug'] = db_taxpayer['debug']
		return new_taxpayer
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

STATUS_DATES = _Constants.STATUS_DATES

# Update taxpayer status:
def update_taxpayer_status(taxpayer,process_constant,logger=None):
	try:
		forest_db = set_connection_to_forest_db()
		db_Taxpayer = forest_db['Taxpayer']
		date_field = STATUS_DATES[process_constant]
		taxpayer[date_field] = Datetime.now()
		db_Taxpayer.save(taxpayer)
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# This update is for balancing each thread in a different server (introduced on May 3rd 2016)
def update_taxpayers_server_index(identifiers,index,logger=None):# The index if the server in which this taxpayers (identfiers) will be processed
	try:
		forest_db = set_connection_to_forest_db()
		db_Taxpayer = forest_db['Taxpayer']
		taxpayer_filter = {
			'identifier' : {
				'$in' : identifiers
			}#End of identifier
		}#End of taxpayer_filter
		taxpayer_update = {
			'$set' : {
				'server_index' : index
			}#End of $set
		}#End of taxpayer_update
		db_update_result = db_Taxpayer.update(taxpayer_filter,taxpayer_update,multi=True)	
		return db_update_result
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# ______           _____ ____________ _____      
# |  ___|         /  __ \|  ___|  _  \_   _|   _ 
# | |_ ___  _ __  | /  \/| |_  | | | | | | ___(_)
# |  _/ _ \| '__| | |    |  _| | | | | | |/ __|  
# | || (_) | |    | \__/\| |   | |/ / _| |\__ \_ 
# \_| \___/|_|     \____/\_|   |___/  \___/___(_)
 
# Create a new CFDI in Forest DB:
def create_cfdi(new_cfdi,logger=None,log=None,forest_db=None):
	try:
		if forest_db is None:
			forest_db = set_connection_to_forest_db()
		db_CFDI = forest_db['CFDI']
		uuid = new_cfdi['uuid'].upper()
		# Build new db cfdi:
		db_new_cfdi = {
			'uuid': uuid,
			'buyer': new_cfdi['buyer'],
			'seller': new_cfdi['seller'],
			'status': new_cfdi['status'],
			'voucher_effect' : new_cfdi['voucher_effect'] if 'voucher_effect' in new_cfdi else None
		}#End of db_ne_cfdi
		if 'simulated' in new_cfdi and new_cfdi['simulated'] == True:
			db_new_cfdi['certification_date'] = new_cfdi['certification_date']# It comes from db -- date is already parsed -- 
			db_new_cfdi['issued_date'] = new_cfdi['issued_date']
		else:
			db_new_cfdi['certification_date'] = sat_date_to_ISODate(new_cfdi['certification_date'])
			db_new_cfdi['issued_date'] = sat_date_to_ISODate(new_cfdi['issued_date'])
		# Get xml data:
		xml = new_cfdi['xml']
		if xml is not None and xml != '':#bug_solved, xml was '' and it causes errors in cfdi_type, currency and taxes
			cfdi_type = get_cfdi_type(xml,logger=logger)
			validation = _Pauli_Helper.validate_xml(xml)
			xml_warnings = validation['warnings']
			xml_invalidations = validation['invalidations']
			db_new_cfdi['xml'] = xml
			db_new_cfdi['validated'] = True  if validation['validated'] else False
			db_new_cfdi['details'] = {
				'invalidations' : xml_invalidations,
				'warnings' : xml_warnings
			}#End of details
			db_new_cfdi['cfdi_type'] = cfdi_type# It says if cfdi is a credit_note, payroll or normal
			currency = _Pauli_Helper.get_currency(xml,logger=logger)
			if currency is not None:
				db_new_cfdi['currency'] = currency
			else:
				db_new_cfdi['currency'] = 'mxn'# Default
			taxes_included = _Pauli_Helper.get_taxes_included_in_this_CFDI(xml,logger=logger)
			db_new_cfdi['_wl_ish'] = taxes_included['_wl_ish'] if taxes_included['_wl_ish'] is not None else False
			db_new_cfdi['_t_iva_16'] = taxes_included['_t_iva_16'] if taxes_included['_t_iva_16'] is not None else False
			db_new_cfdi['_t_iva_0'] = taxes_included['_t_iva_0'] if taxes_included['_t_iva_0'] is not None else False
			db_new_cfdi['_w_iva_10'] = taxes_included['_w_iva_10'] if taxes_included['_w_iva_10'] is not None else False
			db_new_cfdi['_w_isr'] = taxes_included['_w_isr'] if taxes_included['_w_isr'] is not None else False
			db_new_cfdi['_tl_ish'] = taxes_included['_tl_ish'] if taxes_included['_tl_ish'] is not None else False
			db_new_cfdi['_t_ieps'] = taxes_included['_t_ieps'] if taxes_included['_t_ieps'] is not None else False
			log['forest_db']['after']['new'] = log['forest_db']['after']['new'] + 1
		elif new_cfdi['status'] == _Constants.CANCELED_STATUS:
			# db_new_cfdi['xml'] = _Helper.build_default_xml(db_new_cfdi['seller'],db_new_cfdi['buyer'],db_new_cfdi['certification_date'],db_new_cfdi['issued_date'],db_new_cfdi['voucher_effect'],db_new_cfdi['uuid'])
			log['forest_db']['after']['new'] = log['forest_db']['after']['new'] + 1
		else:
			log['forest_db']['after']['pending'] = log['forest_db']['after']['pending'] + 1
		db_CFDI.insert(db_new_cfdi)
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Get the existing uuids (already exists in Forest DB and they have xml):
def get_existing_uuids_in_forest_db(cfdis_in_db=None,logger=None):
	try:
		existing_cfdi_uuids = []
		for cfdi_in_db in cfdis_in_db:
			uuid = cfdi_in_db['uuid']
			status = cfdi_in_db['status']
			existing_uuid = {
				'uuid' : uuid,
				'status' : status
			}# End of existing_uuid
			existing_cfdi_uuids.append(existing_uuid)
		number_of_existing_cfdi_uuids = len(existing_cfdi_uuids)
		return existing_cfdi_uuids
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception
		
def log_cfdis_uuids(title=None,indent=None,cfdis=None,logger=None,dict=False):
	try:
		logger.info(title)
		n = 0
		for ref in cfdis:
			if dict == True:
				uuid = ref
			else:
				uuid = ref['uuid']
			n = n + 1
			logger.info(indent + str(n) + '. ' + uuid)
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def get_cfdis_count_in_forest_for_this_taxpayer_at_period(taxpayer,begin_date,end_date):
	try:
		taxpayer_indentifier = taxpayer['identifier']
		forest_db = set_connection_to_forest_db()
		db_CFDI = forest_db['CFDI']
		cfdis_in_db = []
		cfdis_issued_in_db = db_CFDI.find({ 'xml' : { '$exists' : True, '$ne' : '' }, 'seller': taxpayer['identifier'], 'certification_date':  {'$gte': begin_date, '$lte': end_date} }).count()
		cfdis_received_in_db = db_CFDI.find({ 'xml' : { '$exists' : True, '$ne' : '' }, 'buyer': taxpayer['identifier'], 'certification_date': {'$gte': begin_date, '$lte': end_date} }).count()
		cfdis_count = cfdis_issued_in_db + cfdis_received_in_db
		return cfdis_count
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def get_cfdis_in_forest_for_this_taxpayer_at_period(taxpayer,begin_date,end_date,limit=None,logger=None,dict_result=False):
	try:
		taxpayer_indentifier = taxpayer['identifier']
		forest_db = set_connection_to_forest_db()
		db_CFDI = forest_db['CFDI']
		cfdis_in_db = []
		if limit is None:
			cfdis_issued_in_db = db_CFDI.find({ 'xml' : { '$exists' : True, '$ne' : '' }, 'seller': taxpayer['identifier'], 'certification_date':  {'$gte': begin_date, '$lte': end_date} })
			cfdis_received_in_db = db_CFDI.find({ 'xml' : { '$exists' : True, '$ne' : '' }, 'buyer': taxpayer['identifier'], 'certification_date': {'$gte': begin_date, '$lte': end_date} })
		else:
			cfdis_issued_in_db = db_CFDI.find({ 'xml' : { '$exists' : True, '$ne' : '' }, 'seller': taxpayer['identifier'], 'certification_date':  {'$gte': begin_date, '$lte': end_date} }).limit(limit)
			cfdis_received_in_db = db_CFDI.find({ 'xml' : { '$exists' : True, '$ne' : '' }, 'buyer': taxpayer['identifier'], 'certification_date': {'$gte': begin_date, '$lte': end_date} }).limit(limit)
		for cfdi_issued_in_db in cfdis_issued_in_db:
			cfdis_in_db.append(cfdi_issued_in_db)
		for cfdi_received_in_db in cfdis_received_in_db:
			cfdis_in_db.append(cfdi_received_in_db)
		if dict_result == True:
			cfdis_in_forest_db_dict = {}
			for cfdi_in_db in cfdis_in_db:
				uuid = cfdi_in_db['uuid']
				if not uuid in cfdis_in_forest_db_dict:
					cfdis_in_forest_db_dict[uuid] = cfdi_in_db
			return cfdis_in_forest_db_dict
		return cfdis_in_db
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def get_pending_cfdis_in_forest_for_this_taxpayer_at_period(taxpayer,begin_date,end_date):
	try:
		taxpayer_indentifier = taxpayer['identifier']
		forest_db = set_connection_to_forest_db()
		db_CFDI = forest_db['CFDI']
		pending_cfdis_in_db = []
		pending_cfdis_issued_in_db = db_CFDI.find({ 'xml' : { '$exists' : False }, 'seller': taxpayer['identifier'], 'certification_date':  {'$gte': begin_date, '$lte': end_date} })
		pedning_cfdis_received_in_db = db_CFDI.find({ 'xml' : { '$exists' : False }, 'buyer': taxpayer['identifier'], 'certification_date': {'$gte': begin_date, '$lte': end_date} })
		for pending_cfdi_issued_in_db in pending_cfdis_issued_in_db:
			pending_cfdis_in_db.append(pending_cfdi_issued_in_db)
		for pending_cfdi_received_in_db in pedning_cfdis_received_in_db:
			pending_cfdis_in_db.append(pending_cfdi_received_in_db)
		return pending_cfdis_in_db
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Return whether xml (CFDI) is a normal CFDI, payroll or credit note:
def get_cfdi_type(cfdi_xml,logger=None):
	try:
		cfdi_type = ''
		xml_element = _Pauli_Helper.get_xml_element_from_xml(cfdi_xml)
		xml_element_attributes = xml_element.attrib
		payroll = is_a_payroll(xml_element,logger=logger)# return boolean
		voucher_effect = xml_element_attributes['tipoDeComprobante']
		if payroll:
			cfdi_type = _Constants.PAYROLL_CFDI_TYPE
		elif not payroll and voucher_effect == _Constants.EXPENSE_VOUCHER_EFFECT:
			cfdi_type = _Constants.CREDIT_NOTE_CFDI_TYPE
		elif not payroll and voucher_effect == _Constants.TRANSFERRED_VOUCHER_EFFECT:
			cfdi_type = _Constants.TRANSPORT_DOCUMENT_CFDI_TYPE
		else: 
			cfdi_type = _Constants.NORMAL_CFDI_TYPE
		return cfdi_type
	except Exception as e:
		if logger is not None:
			logger.info(e)

def is_a_payroll(xml_element,execution_data=None,logger=None):
	try:
		is_a_payroll = False
		payroll_element = _Pauli_Helper.get_specific_element_from_a_xml_element(xml_element,'nomina')
		if payroll_element is not None:
			is_a_payroll = True
		return is_a_payroll
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except:
		other_exception = str(sys.exc_info()[1])
		other_error = Error(_Pauli_Constants.HTTP_CODES['INTERNAL'],_Pauli_Constants.ERROR_MESSAGES['INTERNAL'])
		if logger is not None:
			logger.critical(other_error.content + other_exception)
		already_handled_exception = Already_Handled_Exception(other_error)
		raise already_handled_exception

# ______                                               
# |  ___|                                            _ 
# | |_ ___  _ __   _ __  _ __ ___   ___ ___  ___ ___(_)
# |  _/ _ \| '__| | '_ \| '__/ _ \ / __/ _ \/ __/ __|  
# | || (_) | |    | |_) | | | (_) | (_|  __/\__ \__ \_ 
# \_| \___/|_|    | .__/|_|  \___/ \___\___||___/___(_)
#                 | |                                  
#                 |_|                                  

def update_current_taxpayer(process_name,current_taxpayer,current_taxpayer_index,logger=None):
	try:
		process = get_db_process(process_name,logger=logger)
		process['current_taxpayer'] = current_taxpayer
		process['current_taxpayer_index'] = current_taxpayer_index
		process['current_taxpayer_triggered'] = Datetime.now()
		if not 'total_taxpayers' in process:
			process['total_taxpayers'] = 1# Just a bug
		process['percentage_done'] = get_percentage_done(process['current_taxpayer_index'],process['total_taxpayers'])
		forest_db = set_connection_to_forest_db()
		db_Process = forest_db['Process']
		db_Process.save(process)
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception  

def get_db_process(process_name,logger=None,db_Process=None):
	try:
		if db_Process is None:
			forest_db = set_connection_to_forest_db()
			db_Process = forest_db['Process']
		process_filter = { 'name' : process_name }
		process_exists = db_Process.find(process_filter).count()
		if process_exists:
			process = db_Process.find(process_filter)[0]
		else:
			process = new_process(process_name,logger=logger,db_Process=db_Process)
		return process
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def new_process(process_name,logger=None,db_Process=None):
	try:
		if db_Process is None:
			forest_db = set_connection_to_forest_db()
			db_Process = forest_db['Process']
		process = {
			'name' : process_name,
			'available' : True
		}# End of process
		db_Process.save(process)
		process_filter = { 'name' : process_name }
		process = db_Process.find(process_filter)[0]
		return process
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def set_process_unavailable(process_name,taxpayers=[],logger=None,db_Process=None,debug_execution=False,threads=None):
	try:
		if db_Process is None:
			forest_db = set_connection_to_forest_db()
			db_Process = forest_db['Process']
		process = get_db_process(process_name,logger=logger)
		if debug_execution is not True:# These attributes are updated just if it is not a debug execution
			process['last_triggered'] = Datetime.now()
			process['available'] = False
			process['could_server_start'] = DEFAULT_SERVERS
			if threads is not None:
				process['servers'] = threads
		process['total_taxpayers'] = len(taxpayers)
		process['percentage_done'] = '0.00%'
		db_Process.save(process)
		if debug_execution:
			process_availability = False# Just to seem it was set unavailable
		else:
			process_availability = process['available']
		return process_availability
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def set_process_available(process_name,process_duration=0,logger=None,db_Process=None,log_process_duration=False,debug_execution=False):
	try:
		if debug_execution is not True:
			if db_Process is None:
				forest_db = set_connection_to_forest_db()
				db_Process = forest_db['Process']
			process = get_db_process(process_name,logger=logger)
			process['last_completed'] = Datetime.now()
			if log_process_duration is True:
				executions_counter = process['executions_counter'] if 'executions_counter' in process else 0
				average_duration = process['average_duration'] if 'average_duration' in process else 0
				total_of_durations = average_duration*executions_counter
				new_total_of_durations = total_of_durations + process_duration
				process['executions_counter'] = executions_counter + 1
				process['average_duration'] = new_total_of_durations/process['executions_counter']
			process['available'] = True
			if 'current_taxpayer' in process:
				del process['current_taxpayer'] 
			if 'current_taxpayer_index' in process:
				del process['current_taxpayer_index']
			if 'current_taxpayer_triggered' in process:
				del process['current_taxpayer_triggered']
			if 'total_taxpayers' in process:
				del process['total_taxpayers']
			if 'percentage_done' in process:
				del process['percentage_done']
			db_Process.save(process)
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def set_process_server_available(process_name,server_index,logger=None,db_Process=None):
	try:
		if db_Process is None:
			forest_db = set_connection_to_forest_db()
			db_Process = forest_db['Process']
		process = get_db_process(process_name,logger=logger)
		server_index_str = str(server_index)
		process['servers_availability'][server_index_str] = True
		db_Process.save(process)
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def set_process_server_unavailable(process_name,server_index,logger=None,db_Process=None):
	try:
		if db_Process is None:
			forest_db = set_connection_to_forest_db()
			db_Process = forest_db['Process']
		process = get_db_process(process_name,logger=logger)
		server_index_str = str(server_index)
		process['servers_availability'][server_index_str] = False
		process['could_server_start'][server_index_str] = False
		db_Process.save(process)
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def check_process_availability(process_name,logger=None,db_Process=None,debug_execution=False):
	try:
		available = True
		if debug_execution is True:
			return available
		if db_Process is None:
			forest_db = set_connection_to_forest_db()
			db_Process = forest_db['Process']
		process = get_db_process(process_name,logger=logger)
		process_availability = process['available']
		if process_availability == True:
			available = True
		else:
			available = False
		process['last_requested'] = Datetime.now()
		db_Process.save(process)
		return available
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def check_process_server_availability(process_name,server_index,logger=None,db_Process=None,servers=None):
	try:
		if db_Process is None:
			forest_db = set_connection_to_forest_db()
			db_Process = forest_db['Process']
		process = get_db_process(process_name,logger=logger)
		servers_availability = process['servers_availability']
		could_server_start_by_index = process['could_server_start']
		server_index_str = str(server_index)
		could_server_start = could_server_start_by_index[server_index_str]
		server_availability = servers_availability[server_index_str]
		if servers_availability is True and could_server_start is True:
			available = True
		else:
			available = False
		return available
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def check_process_servers_availability(process_name,logger=None,db_Process=None):
	try:
		available = True
		if db_Process is None:
			forest_db = set_connection_to_forest_db()
			db_Process = forest_db['Process']
		process = get_db_process(process_name,logger=logger)
		servers = process['servers']
		servers_availability = process['servers_availability']
		all_servers_are_available = True
		logger.info(3*LOG_INDENT + 'Checking every server of ' + str(servers) + ' ... ')
		for server_index in range(1,servers+1):
			server_index_str = str(server_index)
			if server_index_str in servers_availability and servers_availability[server_index_str] is True:
				logger.info(3*LOG_INDENT + 'Server ' + server_index_str + ' availability: True')
				all_servers_are_available = all_servers_are_available and True
			else:
				logger.info(3*LOG_INDENT + 'Server ' + server_index_str + ' availability: False')
				all_servers_are_available = all_servers_are_available and False
		return all_servers_are_available
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def update_cron_process_log(process_in_turn,logger=None,db_Process=None,suspended_at=None,debug_execution=False):
	try:
		if debug_execution is False:
			if db_Process is None:
				forest_db = set_connection_to_forest_db()
				db_Process = forest_db['Process']
			process = get_db_process('cron',logger=logger)
			if suspended_at is None:
				if 'suspended_at' in process:
					del process['suspended_at']
				process['last_triggered'] = Datetime.now()
				process['process_in_turn'] = process_in_turn
				db_Process.save(process)
			elif not 'suspended_at' in process:
				process['suspended_at'] = Datetime.now()
				db_Process.save(process)
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

#  _____                _                 _     ____________   
# /  __ \              | |               | |    |  _  \ ___ \_ 
# | /  \/ ___  _ __ ___| |__   ___   ___ | | __ | | | | |_/ (_)
# | |    / _ \| '__/ _ \ '_ \ / _ \ / _ \| |/ / | | | | ___ \  
# | \__/\ (_) | | |  __/ |_) | (_) | (_) |   <  | |/ /| |_/ /_ 
#  \____/\___/|_|  \___|_.__/ \___/ \___/|_|\_\ |___/ \____/(_)                                                            
                                                                                                    
# Description: Corebook's connection and data

# Set connection to corebook's db:
def set_connection_to_corebook_db():
	try:
		DB_HOST = 'mongodb://mikemachine:kikinazul@ds033121-a0.mongolab.com:33121,ds033121-a1.mongolab.com:33121/corebook'# Domain of our DB or mongoDB URI
		DB_PORT = 33121# DB port (a number)
		DB_NAME = 'corebook'# Mongo data base name
		mongo = MongoClient(DB_HOST,DB_PORT)
		db = mongo[DB_NAME]
		return db# Mongo db object
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

#  _____ _   _                 
# |  _  | | | |              _ 
# | | | | |_| |__   ___ _ __(_)
# | | | | __| '_ \ / _ \ '__|  
# \ \_/ / |_| | | |  __/ |   _ 
#  \___/ \__|_| |_|\___|_|  (_)
                                                        
# Description: other functions

#Return the current period as an array of months e.g ["1","2"] is the first two month period of the year in course
def get_current_fiscal_declaration_period(period):
	try:
		today = Date.today();
		months_of_the_period = [];
		if period == _Constants.TWO_MONTHS_PERIOD:
			months_of_the_period.append(today.month);# First month
			if today.month != 1:# Always return current month and previous month (except in january)
				months_of_the_period.append(today.month-1)
		months_of_the_period = sorted(months_of_the_period)
		for i in range(len(months_of_the_period)):
			months_of_the_period[i] = str(months_of_the_period[i])
			if len(months_of_the_period[i]) == 1:
				months_of_the_period[i] = "0" + months_of_the_period[i]
		return months_of_the_period
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Return the number of date of a specific month (month is given in a string e.g. '01' for january):
def get_month_days(month):
	try:
		month_days = {
			'01': 31,
			'02': 28,
			'03': 31,
			'04': 30,
			'05': 31,
			'06': 30,
			'07': 31,
			'08': 31,
			'09': 30,
			'10': 31,
			'11': 30,
			'12': 31
		}# End of month days
		return month_days[month]
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Get percentage done of something:
def get_percentage_done(part_done,total,logger=None):
	try:
		if total == 0:
			total = 1 
		percentage_done = part_done*100/total
		return str(round(percentage_done,2)) + '%'
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Get percentage done of a taxpayer process:
def get_process_percentage_done(taxpayers_synchronized,total_taxpayers):
	try:
		if total_taxpayers == 0:
			total_taxpayers = 1 
		syncrhonization_process_percentage_done = taxpayers_synchronized*100/total_taxpayers
		return str(round(syncrhonization_process_percentage_done,2)) + '%'
	except Exception as e:
		# sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

#Convert a sat (web site) cfdi date to an ISO Date format:
def sat_date_to_ISODate(sat_date,logger=None):
	try:
		sat_date_elements = sat_date.split('-')
		year = int(sat_date_elements[0])
		month = int(sat_date_elements[1])
		sat_time_elements = sat_date_elements[2].split(':')
		date = int(sat_time_elements[0][0] + sat_time_elements[0][1])
		hour = int(sat_time_elements[0][3] + sat_time_elements[0][4])
		minutes = int(sat_time_elements[1])
		seconds = int(sat_time_elements[2])
		return Datetime(year,month,date,hour,minutes,seconds)
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def set_timeout(func, args=(), kwargs={}, timeout_duration=5, default=None):
	class TimeoutError(Exception):
		pass
	def handler(signum, frame):
		raise TimeoutError('TimeOut Exception')
	signal.signal(signal.SIGALRM, handler) 
	signal.alarm(timeout_duration)
	try:
		result = func(*args,**kwargs)
	except TimeoutError as exc:
		result = default
	except Exception as exc:
		result = default
	return result

def handle_forest_cron_error(error,logger=None):
	try:
		forest_db = set_connection_to_forest_db()
		db_Process = forest_db['Process']
		process = get_db_process('cron',logger=logger)
		notified_problem = process['data']['notifications']['notified_problem'] if 'notified_problem' in process['data']['notifications'] else None
		if notified_problem is None or notified_problem is not None and notified_problem['notified'] is not True:
			if logger is not None:
				logger.info('Notifiying problem')
			people_to_notify_in_telegram = process['data']['notifications']['telegram']
			for person_to_notify_in_telegram in people_to_notify_in_telegram:
				chat_id = person_to_notify_in_telegram['chat_id']
				person_notified_name = person_to_notify_in_telegram['name']
				logger.info(' -> ' + str(person_notified_name))
				telegram_forest_bot.sendMessage(chat_id=chat_id,text='Me caí')
				telegram_forest_bot.sendMessage(chat_id=chat_id, text=telegram.Emoji.GRINNING_FACE_WITH_SMILING_EYES)
				telegram_forest_bot.sendMessage(chat_id=chat_id,text='No sé que me pasa por que sin querer mando')
				telegram_forest_bot.sendMessage(chat_id=chat_id,text=str(error))
				telegram_forest_bot.sendMessage(chat_id=chat_id,text='Me puedes dar una checada?')
			process['data']['notifications']['notified_problem'] = {
				'message' : str(error),
				'notified' : True,
				'fixed' : False,
				'date' : Datetime.now()
			}# End of notified problem
			db_Process.save(process)
		else:
			if logger is not None:
				logger.info('Notification already sent')
	except Exception as e:
		if logger is not None:
			logger.info(e)

def handle_forest_cron_success(success,logger=None):
	try:
		forest_db = set_connection_to_forest_db()
		db_Process = forest_db['Process']
		process = get_db_process('cron',logger=logger)
		notified_problem = process['data']['notifications']['notified_problem'] if 'notified_problem' in process['data']['notifications'] else None
		if notified_problem is True:
			if logger is not None:
				logger.info('Notifiying success')
			people_to_notify_in_telegram = process['data']['notifications']['telegram']
			for person_to_notify_in_telegram in people_to_notify_in_telegram:
				chat_id = person_to_notify_in_telegram['chat_id']
				person_notified_name = person_to_notify_in_telegram['name']
				logger.info(' -> ' + str(person_notified_name))
				telegram_forest_bot.sendMessage(chat_id=chat_id,text='Ya está todo en orden')
				telegram_forest_bot.sendMessage(chat_id=chat_id,text='Gracias carnal! :)')
			del process['data']['notifications']['notified_problem']
			db_Process.save(process)
	except Exception as e:
		if logger is not None:
			logger.info(e)

def get_chat_ids(logger=None):
	try:
		chat_ids = {}
		updates = telegram_forest_bot.getUpdates()
		for item in updates:
			if item['message'] and item['message']['chat'] and item['message']['chat']['id']:
				chat_id = str(item['message']['chat']['id'])
				if not chat_id in chat_ids:
					chat_ids[chat_id] = True
		process = get_db_process('supervisor',logger=logger)
		db_chat_ids = process['chat_ids']
		for chat_id in db_chat_ids:
			chat_id = str(chat_id)
			if not chat_id in chat_ids:
				chat_ids[chat_id] = True
		chats = []
		for chat_id in chat_ids:
			chat = int(chat_id)
			chats.append(chat)
		forest_db = set_connection_to_forest_db()
		db_Process = forest_db['Process']
		process['chat_ids'] = chats
		db_Process.save(process)
		return chats
	except Exception as e:
		print e

def hey(logger=None,server_index=None):
	process = get_db_process('supervisor',logger=logger)
	forest_db = set_connection_to_forest_db()
	db_Process = forest_db['Process']
	if not 'messages' in process:
		process['messages'] = {}
	messages_length = len(process['messages'])
	if messages_length > 100:
		process['messages'] = {}
	db_Process.save(process)
	hey = False
	updates = telegram_forest_bot.getUpdates()
	for item in updates:
		if item['message'] and item['message']['text']:
			text = item['message']['text']
			text = text.lower()
			if 'hey' in text:
				message_id = item['message']['message_id']
				chat_id = item['message']['chat']['id']
				key = text + ' ' + str(message_id) + ' ' + str(chat_id)
				if server_index is not None:
					key = key + ' ' + str(server_index)	
				if not key in process['messages']:
					process['messages'][key] = True
					db_Process.save(process)
					return chat_id
	return False

def send_message_to_forest_telegram_contacts(message,chat_ids=None,logger=None):
	if chat_ids is None:
		chat_ids = get_chat_ids(logger=logger)
	for chat_id in chat_ids:
		if logger is not None:
			logger.info(3*LOG_INDENT + 'Chat id -> ' + str(chat_id))
			# print chat_id
		telegram_forest_bot.sendMessage(chat_id=chat_id,text=message)




	




