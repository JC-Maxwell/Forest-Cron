# -*- coding: utf-8 -*-

#  ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗ 
# ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝ 
# ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
# ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
# ╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
#  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 

# Description: contains initialization configuration

# ======================================================== DEPENDENCIES

from General import config as _General_Config

# ======================================================== CODE

LOGGING_CONFIG = _General_Config.general['logging']

initialization = {
	'logging' : {
		'process_path' : '/var/log/supervisord/Forest/Cron/Initialization',
		'process_file_name' : 'init',
		'file_extension' : LOGGING_CONFIG['file_extension'],
		'level' : LOGGING_CONFIG['level'],
		'format' : ' |%(date)-13s|%(hour)-10s|%(process_name)-12s|%(percentage_done)-7s|%(current_taxpayer_index)-7s|%(total_taxpayers)-7s|%(identifier)-16s|%(new)-19s|%(stored)-19s|%(year_initialized)-19s|%(month_initialized)-19s|%(percentage_initialized)-19s|%(message)s',
		'table_row_limit' : 50,
		'table_lengths' : {
			'date' : 13,
			'hour' : 10,
			'process_name' : 12,
			'percentage_done' : 7,
			'current_taxpayer_index' : 7,
			'total_taxpayers' : 7,
			'identifier' : 16,
			'new' : 19,
			'stored' : 19,
			'year_initialized' : 19,
			'month_initialized' : 19,
			'percentage_initialized' : 19
		},
		'table_titles' : {
			'date' : 'Day',
			'hour' : 'Hour',
			'process_name' : 'Thread',
			'percentage_done' : '%',
			'current_taxpayer_index' : 'No',
			'total_taxpayers' : 'Of',
			'identifier' : 'Identifier',
			'new' : 'SAT New CFDIs',
			'stored' : 'F Stored CFDIs',
			'year_initialized' : 'Year Initialized',
			'month_initialized' : 'Month Initialized',
			'percentage_initialized' : '% Initialized'
		}
	},# End of logging
	'threads' : 1
}# End of initialization

