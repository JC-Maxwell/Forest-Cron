# -*- coding: utf-8 -*-

# ███████╗██╗     ██╗    ██╗      ██████╗  ██████╗ █████╗ ██╗     ███████╗
# ██╔════╝██║    ███║    ██║     ██╔═══██╗██╔════╝██╔══██╗██║     ██╔════╝
# ███████╗██║    ╚██║    ██║     ██║   ██║██║     ███████║██║     ███████╗
# ╚════██║██║     ██║    ██║     ██║   ██║██║     ██╔══██║██║     ╚════██║
# ███████║███████╗██║    ███████╗╚██████╔╝╚██████╗██║  ██║███████╗███████║
# ╚══════╝╚══════╝╚═╝    ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝

# Description: contains syncrhonization layer 1 local functions (functions that are used in SL1's logics)

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

# Development:
from General import constants as _Constants
from General import utilities as _Utilities
from Processes.Synchronization_layer_1 import config as _SL1_config

# ======================================================== CODE                                                                                                                                                                          

LOG_INDENT = _Constants.LOG_INDENT
SL1_CONFIG = _SL1_config.synchronization_layer_1
SL1_LOGGING_CONFIG = SL1_CONFIG['logging']


# Cron logger (Main):
cron_logger = _Utilities.get_logger('cron')
sl1_logger = _Utilities.get_logger(SL1_LOGGING_CONFIG['process_file_name'])

#  _                       _               
# | |                     (_)            _ 
# | |     ___   __ _  __ _ _ _ __   __ _(_)
# | |    / _ \ / _` |/ _` | | '_ \ / _` |  
# | |___| (_) | (_| | (_| | | | | | (_| |_ 
# \_____/\___/ \__, |\__, |_|_| |_|\__, (_)
#               __/ | __/ |         __/ |  
#              |___/ |___/         |___/   

# Dictionary to log synchronization layer 1 data:
def new_synchronization_layer_1_log(logger=None):
	try:
		synchronization_layer_1_log = {
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
		}# End of synchronization_layer_1_log
		return synchronization_layer_1_log
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

SL1_TABLE_TITLES = SL1_LOGGING_CONFIG['table_titles']
SL1_TABLE_FIELD_LENGTHS = SL1_LOGGING_CONFIG['table_lengths']
DEFAULT_LOG = {}
for key in SL1_TABLE_TITLES:
	DEFAULT_LOG[key] = ''

# Log at sl1 main logs:
def log_sl1_thread_logs_at_sl1_main_logs(sl1_execution_log=None,sl1_logger=sl1_logger,cron_logger=cron_logger):
	try:
		current_taxpayer_index = sl1_execution_log['current_taxpayer_index']
		total_taxpayers = sl1_execution_log['total_taxpayers']
		end = sl1_execution_log['end']
		current_table_row = sl1_execution_log['current_table_row']
		lock = sl1_execution_log['lock']
		total_percentage_done = _Utilities.get_process_percentage_done(current_taxpayer_index,total_taxpayers)
		sl1_execution_log['percentage_done'] = total_percentage_done				
		with lock:
			current_table_row.value = current_table_row.value + 1
		if current_table_row.value >= SL1_LOGGING_CONFIG['table_row_limit']:
			with lock: 
				current_table_row.value = 0
			begin_table_row = _Utilities.format_log(SL1_TABLE_TITLES,SL1_TABLE_FIELD_LENGTHS,begin=True)	
			sl1_logger.info('',extra=begin_table_row)
		sl1_execution_log = _Utilities.format_log(sl1_execution_log,SL1_TABLE_FIELD_LENGTHS)
		sl1_logger.info('',extra=sl1_execution_log)
		if end is True:
			end_table_row = _Utilities.format_log(DEFAULT_LOG,SL1_TABLE_FIELD_LENGTHS,end=True)
			sl1_logger.info('',extra=end_table_row)
			end_message = sl1_execution_log['end_message']
			sl1_logger.info(end_message,extra=DEFAULT_LOG)
	except Exception as e:
		sl1_logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception	

