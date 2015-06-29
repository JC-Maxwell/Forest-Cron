# -*- coding: utf-8 -*-

#  ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗ 
# ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝ 
# ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
# ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
# ╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
#  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 

# Description: contains syncrhoniztion layer 1 configuration

# ======================================================== DEPENDENCIES

from General import config as _General_Config

# ======================================================== CODE

LOGGING_CONFIG = _General_Config.general['logging']

synchronization_layer_1 = {
	'logging' : {
		'process_path' : '/var/log/supervisord/Forest/Cron/SL1',
		'process_file_name' : 'sl1',
		'file_extension' : LOGGING_CONFIG['file_extension'],
		'level' : LOGGING_CONFIG['level'],
		'format' : ' |%(date)-13s|%(hour)-10s|%(process_name)-12s|%(percentage_done)-7s|%(current_taxpayer_index)-7s|%(total_taxpayers)-7s|%(identifier)-16s|%(new)-19s|%(to_update)-19s|%(stored)-19s|%(updated)-19s|%(completed)-19s|%(pending)-19s|%(message)s',
		'table_row_limit' : 50,
		'table_lengths' : {
			'date' : 13,
			'hour' : 10,
			'process_name' : 12,
			'current_taxpayer_index' : 7,
			'total_taxpayers' : 7,
			'percentage_done' : 7,
			'identifier' : 16,
			'new' : 19,
			'to_update' : 19,
			'stored' : 19,
			'updated' : 19,
			'completed' : 19,
			'pending' : 19
		},
		'table_titles' : {
			'date' : 'Day',
			'hour' : 'Hour',
			'process_name' : 'Thread',
			'current_taxpayer_index' : 'No',
			'total_taxpayers' : 'Of',
			'percentage_done' : '%',
			'identifier' : 'Identifier',
			'new' : 'SAT New CFDIs',
			'to_update' : 'SAT Updated CFDIs',
			'stored' : 'F Stored CFDIs',
			'updated' : 'F Updated CFDIs',
			'completed' : 'F Completed CFDIs',
			'pending' : 'F Keep Pending'
		}
	},# End of logging
	'threads' : 3
}# End of general

