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

# Logging
LOGGING_LEVELS = {
	'critical' : logging.CRITICAL,
	'error' : logging.ERROR,
	'warning' : logging.WARNING,
	'info' : logging.INFO,
	'debug' : logging.DEBUG,
	'notset' : logging.NOTSET
}# End of LOGGING_LEVELS

# Processes (syncrhonization layer 2 and incident handler are for all taxpayers)
SYNCHRONIZATION = 'keeping_syncrhonizing'
INITIALIZATION = 'initialization'
UPDATING = 'updating'
CRON_PROCESSES = 'cron_processes'

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

# CFDIs status:
CANCELED_STATUS = 'canceled'

CONSTANTS_BY_PROCESS_NAMES = {
	'synchronization_layer_1' : SYNCHRONIZATION,
	'synchronization_layer_2' : SYNCHRONIZATION,
	'initialization' : INITIALIZATION,
	'updating' : UPDATING,
	'equalization' : SYNCHRONIZATION,
	'inicident_handler' : None
}# End of CONSTANTS_BY_PROCESS_NAMES



