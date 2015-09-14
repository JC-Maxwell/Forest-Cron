# -*- coding: utf-8 -*-

# ███████╗██╗██████╗ ███╗   ███╗██╗    ██╗ █████╗ ██████╗ ███████╗
# ██╔════╝██║██╔══██╗████╗ ████║██║    ██║██╔══██╗██╔══██╗██╔════╝
# █████╗  ██║██████╔╝██╔████╔██║██║ █╗ ██║███████║██████╔╝█████╗  
# ██╔══╝  ██║██╔══██╗██║╚██╔╝██║██║███╗██║██╔══██║██╔══██╗██╔══╝  
# ██║     ██║██║  ██║██║ ╚═╝ ██║╚███╔███╔╝██║  ██║██║  ██║███████╗
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

# Description: contains the set of instructions that are necessary to stablish comunication with Forest's drivers:

# ======================================================== DEPENDENCIES

# NATIVE
import sys
import json

# EXTERNAL
import logging

# SDK:
from pauli_sdk.Modules import constants as _Pauli_Constants
from pauli_sdk.Modules import helper as _Pauli_Helper
from pauli_sdk.Classes.response import Error
from pauli_sdk.Classes.response import Already_Handled_Exception

# Development:
from General import constants as _Constants
from General import utilities as _Utilities

# ======================================================== MODULE CODE

LOG_INDENT = _Constants.LOG_INDENT
AVOID_FIRMWARE = _Constants.AVOID_FIRMWARE
DEFAULT_FIRMWARE_RESULT = _Constants.DEFAULT_FIRMWARE_RESULT
FIRMWARE_STABLISH_CONNECTION_TIME_ON_SECONDS = _Constants.FIRMWARE_STABLISH_CONNECTION_TIME
FIRMWARE_WAITING_TIME_ON_SECONDS = _Constants.FIRMWARE_WAITING_TIME_ON_SECONDS

# Firmware (comment this to simulate firmware):
from forest_firmware.isa import instructions as ISA
# Firmware simulation (uncomment this to simulate firmware
# --------------------- BEGIN OF FIRMWARE SIMULATION ---------------------
# Just a firmware simulation for debugging:
# def get_sat_updates(params,logger=None):
# 	try:
# 		logger.info(3*LOG_INDENT + ' -> Simulating Firmware.ISA ... ')
# 		forest_db = _Utilities.set_connection_to_forest_db()
# 		db_CFDI = forest_db['CFDI']
# 		# This query is to retrieve CFDIs from forest (just specify the query as you wish)
# 		simulated_cfdis = db_CFDI.find({ 
# 			'uuid' : { 
# 				'$in' : [
# 					'83000FEA-35C7-4CCB-9136-45F8FF7D90C6',# credit note
# 					'3A58597F-E0A3-474A-8299-E34E9DBFFE68',# payroll
# 					'E254BDBC-9F6A-4056-85AF-0557FD20391C'# normal
# 				]# End of in 
# 			}# End of uuid
# 		})# End simulated_cfdis
# 		simulated_cfdis_list = []
# 		for simulated_cfdi in simulated_cfdis:
# 			simulated_cfdi['simulated'] = True
# 			simulated_cfdis_list.append(simulated_cfdi)
# 		logger.info(3*LOG_INDENT + ' -> Simulated CFDIs: ' + str(len(simulated_cfdis_list)))
# 		firmware_result_json = {
# 			'new' : simulated_cfdis_list,
# 			'updated' : []
# 		}#End of firmware_result_json
# 		return firmware_result_json
# 	except Exception as e:
# 		logger.info(3*LOG_INDENT + str(e))

# ISA = {
# 	'get_sat_updates' : get_sat_updates,
# 	'simulation' : True
# }# End of ISA simulation
# --------------------- END OF FIRMWARE SIMULATION ---------------------

def isa(**params):
	try:
		logger = None
		if 'logger' in params:
			logger = params['logger']
			del params['logger']
		taxpayer = params['taxpayer']
		del params['taxpayer']
		log = params['log']
		del params['log']
		payload = params
		headers = {'content-type':'application/json'}
		if AVOID_FIRMWARE is not True:
			try:				
				instruction = params['instruction']
				isa_params = params['params']
				logger.info(3*LOG_INDENT + 'Consuming Firmware.ISA ')
				# Verify if it is not a firmware simulation:
				if 'simulation' in ISA and ISA['simulation'] == True:
					firmware_result_json = ISA[instruction](isa_params,logger=logger)
				# Really consumes firmware:
				else:
					firmware_result = ISA[instruction](isa_params)
					firmware_result_json = firmware_result.content
				log['firmware']['new'] = len(firmware_result_json['new'])
				log['firmware']['update'] = len(firmware_result_json['updated'])
				_Utilities.handle_forest_cron_success('ok',logger=logger)
				return firmware_result_json
			except Exception as e:
				logger.info(e)
				logger.info(3*LOG_INDENT + 'Request to firmware was not possible (connection or timeout)')
				logger.info(3*LOG_INDENT + 'Avoiding iteration ... ')
				log['avoid_iteration'] = True# Just a flag to avoid taxpayer logs to be updated with this sync/init iteration (they must not be updated because there was a firmware problem)
				_Utilities.handle_forest_cron_error(e,logger=logger)
				return DEFAULT_FIRMWARE_RESULT
		else:
			_Utilities.handle_forest_cron_success('ok',logger=logger)
			return DEFAULT_FIRMWARE_RESULT
	except Exception as e:
		logger.info(3*LOG_INDENT + str(e))
		# -------------------------------------------------------------------
		# bugSolved 12/Ago/15 
		# Event: timeout value was becoming longer and longer because of connection problems (firmware servers could not be reached due to connection problems instead of logic problems)
		# _Utilities.update_taxpayer_firmware_timeout(taxpayer,logger=logger)# firmware timeout updating was avoided
		# -------------------------------------------------------------------
		raise e


















