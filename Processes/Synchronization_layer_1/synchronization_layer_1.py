# -*- coding: utf-8 -*-

# ███████╗██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗    ██╗      █████╗ ██╗   ██╗███████╗██████╗      ██╗
# ██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║    ██║     ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗    ███║
# ███████╗ ╚████╔╝ ██╔██╗ ██║██║     ███████║██████╔╝██║   ██║██╔██╗ ██║██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║    ██║     ███████║ ╚████╔╝ █████╗  ██████╔╝    ╚██║
# ╚════██║  ╚██╔╝  ██║╚██╗██║██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║    ██║     ██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██╗     ██║
# ███████║   ██║   ██║ ╚████║╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║    ███████╗██║  ██║   ██║   ███████╗██║  ██║     ██║
# ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝     ╚═╝

# Description: contains syncrhonization layer 1 process. Synchronization layer 1 means the first layer of synchronization i.e. first iteration 

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
from Processes.Synchronization_layer_1 import config as _SL1_config
from Processes.Synchronization_layer_1 import locals as _Locals

# ======================================================== CODE                                                                                                                                                                          

SL1_CONFIG = _SL1_config.synchronization_layer_1
SL1_LOGGING_CONFIG = SL1_CONFIG['logging']
LOG_INDENT = _Constants.LOG_INDENT
SYNCHRONIZATION_LAYER_1_PROCESS_NAME = 'SYNCHRONIZATION LAYER 1'

# Cron logger (Main):
cron_logger = _Utilities.get_logger('cron')
sl1_logger = _Utilities.get_logger(SL1_LOGGING_CONFIG['process_file_name'])

# Notes:
# cron_logger    -> log at cron main level execution
# sl1_logger     -> log at cron-sl1 process level execution
# process_logger -> log at cron-sl1-n subprocess level execution (n subprocesses every one has its log file)

