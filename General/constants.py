# -*- coding: utf-8 -*-

#  ██████╗ ██████╗ ███╗   ██╗███████╗████████╗ █████╗ ███╗   ██╗████████╗███████╗
# ██╔════╝██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝██╔════╝
# ██║     ██║   ██║██╔██╗ ██║███████╗   ██║   ███████║██╔██╗ ██║   ██║   ███████╗
# ██║     ██║   ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║╚██╗██║   ██║   ╚════██║
# ╚██████╗╚██████╔╝██║ ╚████║███████║   ██║   ██║  ██║██║ ╚████║   ██║   ███████║
#  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
                                                                               
# Description: Contains the local constants that are used in Forest-Cron

# ======================================================== DEPENDENCIES

# Native:
import logging

# ======================================================== CODE

# Paths:
THREADS_DIR = '/Threads'

# Time Out:
DEFAULT_FIRMWARE_TIMEOUT = 3600# One hour
UPDATING_FIRMWARE_TIMEOUT_RATE = 1.5
AVOID_FIRMWARE = False
DEFAULT_FIRMWARE_RESULT = {
	'new' : [],
	'updated' : []
}# End of DEFAULT_FIRMWARE_RESULT
FIRMWARE_STABLISH_CONNECTION_TIME = 2# seconds (connection to firmware must be stablished in less than this seconds)
FIRMWARE_WAITING_TIME = 2# hours (firmware response is gonna be waited for 2 hours no more)
FIRMWARE_WAITING_TIME_ON_SECONDS = FIRMWARE_WAITING_TIME*3600

# Logging
LOGGING_LEVELS = {
	'critical' : logging.CRITICAL,
	'error' : logging.ERROR,
	'warning' : logging.WARNING,
	'info' : logging.INFO,
	'debug' : logging.DEBUG,
	'notset' : logging.NOTSET
}# End of LOGGING_LEVELS

# Periods
ONE_MONTHS_PERIOD = 1
TWO_MONTHS_PERIOD = 2

# Others
LOG_SEPARATOR = '----------------------------------------------------------------------------------'
LOG_INDENT = '    '

# Firmware
forest_1 = 'http://25.186.251.198/firmware'
forest_2 = 'http://25.86.20.35/firmware'
FOREST_URL = 'http://187.189.152.68:5001/firmware'

FIRMWARE_URL = FOREST_URL
FIRMWARE_URL_INIT = forest_2
FOREST_AZURE = 'http://forest-sat.cloudapp.net'

# CFDIs status:
CANCELED_STATUS = 'canceled'
VALID_STATUS = 'valid'
CB_CANCELED_FISCAL_STATUS = 4

# Processes (syncrhonization layer 2 and incident handler are for all taxpayers)
SYNCHRONIZATION = 'synchronization'
CRON_PROCESSES = 'cron_processes'
SL1 = 'synchronization_layer_1'
EQUALIZATION = 'equalization'
INITIALIZATION = 'initialization'
UPDATING = 'updating'

FILTERS_BY_PROCESS_NAMES = {
	'equalization' : {},# Equalization query for all taxpayers
	'synchronization_layer_1' : { 'status' : SYNCHRONIZATION },# SL1 query for taxpayers in synchronization status
	'initialization' : { 'status' : { '$in' : [INITIALIZATION,UPDATING] }}# Initialization query for taxpayers in initialization or updating status
}# End of FILTERS_BY_PROCESS_NAMES

# Status
STATUS_DATES = {
	'synchronization_layer_1' : 'last_sl1',
	'equalization' : 'last_equalization',
	'initialization' : 'initialized_at'
}# End of STATUS_DATES

# Other
ZLATAN = '\\0/'
LIMIT_LOGS_PER_TAXPAYER = 10

# Telegram:
FOREST_BOT_TELEGRAM_TOKEN = '97446605:AAG2fWjMMTwIriBLGnedhJgkB-_W-KeKoQ4'

# XML contants:
EXPENSE_VOUCHER_EFFECT = 'egreso'
INCOME_VOUCHER_EFFECT = 'ingreso'
TRANSFERRED_VOUCHER_EFFECT = 'traslado'

# CFDI_types
CREDIT_NOTE_CFDI_TYPE = 'credit_note'
TRANSPORT_DOCUMENT_CFDI_TYPE = 'transport_document'
PAYROLL_CFDI_TYPE = 'payroll'
NORMAL_CFDI_TYPE = 'normal'










