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
CALLING_FIRMWARE = '         Sending request to Forest-Firmware'

def callback(**params):
	try:
		# return { 'new' : [], 'updated' : [] }
		logger = None
		if 'logger' in params:
			logger = params['logger']
			del params['logger']
		taxpayer = params['taxpayer']
		del params['taxpayer']
		url = FIRMWARE_URL
		sl1_execution_log = params['sl1_execution_log']
		del params['sl1_execution_log']
		payload = params
		headers = {'content-type':'application/json'}
		firmware_result = requests.post(url, data=json.dumps(payload), headers=headers)
		if firmware_result.status_code == 200:
			firmware_result_json = firmware_result.json()
			sl1_execution_log['firmware']['new'] = len(firmware_result_json['new'])
			sl1_execution_log['firmware']['update'] = len(firmware_result_json['updated'])
			return firmware_result_json
		else:
			if logger is not None:
				logger.critical('Firmware error')
				logger.critical(firmware_result)
			return { 'new' : [], 'updated' : [] }	
	except Exception as e:
		logger.info(3*LOG_INDENT + str(e))
		_Utilities.update_taxpayer_firmware_timeout(taxpayer,logger=logger)
		raise e

def isa(**params):
	timeout = params['timeout']
	# Execute firmware with a timeout of 10 seconds
	firmware_result_json = _Utilities.set_timeout(callback,kwargs=params,timeout_duration=timeout,default={ 'new' : [], 'updated' : [] })
	return firmware_result_json
	





