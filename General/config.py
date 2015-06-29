# -*- coding: utf-8 -*-

#  ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗ 
# ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝ 
# ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
# ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
# ╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
#  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 

# Description: contains Forest CRON general configuration

# ======================================================== DEPENDENCIES



# ======================================================== CODE

DEFAULT_LENGTH = 30

general = {
	'logging' : {
		'path' : '/var/log/supervisord/Forest/Cron',
		'file_name' : 'cron',
		'file_extension' : '.log',
		'time_zone' : 'America/Mexico_City',
		'format' : '%(message)-85s %(module)30s:%(lineno)4d --- %(asctime)s',
		'level' : 'info',
		# Processes table:
		'processes_file_name' : 'cron_processes',
		'processes_file_format' : ' |%(date)-13s|%(hour)-10s|%(synchronization_layer_1)-30s|%(equalization)-30s|%(initialization)-30s|%(updating)-30s|%(synchronization_layer_2)-30s|%(incident_handler)-30s| %(message)s',
		'table_row_limit' : 50,# Each X rows titles are gonna be logged again
		'default_length' : DEFAULT_LENGTH,
		'table_lengths' : {
			'date' : 13,
			'hour' : 10,
			'synchronization_layer_1' : DEFAULT_LENGTH,
			'synchronization_layer_2' : DEFAULT_LENGTH,
			'initialization' : DEFAULT_LENGTH,
			'updating' : DEFAULT_LENGTH,
			'equalization' : DEFAULT_LENGTH,
			'incident_handler' : DEFAULT_LENGTH
		},
		'table_titles' : {
			'date' : 'Day',
			'hour' : 'Hour',
			'synchronization_layer_1' : 'Synchronization Bimester',
			'synchronization_layer_2' : 'Synchronization Year',
			'initialization' :  'Initialization',
			'updating' :   'Updating',
			'equalization' :  'Equalization Forest = CB',
			'incident_handler' :  'Incident Handler'
		},
		'completed_symbol' : '\\0/'
	}# End of logging
}# End of general
