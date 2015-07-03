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

FIRMWARE_URL = forest_1
FIRMWARE_URL_INIT = forest_2
FOREST_AZURE = 'http://forest-sat.cloudapp.net'

# CFDIs status:
CANCELED_STATUS = 'canceled'

# Processes (syncrhonization layer 2 and incident handler are for all taxpayers)
SYNCHRONIZATION = 'synchronization'
CRON_PROCESSES = 'cron_processes'
SL1 = 'synchronization_layer_1'
EQUALIZATION = 'equalization'
INITIALIZATION = 'initialization'

CONSTANTS_BY_PROCESS_NAMES = {
	'synchronization_layer_1' : SYNCHRONIZATION,
	'equalization' : SYNCHRONIZATION,
	'initialization' : INITIALIZATION
}# End of CONSTANTS_BY_PROCESS_NAMES

# Status
STATUS_DATES = {
	'synchronization_layer_1' : 'last_sl1',
	'equalization' : 'last_equalization',
	'initialization' : 'initialized_at'
}# End of STATUS_DATES

# Other
ZLATAN = '\\0/'
LIMIT_LOGS_PER_TAXPAYER = 10

