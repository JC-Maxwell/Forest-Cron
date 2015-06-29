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

# ======================================================== MODULE CODE

# Firmware url:
FIRMWARE_URL = _Constants.FIRMWARE_URL
CALLING_FIRMWARE = '         Sending request to Forest-Firmware'

def isa(**params):
	try:
		# return { 'new' : [], 'updated' : [] }
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
			logger.critical('Firmware error')
			return { 'new' : [], 'updated' : [] }
	except Already_Handled_Exception as already_handled_exception:
		raise already_handled_exception
	except Exception as e:
		# logger.critical(e.message)
		already_handled_exception = Already_Handled_Exception(e.message)
		raise already_handled_exception






