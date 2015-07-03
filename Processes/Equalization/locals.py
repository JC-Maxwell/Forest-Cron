# -*- coding: utf-8 -*-

# ███████╗ ██████╗ ██╗   ██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗    ██╗      ██████╗  ██████╗ █████╗ ██╗     ███████╗
# ██╔════╝██╔═══██╗██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║    ██║     ██╔═══██╗██╔════╝██╔══██╗██║     ██╔════╝
# █████╗  ██║   ██║██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║    ██║     ██║   ██║██║     ███████║██║     ███████╗
# ██╔══╝  ██║▄▄ ██║██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║    ██║     ██║   ██║██║     ██╔══██║██║     ╚════██║
# ███████╗╚██████╔╝╚██████╔╝██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║    ███████╗╚██████╔╝╚██████╗██║  ██║███████╗███████║
# ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝
                                                                                                                                                 
# Description: contains equalization local functions (functions that are used in equalization's logics)

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
from Processes.Equalization import config as _Equalization_config
EQUALIZATION_CONFIG = _Equalization_config.equalization
EQUALIZATION_LOGGING_CONFIG = EQUALIZATION_CONFIG['logging']

# ======================================================== CODE                                                                                                                                                                          

LOG_INDENT = _Constants.LOG_INDENT

# Cron logger (Main):
cron_logger = _Utilities.get_logger('cron')
equalization_logger = _Utilities.get_logger(EQUALIZATION_LOGGING_CONFIG['process_file_name'])

#  _____                _                 _     ____________   
# /  __ \              | |               | |    |  _  \ ___ \_ 
# | /  \/ ___  _ __ ___| |__   ___   ___ | | __ | | | | |_/ (_)
# | |    / _ \| '__/ _ \ '_ \ / _ \ / _ \| |/ / | | | | ___ \  
# | \__/\ (_) | | |  __/ |_) | (_) | (_) |   <  | |/ /| |_/ /_ 
#  \____/\___/|_|  \___|_.__/ \___/ \___/|_|\_\ |___/ \____/(_) 

def get_cfdis_count_in_corebook_for_this_taxpayer_at_period(identifier,begin_date,end_date,logger=None):
	try:
		corebook_db = _Utilities.set_connection_to_corebook_db()
		db_Ticket = corebook_db['Ticket']
		db_User = corebook_db['User']
		# Get user:
		user_filter = { 'identifier' : identifier }
		user_exists = db_User.find(user_filter).count()
		if user_exists:
			user = db_User.find(user_filter)[0]
			owner_id = str(user['_id'])
			ticket_filter = { 'ownerId': owner_id, 'expendedAt': {'$gte': begin_date, '$lte': end_date}, 'smartTicketId' : { '$exists' : False } }
			cfdis_in_corebook_db_count = db_Ticket.find(ticket_filter).count()
			return cfdis_in_corebook_db_count
		else:
			error_message = 'User with identifier ' + str(identifier) + ' does not exists in Corebook DB'
			# logger.critical(error_message)
			already_handled_exception = Already_Handled_Exception(error_message)
			raise already_handled_exception
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def get_cfdis_in_corebook_for_this_taxpayer_at_period(identifier,begin_date,end_date,limit=None,logger=None):
	try:
		corebook_db = _Utilities.set_connection_to_corebook_db()
		db_Ticket = corebook_db['Ticket']
		db_User = corebook_db['User']
		# Get user:
		user_filter = { 'identifier' : identifier }
		user_exists = db_User.find(user_filter).count()
		if user_exists:
			user = db_User.find(user_filter)[0]
			owner_id = str(user['_id'])
			ticket_filter = { 'ownerId': owner_id, 'expendedAt':  {'$gte': begin_date, '$lte': end_date}, 'smartTicketId' : { '$exists' : False } }
			if limit is None:
				cfdis_in_corebook_db = db_Ticket.find(ticket_filter)
			else:
				cfdis_in_corebook_db = db_Ticket.find(ticket_filter).limit(limit)
			cfdis_in_corebook_db_dict = {}
			for cfdi_in_corebook_db in cfdis_in_corebook_db:
				if 'uuid' in cfdi_in_corebook_db:
					uuid = cfdi_in_corebook_db['uuid'].upper()
					if not uuid in cfdis_in_corebook_db_dict:
						cfdis_in_corebook_db_dict[uuid] = cfdi_in_corebook_db
			# result = {
			# 	'replicated' : n,
			# 	'without_uuid' : i,
			# 	'ok' : len(cfdis_in_corebook_db_dict),
			# 	'total' : n + i + len(cfdis_in_corebook_db_dict),
			# 	'cfdis' : cfdis_in_corebook_db_dict 
			# }#End of result
			return cfdis_in_corebook_db_dict
		else:
			error_message = 'User with identifier ' + str(identifier) + ' does not exists in Corebook DB'
			# logger.critical(error_message)
			already_handled_exception = Already_Handled_Exception(error_message)
			raise already_handled_exception
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

