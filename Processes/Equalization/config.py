# -*- coding: utf-8 -*-

#  ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗ 
# ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝ 
# ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
# ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
# ╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
#  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 

# Description: contains equalization configuration

# ======================================================== DEPENDENCIES

from General import config as _General_Config

# ======================================================== CODE

LOGGING_CONFIG = _General_Config.general['logging']
DEFAULT_LENGTH = 30

equalization = {
	'logging' : {
		'process_path' : '/var/log/supervisord/Forest/Cron/Equalization',
		'process_file_name' : 'eqdb',
		'file_extension' : LOGGING_CONFIG['file_extension'],
		# 'format' : '%(processName)-6s %(message)-85s %(module)30s:%(lineno)4d --- %(asctime)s',# Multithread, process is logged
		'format' : ' |%(date)-13s|%(hour)-10s|%(process_name)-12s|%(percentage_done)-7s|%(current_taxpayer_index)-6s|%(total_taxpayers)-6s|%(identifier)-16s|%(forest_db)-30s|%(corebook_db)-30s|%(missing_in_forest_db)-30s|%(missing_in_cb_db)-30s|%(stored)-30s|%(errors)-30s|%(message)s',
		'level' : LOGGING_CONFIG['level'],
		'table_row_limit' : 50,
		'table_lengths' : {
			'date' : 13,
			'hour' : 10,
			'process_name' : 12,
			'percentage_done' : 7,
			'current_taxpayer_index' : 6,
			'total_taxpayers' : 6,
			'identifier' : 16,
			'forest_db' : DEFAULT_LENGTH,
			'missing_in_forest_db' : DEFAULT_LENGTH,
			'corebook_db' : DEFAULT_LENGTH,
			'missing_in_cb_db' : DEFAULT_LENGTH,
			'stored' : DEFAULT_LENGTH,
			'errors' : DEFAULT_LENGTH
		},
		'table_titles' : {
			'date' : 'Day',
			'hour' : 'Hour',
			'process_name' : 'Thread',
			'percentage_done' : '%',
			'current_taxpayer_index' : 'No',
			'total_taxpayers' : 'Of',
			'identifier' : 'Identifier',
			'forest_db' : 'CFDIs in Forest DB',
			'corebook_db' : 'CFDIs in CB DB',
			'missing_in_forest_db' : 'Missing CFDIs in Forest DB',
			'missing_in_cb_db' : 'Missing CFDIs in CB DB',
			'stored' : 'CFDIs stored in CB DB',
			'errors' : 'Errors'
		}
	},# End of logging
	'threads' : 1
}# End of equalization
