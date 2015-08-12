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
AVOID_FIRMWARE = False
DEFAULT_FIRMWARE_RESULT = {
	'new' : [],
	'updated' : []
}# End of DEFAULT_FIRMWARE_RESULT

def callback(**params):
	try:
		logger = None
		if 'logger' in params:
			logger = params['logger']
			del params['logger']
		taxpayer = params['taxpayer']
		del params['taxpayer']
		url = FIRMWARE_URL
		log = params['log']
		del params['log']
		payload = params
		headers = {'content-type':'application/json'}
		if AVOID_FIRMWARE is not True:
			firmware_result = requests.post(url, data=json.dumps(payload), headers=headers)
			if firmware_result.status_code == 200:
				firmware_result_json = firmware_result.json()# Comment in case of simulation
				log['firmware']['new'] = len(firmware_result_json['new'])
				log['firmware']['update'] = len(firmware_result_json['updated'])
				return firmware_result_json
			else:
				if logger is not None:
					logger.critical('Firmware error')
					logger.critical(firmware_result)
				return DEFAULT_FIRMWARE_RESULT
		else:
			return DEFAULT_FIRMWARE_RESULT
	except Exception as e:
		logger.info(3*LOG_INDENT + str(e))
		# -------------------------------------------------------------------
		# bugSolved 12/Ago/15 
		# Event: timeout value was becoming longer and longer because of connection problems (firmware servers could not be reached due to connection problems instead of logic problems)
		# _Utilities.update_taxpayer_firmware_timeout(taxpayer,logger=logger)# firmware timeout updating was avoided
		# -------------------------------------------------------------------
		raise e

def isa(**params):
	timeout = params['timeout']
	# Execute firmware with a timeout of n seconds
	firmware_result_json = _Utilities.set_timeout(callback,kwargs=params,timeout_duration=timeout,default={ 'new' : [], 'updated' : [] })
	return firmware_result_json
	