def get_missing_cfdis_in_each_db(cfdis_in_forest_db,cfdis_in_corebook_db):
	try:
		missing_cfdis_in_corebook_db = []
		for uuid in cfdis_in_forest_db:
			if not uuid in cfdis_in_corebook_db:
				cfdi_in_forest = cfdis_in_forest_db[uuid]
				missing_cfdis_in_corebook_db.append(cfdi_in_forest)
		# Get missing CFDIs in Forest:
		missing_uuids_in_forest_db = []
		for uuid in cfdis_in_corebook_db:
			if not uuid in cfdis_in_forest_db:
				missing_uuids_in_forest_db.append(uuid)
		missing_cfdis = {
			'in_corebook_db' : missing_cfdis_in_corebook_db,
			'in_forest_db' : missing_uuids_in_forest_db
		}#End of missing_cfdis
		return missing_cfdis
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# With this configuration CFDIs are going to be stored in Corebook
STORING_CONFIGURATION = {
	'test' : False,
	'predict' : True,# Each CFDI will be predicted
	'store' : True,# Will be stored
	'replace' : True,# If already exists a ticket with this uuid it will be replaced
	'indent' : 2*LOG_INDENT# Just for logging
}#End of STORING_CONFIGURATION

def store_missing_cfdis_in_corebook(missing_cfdis_in_corebook_db,identifier,logger=None,limit=None):
	try:
		logger.info(2*LOG_INDENT + 'Storing missing CFDIs in Corebook DB ... ')
		n = 0
		s = 0
		log = {
			'stored' : 0,
			'errors' : 0
		}# End of result
		for missing_cfdi_in_corebook_db in missing_cfdis_in_corebook_db:
			n = n + 1
			uuid = missing_cfdi_in_corebook_db['uuid']
			xml = missing_cfdi_in_corebook_db['xml']
			cfdi_status = missing_cfdi_in_corebook_db['status']
			canceled = False
			if cfdi_status == _Constants.CANCELED_STATUS:
				canceled = True
			try:
				logger.info(3*LOG_INDENT + str(n) + '. Storing ' + str(uuid) + ' in Corebook DB')
				cfdi_status = 

				result = _Corebook_SDK.create_ticket_from_xml(xml,identifier,canceled=canceled,config=STORING_CONFIGURATION)
				log['stored'] = log['stored'] + 1
				s = s + 1
			except Corebook_SDK_Error as corebook_SDK_Error:
				logger.info(corebook_SDK_Error)
				log['errors'] = log['errors'] + 1
				pass
			except Already_Handled_Exception as already_handled_exception:
				logger.info(3*LOG_INDENT + str(n) + '. ' + str(uuid) + ' ERROR')
				log['errors'] = log['errors'] + 1
				pass
			if limit is not None:
				if n == limit:
					break
		return log
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

#  _                       _               
# | |                     (_)            _ 
# | |     ___   __ _  __ _ _ _ __   __ _(_)
# | |    / _ \ / _` |/ _` | | '_ \ / _` |  
# | |___| (_) | (_| | (_| | | | | | (_| |_ 
# \_____/\___/ \__, |\__, |_|_| |_|\__, (_)
#               __/ | __/ |         __/ |  
#              |___/ |___/         |___/   

EQUALIZATION_TABLE_TITLES = EQUALIZATION_LOGGING_CONFIG['table_titles']
EQUALIZATION_TABLE_FIELD_LENGTHS = EQUALIZATION_LOGGING_CONFIG['table_lengths']
DEFAULT_LOG = {}
for key in EQUALIZATION_TABLE_TITLES:
	DEFAULT_LOG[key] = ''

# Log at equalization main logs:
def log_eq_thread_logs_at_equalization_main_logs(equalization_execution_log=None,equalization_logger=equalization_logger,cron_logger=cron_logger):
	try:
		taxpayer_identifier = equalization_execution_log['identifier']
		current_taxpayer_index = equalization_execution_log['current_taxpayer_index']
		total_taxpayers = equalization_execution_log['total_taxpayers']
		current_table_row = equalization_execution_log['current_table_row']
		lock = equalization_execution_log['lock']
		end = equalization_execution_log['end']
		total_percentage_done = _Utilities.get_process_percentage_done(current_taxpayer_index,total_taxpayers)
		equalization_execution_log['percentage_done'] = total_percentage_done
		with lock:
			current_table_row.value = current_table_row.value + 1
		if current_table_row.value >= EQUALIZATION_LOGGING_CONFIG['table_row_limit']:
			with lock: 
				current_table_row.value = 0
			begin_table_row = _Utilities.format_log(EQUALIZATION_TABLE_TITLES,EQUALIZATION_TABLE_FIELD_LENGTHS,begin=True)	
			equalization_logger.info('',extra=begin_table_row)
		equalization_execution_log = _Utilities.format_log(equalization_execution_log,EQUALIZATION_TABLE_FIELD_LENGTHS)
		equalization_logger.info('',extra=equalization_execution_log)
		if end is True:
			end_table_row = _Utilities.format_log(DEFAULT_LOG,EQUALIZATION_TABLE_FIELD_LENGTHS,end=True)
			equalization_logger.info('',extra=end_table_row)
			end_message = equalization_execution_log['end_message']
			equalization_logger.info(end_message,extra=DEFAULT_LOG)
	except Exception as e:
		equalization_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	