# Each synchronization layer 1 thread (i.e. subprocess) executes this function. Contains synchronization_layer_1 process for a set of taxpayers
def excute_synchronization_layer_1(taxpayers,shared_variables):# Taxpayers are the ones splitted for this specific subprocess
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
		process_logger = _Utilities.get_subprocess_logger(process_name,SL1_LOGGING_CONFIG,logger=sl1_logger)
		# process_logger.info
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(' ')
		process_logger.info(_Constants.LOG_SEPARATOR)
		process_logger.info(SYNCHRONIZATION_LAYER_1_PROCESS_NAME + ' - ' + process_name.upper())
		# Synchronization layer 1 data:
		sl1_data = _Locals.get_synchronization_layer_1_data(logger=process_logger)
		taxpayers_synchronized_counter = 0
		process_logger.info(LOG_INDENT + 'Taxpayers: ' + str(total_taxpayers_for_this_subprocess))
		for taxpayer in taxpayers:
			_Utilities.update_current_taxpayer(_Constants.SL1,taxpayer['identifier'],current_taxpayer.value+1,logger=process_logger)
			percentage_of_synchronization_done = _Utilities.get_process_percentage_done(taxpayers_synchronized_counter,total_taxpayers_for_this_subprocess)
			taxpayers_synchronized_counter = taxpayers_synchronized_counter + 1# Specific taxpayers (this thread's counter)
			process_logger.info(LOG_INDENT + '-> (' + str(taxpayers_synchronized_counter) + '/' + str(total_taxpayers_for_this_subprocess)  + ') ' + taxpayer['identifier'] + ' --- ' + percentage_of_synchronization_done)
			sl1_execution_data = excute_synchronization_layer_1_for_taxpayer(taxpayer=taxpayer,sl1_data=sl1_data,process_logger=process_logger)
			with lock:
				current_taxpayer.value = current_taxpayer.value + 1
			current_date = Datetime.now()
			sl1_execution_log = {
				'date' : str(current_date)[:10],
				'hour' : str(current_date)[10:-7],
				'process_name' : process_name,
				'current_taxpayer_index' : current_taxpayer.value,
				'total_taxpayers' : total_taxpayers.value,
				'identifier' : taxpayer['identifier'],
				'new' : sl1_execution_data['firmware']['new'],
				'to_update' : sl1_execution_data['forest_db']['before']['pending'],
				'stored' : sl1_execution_data['forest_db']['after']['new'],
				'updated' : sl1_execution_data['forest_db']['after']['updated'],
				'completed' : sl1_execution_data['forest_db']['after']['pending_completed'],
				'pending' : sl1_execution_data['forest_db']['after']['pending'],
				# 'new' : 0,
				# 'to_update' : 0,
				# 'stored' : 0,
				# 'updated' : 0,
				# 'completed' : 0,
				# 'pending' : 0,
				'lock' : lock,
				'current_table_row' : current_table_row
			}# End of sl1_execution_log
			if sl1_execution_log['current_taxpayer_index'] == sl1_execution_log['total_taxpayers']:
				sl1_execution_log['end'] = True
				sl1_execution_log['end_message'] = SYNCHRONIZATION_LAYER_1_PROCESS_NAME + ' DONE SUCCESSFULLY \\0/'
			else:
				sl1_execution_log['end'] = False
			_Locals.log_sl1_thread_logs_at_sl1_main_logs(sl1_execution_log=sl1_execution_log,sl1_logger=sl1_logger,cron_logger=cron_logger)
			if 'avoid_iteration' in sl1_execution_data and sl1_execution_data['avoid_iteration'] == True:
				process_logger.info(2*LOG_INDENT + 'NOT Updating synchronization data for taxpayer ... ')
			else:
				process_logger.info(2*LOG_INDENT + 'Updating synchronization data for taxpayer ... ')
				_Locals.update_synchronization_data_for_taxpayer(taxpayer,sl1_execution_log,logger=process_logger)
			process_logger.info(2*LOG_INDENT + 'Synchronized successfully. Logged at SL1 main logs')
		process_logger.info(SYNCHRONIZATION_LAYER_1_PROCESS_NAME + ' - ' + process_name.upper() + ' DONE SUCCESSFULLY \0/')
		process_logger.info(_Constants.LOG_SEPARATOR)
		return 'OK'
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Contains synchronization_layer_1 process for a single taxpayer:
def excute_synchronization_layer_1_for_taxpayer(taxpayer=None,sl1_data=None,process_logger=None):
	try:
		sl1_execution_log = _Locals.new_synchronization_layer_1_log()
		# Get CFDIs from DB:
		process_logger.info(2*LOG_INDENT + 'RETRIEVING DATA FROM FOREST DB ... ')
		cfdis_in_db = _Utilities.get_cfdis_in_forest_for_this_taxpayer_at_period(taxpayer,sl1_data['begin_date'],sl1_data['end_date'])
		pending_cfdis_in_db = _Utilities.get_pending_cfdis_in_forest_for_this_taxpayer_at_period(taxpayer,sl1_data['begin_date'],sl1_data['end_date'])
		# Manage or format CFDis data:
		existing_cfdi_uuids = _Locals.get_existing_uuids_in_forest_db(cfdis_in_db=cfdis_in_db,logger=process_logger,sl1_execution_log=sl1_execution_log)
		pending_cfdi_uuids = _Locals.get_pending_uuids_in_forest_db(pending_cfdis_in_db=pending_cfdis_in_db,logger=process_logger,sl1_execution_log=sl1_execution_log)
		# Log Forest data:
		process_logger.info(3*LOG_INDENT + 'Existing:           ' + str(sl1_execution_log['forest_db']['before']['good']))
		process_logger.info(3*LOG_INDENT + 'Pending:            ' + str(sl1_execution_log['forest_db']['before']['pending']))
		# Get CFDIs from firmware:
		get_sat_updates_params = {
			'identifier' : taxpayer['identifier'],
			'password' : taxpayer['password'],
			'year' : sl1_data['year'],
			'months' : sl1_data['months'],
			'uuids' : existing_cfdi_uuids
		}# End of get_sat_update_params
		# -------------------------------------------------------------------
		# bugSolved 12/Ago/15 
		# Event: timeout value was becoming longer and longer because of connection problems (firmware servers could not be reached due to connection problems instead of logic problems)
		# firmware_timeout = taxpayer['firmware_timeout'] if 'firmware_timeout' in taxpayer and taxpayer['firmware_timeout'] is not None else _Constants.DEFAULT_FIRMWARE_TIMEOUT
		firmware_timeout = _Constants.DEFAULT_FIRMWARE_TIMEOUT
		# -------------------------------------------------------------------
		# process_logger.info(2*LOG_INDENT + 'RETRIEVING DATA FROM FIRMWARE (SAT) constant timeout = ' + str(firmware_timeout) + ' secs')
		process_logger.info(2*LOG_INDENT + 'RETRIEVING DATA FROM FIRMWARE (SAT)')
		sat_updates = _Firmware.isa(instruction='get_sat_updates',params=get_sat_updates_params,log=sl1_execution_log,logger=process_logger,timeout=firmware_timeout,taxpayer=taxpayer)
		new_cfdis = sat_updates['new']
		updated_cfdis = sat_updates['updated']
		process_logger.info(3*LOG_INDENT + 'CFDI new:           ' + str(sl1_execution_log['firmware']['new']))
		process_logger.info(3*LOG_INDENT + 'CFDI to-update:     ' + str(sl1_execution_log['firmware']['update']))
		# Update Forest DB -> NEW OR COMPLETED:
		process_logger.info(2*LOG_INDENT + 'UPDATING FOREST DB (creting new CFDIs) ... ')
		n = 0
		for new_cfdi in new_cfdis:
			n = n + 1
			uuid = new_cfdi['uuid']
			if uuid in pending_cfdi_uuids:# Complete pending cfdis:
				if 'xml' in new_cfdi and new_cfdi['xml'] != '':
					cfdi_with_missing_xml = new_cfdi
					_Locals.set_xml_to_pending_cfdi(cfdi_with_missing_xml,logger=process_logger,sl1_execution_log=sl1_execution_log)
					process_logger.info(3*LOG_INDENT + str(n) + '. ' + uuid + ' completed in Forest DB')
			else:# Completely new ones:
				_Locals.create_cfdi(new_cfdi,logger=process_logger,sl1_execution_log=sl1_execution_log)
				process_logger.info(3*LOG_INDENT + str(n) + '. ' + uuid + ' stored in Forest DB')
		# Update Forest DB -> JUST UPDATING:
		process_logger.info(2*LOG_INDENT + 'UPDATING FOREST DB (updating existing CFDIs) ... ')
		cfdis_in_db = _Utilities.get_cfdis_in_forest_for_this_taxpayer_at_period(taxpayer,sl1_data['begin_date'],sl1_data['end_date'])# Get cfdis for updating data (They must be retrieved again due to cursor invalidation problems):
		updated_cfdi_uuids = []
		updated_cfdis_status_by_uuid = {}
		cfdis_with_status_updated = 0;
		default_canceled_xml_inserted_in_updating = 0;
		n = 0
		for updated_cfdi in updated_cfdis:
			for cfdi_in_db in cfdis_in_db:
				cfdi_in_db_uuid = cfdi_in_db['uuid']
				updating_cfdi_uuid = updated_cfdi['uuid']
				if cfdi_in_db_uuid == updating_cfdi_uuid:
					updated_cfdi_status = updated_cfdi['status']
					# Compare the one in forest db and the one in SAT to equalize CFDI state:
					if updated_cfdi_status == _Constants.CANCELED_STATUS:
						_Locals.set_cancelled_status_to_cfdi(cfdi_in_db,updated_cfdi,logger=process_logger,sl1_execution_log=sl1_execution_log)
						n = n + 1
						process_logger.info(3*LOG_INDENT + str(n) + '. ' + cfdi_in_db_uuid + ' updated in Forest DB')
		process_logger.info(2*LOG_INDENT + 'SUMMARY ... ')
		process_logger.info(3*LOG_INDENT + 'New stored:         ' + str(sl1_execution_log['forest_db']['after']['new']))
		process_logger.info(3*LOG_INDENT + 'Pending completed:  ' + str(sl1_execution_log['forest_db']['after']['pending_completed']))
		process_logger.info(3*LOG_INDENT + 'Pending:            ' + str(sl1_execution_log['forest_db']['after']['pending']))
		process_logger.info(3*LOG_INDENT + 'Updated:            ' + str(sl1_execution_log['forest_db']['after']['updated']))
		return sl1_execution_log
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		process_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception
