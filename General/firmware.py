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
import requests

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

# Firmware url:
FIRMWARE_URL = _Constants.FIRMWARE_URL
AVOID_FIRMWARE = _Constants.AVOID_FIRMWARE
DEFAULT_FIRMWARE_RESULT = _Constants.DEFAULT_FIRMWARE_RESULT
FIRMWARE_STABLISH_CONNECTION_TIME_ON_SECONDS = _Constants.FIRMWARE_STABLISH_CONNECTION_TIME
FIRMWARE_WAITING_TIME_ON_SECONDS = _Constants.FIRMWARE_WAITING_TIME_ON_SECONDS

def isa(**params):
	try:
		logger = None
		if 'logger' in params:
			logger = params['logger']
			del params['logger']
		taxpayer = params['taxpayer']
		del params['taxpayer']
		url = FIRMWARE_URL
		# url = 'http://fakeurl'
		log = params['log']
		del params['log']
		payload = params
		headers = {'content-type':'application/json'}
		# AVOID_FIRMWARE = True
		if AVOID_FIRMWARE is not True:
			try:
				logger.info(3*LOG_INDENT + 'Requesting ' + url + ' ( ' + str(FIRMWARE_WAITING_TIME_ON_SECONDS) + ' secs ) ... ')
				firmware_result = requests.post(url, data=json.dumps(payload), headers=headers,timeout=(FIRMWARE_STABLISH_CONNECTION_TIME_ON_SECONDS,FIRMWARE_WAITING_TIME_ON_SECONDS))# timeout = (connection,read)
			except Exception as e:
				logger.info(e)
				logger.info(3*LOG_INDENT + 'Request to firmware was not possible (connection or timeout)')
				logger.info(3*LOG_INDENT + 'Avoiding iteration ... ')
				log['avoid_iteration'] = True# Just a flag to avoid taxpayer logs to be updated with this sync/init iteration (they must not be updated because there was a firmware problem)
				_Utilities.handle_forest_cron_error(e,logger=logger)
				return DEFAULT_FIRMWARE_RESULT
			if firmware_result.status_code == 200:
				_Utilities.handle_forest_cron_success('ok',logger=logger)
				firmware_result_json = firmware_result.json()# Comment in case of simulation
				log['firmware']['new'] = len(firmware_result_json['new'])
				log['firmware']['update'] = len(firmware_result_json['updated'])
				return firmware_result_json
			else:
				if logger is not None:
					logger.critical('Firmware error')
					logger.critical(firmware_result)
				logger.info(e)
				logger.info(3*LOG_INDENT + 'Firmware return error')
				logger.info(3*LOG_INDENT + 'Avoiding iteration ... ')
				log['avoid_iteration'] = True# Just a flag to avoid taxpayer logs to be updated with this sync/init iteration (they must not be updated because there was a firmware problem)
				_Utilities.handle_forest_cron_error('Firmware.response.code was not 200',logger=logger)
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
	





