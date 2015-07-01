# -*- coding: utf-8 -*-

#  ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗ 
# ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝ 
# ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
# ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
# ╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
#  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 

# Description: contains Forest CRON processes configuration

# ======================================================== DEPENDENCIES

# Development:
from Processes.Synchronization_layer_1 import synchronization_layer_1 as _Synchronization_Layer_1
from Processes.Equalization import equalization as _Equalization
from Processes.Synchronization_layer_1 import config as _SL1_Config
from Processes.Equalization import config as _Equalization_Config
from General import utilities as _Utilities

import multiprocessing
from multiprocessing import Value

SL1_LOGGING_CONFIG = _SL1_Config.synchronization_layer_1['logging']
EQUALIZATION_LOGGING_CONFIG = _Equalization_Config.equalization['logging']

SL1_TABLE_TITLES = SL1_LOGGING_CONFIG['table_titles']
SL1_DEFAULT_LOG = {}
for key in SL1_TABLE_TITLES:
	SL1_DEFAULT_LOG[key] = ''

EQUALIZATION_TABLE_TITLES = EQUALIZATION_LOGGING_CONFIG['table_titles']
EQUALIZATION_DEFAULT_LOG = {}
for key in EQUALIZATION_TABLE_TITLES:
	EQUALIZATION_DEFAULT_LOG[key] = ''

# ======================================================== CODE

process_handler = {
	'synchronization_layer_1' : {
		'process_instance' : _Synchronization_Layer_1.excute_synchronization_layer_1,# Process instance that will be executed for each subprocess (thread) of this process
		'process_name' : 'synchronization_layer_1',
		'process_file_name' : SL1_LOGGING_CONFIG['process_file_name'],
		'specific_process_logger' : _Utilities.get_logger(SL1_LOGGING_CONFIG['process_file_name']),# Logger for this process (Note: each subprocess of this process will have its own logs but this is the main logger of this process)
		'cron_logger_starting_message' : 'SL1 start',# Message to confirm the main logger (cron-logger) that process has started
		'threads' : 1,
		'specific_shared_variables' : {
			'current_table_row' : Value('i',SL1_LOGGING_CONFIG['table_row_limit'])
		},
		'default_log' : SL1_DEFAULT_LOG
	},
	'equalization' : {
		'process_instance' : _Equalization.equalize_dbs,
		'process_name' : 'equalization',
		'process_file_name' : EQUALIZATION_LOGGING_CONFIG['process_file_name'],
		'specific_process_logger' : _Utilities.get_logger(EQUALIZATION_LOGGING_CONFIG['process_file_name']),
		'cron_logger_starting_message' : 'EQUALIZATION start',
		'threads' : 1,
		'specific_shared_variables' : {
			'current_table_row' : Value('i',EQUALIZATION_LOGGING_CONFIG['table_row_limit'])
		},
		'default_log' : EQUALIZATION_DEFAULT_LOG
	},
	'synchronization_layer_2' : None,
	'initialization' : None,
	'updating' : None,
	'inicident_handler' : None
}# End of process_handler