#  _   _                 _ _          _______                         _       _        
# | | | |               | | |        / / ___ \                       | |     | |       
# | |_| | __ _ _ __   __| | | ___   / /| |_/ /_ _ _ __ ___  ___    __| | __ _| |_ __ _ 
# |  _  |/ _` | '_ \ / _` | |/ _ \ / / |  __/ _` | '__/ __|/ _ \  / _` |/ _` | __/ _` |
# | | | | (_| | | | | (_| | |  __// /  | | | (_| | |  \__ \  __/ | (_| | (_| | || (_| |
# \_| |_/\__,_|_| |_|\__,_|_|\___/_/   \_|  \__,_|_|  |___/\___|  \__,_|\__,_|\__\__,_|
                                                                                                                                                                      
# Get synchronization layer 1 data:
def get_synchronization_layer_1_data(logger=None):
	try:
		year =  str(Datetime.now().year)
		months = _Utilities.get_current_fiscal_declaration_period(_Constants.TWO_MONTHS_PERIOD)
		begin_date = Datetime(int(year),int(months[0]),1)
		end_date = Datetime(int(year),int(months[len(months)-1]),_Utilities.get_month_days(months[len(months)-1]))
		end_date = end_date.replace(hour=23, minute=59,second=59)
		sl1_data = {
			'year' : year,
			'months' : months,
			'begin_date' : begin_date,
			'end_date' : end_date
		}#End of sl1_data
		logger.info(LOG_INDENT + 'Year:      ' + str(sl1_data['year']))
		logger.info(LOG_INDENT + 'Months:    ' + str(sl1_data['months']))
		logger.info(LOG_INDENT + 'From ' + str(sl1_data['begin_date']) + ' to ' + str(sl1_data['end_date']))
		return sl1_data
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Get the existing uuids (already exists in Forest DB and they have xml):
def get_existing_uuids_in_forest_db(cfdis_in_db=None,logger=None,sl1_execution_log=None):
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
		sl1_execution_log['forest_db']['before']['good'] = number_of_existing_cfdi_uuids
		return existing_cfdi_uuids
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Get the pending uuids (already exists in Forest DB but they do not have xml):
def get_pending_uuids_in_forest_db(pending_cfdis_in_db=None,logger=None,sl1_execution_log=None):
	try:
		pending_cfdi_uuids = {}
		for pending_cfdi_in_db in pending_cfdis_in_db:
			uuid = pending_cfdi_in_db['uuid']
			pending_cfdi_uuids[uuid] = True
		number_of_pending_cfdi_uuids = len(pending_cfdi_uuids)
		sl1_execution_log['forest_db']['before']['pending'] = number_of_pending_cfdi_uuids
		return pending_cfdi_uuids
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Set an xml and its validations to a db CFDI which is missing its xml:
def set_xml_to_pending_cfdi(cfdi,logger=None,sl1_execution_log=None):
	try:
		forest_db = _Utilities.set_connection_to_forest_db()
		db_CFDI = forest_db['CFDI']
		uuid = cfdi['uuid']
		# Get xml data:
		xml = cfdi['xml']
		validation = _Pauli_Helper.validate_xml(xml)
		xml_warnings = validation['warnings']
		xml_invalidations = validation['invalidations']
		# Updating data:
		updating_cfdi_data = {
			'xml' : xml,
			'validated' : True  if validation['validated'] else False,
			'details' : {
			    'invalidations' : xml_invalidations,
			    'warnings' : xml_warnings
			}# End of details
		}#End of updating_cfdi_data
		db_CFDI.update({'uuid':uuid},{'$set':updating_cfdi_data})
		sl1_execution_log['forest_db']['after']['pending_completed'] = sl1_execution_log['forest_db']['after']['pending_completed'] + 1
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

#  _   _           _       _   _               _____ ____________ _     
# | | | |         | |     | | (_)             /  __ \|  ___|  _  (_)    
# | | | |_ __   __| | __ _| |_ _ _ __   __ _  | /  \/| |_  | | | |_ ___ 
# | | | | '_ \ / _` |/ _` | __| | '_ \ / _` | | |    |  _| | | | | / __|
# | |_| | |_) | (_| | (_| | |_| | | | | (_| | | \__/\| |   | |/ /| \__ \
#  \___/| .__/ \__,_|\__,_|\__|_|_| |_|\__, |  \____/\_|   |___/ |_|___/
#       | |                             __/ |                           
#       |_|                            |___/                            

# Create a new CFDI in Forest DB:
def create_cfdi(new_cfdi,logger=None,sl1_execution_log=None):
	try:
		forest_db = _Utilities.set_connection_to_forest_db()
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
			db_new_cfdi['certification_date'] = _Utilities.sat_date_to_ISODate(new_cfdi['certification_date'])
			db_new_cfdi['issued_date'] = _Utilities.sat_date_to_ISODate(new_cfdi['issued_date'])
		# Get xml data:
		xml = new_cfdi['xml']
		if xml is not None:
			cfdi_type = _Utilities.get_cfdi_type(xml,logger=logger)
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
			sl1_execution_log['forest_db']['after']['new'] = sl1_execution_log['forest_db']['after']['new'] + 1
		elif new_cfdi['status'] == _Constants.CANCELED_STATUS:
			db_new_cfdi['xml'] = _Helper.build_default_xml(db_new_cfdi['seller'],db_new_cfdi['buyer'],db_new_cfdi['certification_date'],db_new_cfdi['issued_date'],db_new_cfdi['voucher_effect'],db_new_cfdi['uuid'])
			sl1_execution_log['forest_db']['after']['new'] = sl1_execution_log['forest_db']['after']['new'] + 1
		else:
			sl1_execution_log['forest_db']['after']['pending'] = sl1_execution_log['forest_db']['after']['pending'] + 1
		db_CFDI.insert(db_new_cfdi)
	except Exception as e:
		logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception

# Update an existing CFDI in Forest DB to cancelled status:
def set_cancelled_status_to_cfdi(cfdi,updated_cfdi,logger=None,sl1_execution_log=None):
	try:
		forest_db = _Utilities.set_connection_to_forest_db()
		db_CFDI = forest_db['CFDI']
		cfdi['status'] = updated_cfdi['status'] # Equalize status
		if 'cancelation_date' in updated_cfdi:
			cfdi['cancelation_date'] = _Helper.sat_date_to_ISODate(updated_cfdi['cancelation_date'])
		xml_exists = 'xml' in cfdi and cfdi['xml'] != ''
		if not xml_exists:
			cfdi['xml'] = _Helper.build_default_xml(cfdi['seller'],cfdi['buyer'],cfdi['certification_date'],cfdi['issued_date'],cfdi['voucher_effect'],cfdi['uuid'])
		sl1_execution_log['forest_db']['after']['updated'] = sl1_execution_log['forest_db']['after']['updated'] + 1
		db_CFDI.save(cfdi)
	except Exception as e:
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

STATUS_DATES = _Constants.STATUS_DATES

def update_synchronization_data_for_taxpayer(taxpayer,sl1_execution_log,logger=None):
	try:
		forest_db = _Utilities.set_connection_to_forest_db()
		db_Taxpayer = forest_db['Taxpayer']
		# Update sl1 success execution date:
		sl1_date = STATUS_DATES['synchronization_layer_1']
		synchronization_date = Datetime.now()
		taxpayer[sl1_date] = synchronization_date
		# Update synchronization logs:
		identifier = taxpayer['identifier']
		begin_date = taxpayer['start_date']#Since taxpayer claim to be synchronized
		begin_date = begin_date.replace(hour=0, minute=0)
		end_date = synchronization_date# Until now
		cfdis_in_forest_db_count = _Utilities.get_cfdis_count_in_forest_for_this_taxpayer_at_period(taxpayer,begin_date,end_date)
		synchronization_log = {
			'status' : 200,
			'temporal_data' : {
				'completed_date' : synchronization_date,
				'period' : {
					'year' : synchronization_date.year,
					'month' : synchronization_date.month
				},
			},
			'cfdis' : {
				'new' : sl1_execution_log['stored'],
				'updated' : sl1_execution_log['updated'],
				'total' : cfdis_in_forest_db_count
			}# End of synchronization_log
		}# End of synchronization_log
		taxpayer_logs = taxpayer['logs'] if 'logs' in taxpayer else {}
		taxpayer_synchronization_logs = taxpayer_logs[_Constants.SYNCHRONIZATION] if _Constants.SYNCHRONIZATION in taxpayer_logs else []
		taxpayer_synchronization_logs.append(synchronization_log)
		if len(taxpayer_synchronization_logs) > _Constants.LIMIT_LOGS_PER_TAXPAYER: 
			taxpayer_synchronization_logs[:1] = []
		taxpayer_logs[_Constants.SYNCHRONIZATION] = taxpayer_synchronization_logs
		taxpayer['logs'] = taxpayer_logs
		db_Taxpayer.save(taxpayer)		
	except Exception as e:
		if logger is not None:
			logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception











