# -*- coding: utf-8 -*-

# ███████╗ ██████╗ ██╗   ██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝██╔═══██╗██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# █████╗  ██║   ██║██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔══╝  ██║▄▄ ██║██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ███████╗╚██████╔╝╚██████╔╝██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                                                                                            

# Description: contains equalization process i.e. logics for equalizing Corebook DB and Forest DB

# ======================================================== DEPENDENCIES

# Native:
import sys
from datetime import datetime as Datetime
from datetime import date as Date
from dateutil.relativedelta import *
import multiprocessing

# Pauli SDK dependency:
from pauli_sdk.Modules import constants as _Pauli_Constants
from pauli_sdk.Modules import helper as _Pauli_Helper
from pauli_sdk.Classes.response import Error
from pauli_sdk.Classes.response import Already_Handled_Exception

# Development:
from General import constants as _Constants
from General import utilities as _Utilities
from Processes.Equalization import config as _Equalization_config
from Processes.Equalization import locals as _Locals

# ======================================================== CODE                                                                                                                                                                          

EQUALIZATION_CONFIG = _Equalization_config.equalization
EQUALIZATION_LOGGING_CONFIG = EQUALIZATION_CONFIG['logging']
LOG_INDENT = _Constants.LOG_INDENT
EQUALIZATION_PROCESS_NAME = 'DBS EQUALIZATION'

# Cron logger (Main):
cron_logger = _Utilities.get_logger('cron')
equalization_logger = _Utilities.get_logger(EQUALIZATION_LOGGING_CONFIG['process_file_name'])

# Notes:
# cron_logger    -> log at cron main level execution
# equalization_logger -> log at cron-sl1 process level execution
# process_logger -> log at cron-equalization-n subprocess level execution (n subprocesses every one has its log file)

# Each equalization dbs thread (i.e. subprocess) executes this function. Contains equalize_dbs process for a set of taxpayers
def equalize_dbs(taxpayers,shared_variables):# Taxpayers are the ones splitted for this specific subprocess
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
		process_logger = _Utilities.get_subprocess_logger(process_name,EQUALIZATION_LOGGING_CONFIG,logger=equalization_logger)
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(_Constants.LOG_SEPARATOR)
		process_logger.info(EQUALIZATION_PROCESS_NAME + ' - ' + process_name.upper())
		taxpayers_equalized_counter = 0
		process_logger.info(LOG_INDENT + 'Taxpayers: ' + str(total_taxpayers_for_this_subprocess))
		for taxpayer in taxpayers:
			_Utilities.update_current_taxpayer(_Constants.EQUALIZATION,taxpayer['identifier'],current_taxpayer.value+1,logger=process_logger)
			percentage_of_equalization_done = _Utilities.get_process_percentage_done(taxpayers_equalized_counter,total_taxpayers_for_this_subprocess)
			taxpayers_equalized_counter = taxpayers_equalized_counter + 1# Specific taxpayers (this thread's counter)
			process_logger.info(LOG_INDENT + '-> (' + str(taxpayers_equalized_counter) + '/' + str(total_taxpayers_for_this_subprocess)  + ') ' + taxpayer['identifier'] + ' --- ' + percentage_of_equalization_done)
			equalization_data = equalize_dbs_for_a_taxpayer(taxpayer=taxpayer,process_logger=process_logger)
			with lock:
				current_taxpayer.value = current_taxpayer.value + 1
			current_date = Datetime.now()
			equalization_log = {
				'date' : str(current_date)[:10],
				'hour' : str(current_date)[10:-7],
				'process_name' : process_name,
				'current_taxpayer_index' : current_taxpayer.value,
				'total_taxpayers' : total_taxpayers.value,
				'identifier' : taxpayer['identifier'],
				'forest_db' : equalization_data['before']['forest_db'],
				'corebook_db' : equalization_data['before']['corebook_db'],
				'missing_in_forest_db' : equalization_data['before']['cb_but_not_in_f'],
				'missing_in_cb_db' : equalization_data['before']['f_but_not_in_cb'],
				'stored' : equalization_data['after']['stored'],
				'errors' : equalization_data['after']['errors'],
				# 'forest_db' : 90,
				# 'corebook_db' : 10,
				# 'missing_in_forest_db' : 10,
				# 'missing_in_cb_db' : 11,
				# 'stored' : 10,
				# 'errors' : 1,
				'current_table_row' : current_table_row,
				'lock' : lock
			}# End of equalization_log
			if equalization_log['current_taxpayer_index'] == equalization_log['total_taxpayers']:
				equalization_log['end'] = True
				equalization_log['end_message'] = EQUALIZATION_PROCESS_NAME + ' DONE SUCCESSFULLY \\0/'
			else:
				equalization_log['end'] = False
			_Locals.log_eq_thread_logs_at_equalization_main_logs(equalization_execution_log=equalization_log,equalization_logger=equalization_logger,cron_logger=cron_logger)
			process_logger.info(2*LOG_INDENT + 'Updating taxpayer ... ')
			_Utilities.update_taxpayer_status(taxpayer,_Constants.EQUALIZATION,logger=process_logger)
			process_logger.info(2*LOG_INDENT + 'Equalized successfully. Logged at Equalization main logs')
		process_logger.info(EQUALIZATION_PROCESS_NAME + ' - ' + process_name.upper() + ' DONE SUCCESSFULLY \0/')
		process_logger.info(_Constants.LOG_SEPARATOR)
		return 'OK'
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		equalization_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Equalize Forest DB an Corebook DB in a given period for a given identifier (i.e. It ensures both data bases contain the same CFDIs)
def equalize_dbs_for_a_taxpayer(taxpayer=None,process_logger=None):
	try:
		indent = '    '
		log = {
			'before' : {},
			'after' : {
				'stored' : 0,
				'errors' : 0
			}
		}# End of log
		# Get params:
		identifier = taxpayer['identifier']
		created_at = taxpayer['created_at']
		created_at_lower_limit = Datetime.now() - relativedelta(months=1)
		force_start_date = True
		# process_logger.info(2*LOG_INDENT + 'FORCING START DATE')
		if created_at > created_at_lower_limit:
			begin_date = taxpayer['start_date']#Since taxpayer claim to be synchronized
			process_logger.info(2*LOG_INDENT + 'Chosing start date as begin date')
		else:
			current_date = Datetime.now()
			current_year = current_date.year
			begin_date = Datetime(current_year,1,1)# Jan 1st of the current year
			process_logger.info(2*LOG_INDENT + 'Chosing ' + str(begin_date) + ' as begin date')
		# year =  str(Datetime.now().year)
		# months = _Utilities.get_current_fiscal_declaration_period(_Constants.TWO_MONTHS_PERIOD)
		# begin_date = Datetime(int(year),int(months[0]),1)# Since previous month (optimization introduced on Sep 8, 2015)
		begin_date = begin_date.replace(hour=0, minute=0)
		end_date = Datetime.now()# Until now
		process_logger.info(2*LOG_INDENT + 'Equalizing dbs from ' + str(begin_date) + ' to ' + str(end_date))
		# Get CFDIs from Forest DB:
		cfdis_in_forest_db_count = _Utilities.get_cfdis_count_in_forest_for_this_taxpayer_at_period(taxpayer,begin_date,end_date)
		process_logger.info(2*LOG_INDENT + 'Retrieving ' + str(cfdis_in_forest_db_count) + ' from Forest DB ... ')
		cfdis_in_forest_db = _Utilities.get_cfdis_in_forest_for_this_taxpayer_at_period(taxpayer,begin_date,end_date,limit=None,logger=process_logger,dict_result=True)	
		# Get CFDIs from Corebook DB:
		try:
			cfdis_in_corebook_db_count = _Locals.get_cfdis_count_in_corebook_for_this_taxpayer_at_period(identifier,begin_date,end_date,logger=process_logger)
			process_logger.info(2*LOG_INDENT + 'Retrieving ' + str(cfdis_in_corebook_db_count) + ' from Corebook DB ... ')
			cfdis_in_corebook_db = _Locals.get_cfdis_in_corebook_for_this_taxpayer_at_period(identifier,begin_date,end_date,limit=None,logger=process_logger)	
		except Already_Handled_Exception as already_handled_exception:
			process_logger.info(2*LOG_INDENT + already_handled_exception.value)
			log['before'] = {
				'forest_db' : 0,
				'corebook_db' : 0,
				'f_but_not_in_cb' : 0,
				'cb_but_not_in_f' : 0
			}# End of log
			log['after']['errors'] = log['after']['errors'] + 1
			return log
		# Log data in db:
		log['before']['forest_db'] = len(cfdis_in_forest_db)
		log['before']['corebook_db'] = len(cfdis_in_corebook_db)
		# Get missing CFDIs in Corebook:
		process_logger.info(2*LOG_INDENT + 'Getting differences in dbs ... ')
		# _Utilities.log_cfdis_uuids(title='Forest CFDIs: ',indent=2*LOG_INDENT,cfdis=cfdis_in_forest_db,logger=process_logger,dict=True)
		# _Utilities.log_cfdis_uuids(title='Corebook CFDIs: ',indent=2*LOG_INDENT,cfdis=cfdis_in_corebook_db,logger=process_logger,dict=True)
		missing_cfdis = _Locals.get_missing_cfdis_in_each_db(cfdis_in_forest_db,cfdis_in_corebook_db,logger=process_logger)
		missing_cfdis_in_corebook_db = missing_cfdis['in_corebook_db']
		missing_cfdis_in_forest_db = missing_cfdis['in_forest_db']
		cfdis_with_different_status = missing_cfdis['cfdis_with_different_status']
		# General status:
		log['before']['f_but_not_in_cb'] = len(missing_cfdis_in_corebook_db)
		log['before']['cb_but_not_in_f'] = len(missing_cfdis_in_forest_db)
		log['before']['cfdis_with_different_status'] = cfdis_with_different_status
		process_logger.info(2*LOG_INDENT + 'DBs Status: ')
		process_logger.info(3*LOG_INDENT + 'Forest DB   -> ' + str(log['before']['forest_db']))
		process_logger.info(3*LOG_INDENT + 'Corebook DB -> ' + str(log['before']['corebook_db']))
		process_logger.info(3*LOG_INDENT + 'F not in CB -> ' + str(log['before']['f_but_not_in_cb'] - log['before']['cfdis_with_different_status']))
		process_logger.info(3*LOG_INDENT + 'CB not in F -> ' + str(log['before']['cb_but_not_in_f']))
		process_logger.info(3*LOG_INDENT + 'Diff Status -> ' + str(log['before']['cfdis_with_different_status']))
		if len(missing_cfdis_in_corebook_db) > 0:
			# _Utilities.log_cfdis_uuids(title='Missing CFDIs: ',indent=2*LOG_INDENT,cfdis=missing_cfdis_in_corebook_db,logger=process_logger)
			# log['after']['stored'] = len(missing_cfdis_in_corebook_db)
			# log['after']['errors'] = 0
			cb_summary = _Locals.store_missing_cfdis_in_corebook(missing_cfdis_in_corebook_db,identifier,logger=process_logger,limit=None)
			log['after']['stored'] = cb_summary['stored']
			log['after']['errors'] = cb_summary['errors']
			process_logger.info(2*LOG_INDENT + 'Equalization Summary: ')
			process_logger.info(3*LOG_INDENT + 'CFDIs stored in CB  -> ' + str(log['after']['stored']))
			process_logger.info(3*LOG_INDENT + 'Errors occurred     -> ' + str(log['after']['errors']))
		return log
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		equalization_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception
