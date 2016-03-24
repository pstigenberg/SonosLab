#!/usr/bin/env python
import os
import io
import time
import sys
import soco

from soco import SoCo
from os import listdir
from os.path import isfile, join

# Usage
# -----------------------------------------------------------------------------------
# You will need the IP to the Sonos. Add argument -d to search for sonos players
# Create a .txt file in the dropbox folder with the prefix 'play' in the filename
# Add the ID from the spotify uri in the file
# Arguments
# -d will list sonos players in the network with name and IP
# -s will stop the configured player

# Configuration
# -----------------------------------------------------------------------------------
sonos_ip = '192.168.0.51'
sonos_volume = 8
sonos_song_timeout = 20 # 0 = no timeout
track_uri = 'x-sonos-spotify:spotify%3Atrack%3A[ID]?sid=9'
dropbox_path = '~/Dropbox/Tekla'
file_prefix = 'play'
id_placeholder = '[ID]'

if __name__ == '__main__':
	
	# get arguments
	argument = ''
	if len(sys.argv[1:]) > 0:
		argument = sys.argv[1:][0]
		
	# check if discovery mode
	if argument == '-d':
		for sonos_players in soco.discover():
			print sonos_players.player_name
			print sonos_players.ip_address
			sys.exit()
	
	# init sonos
	directory_path = os.path.expanduser(dropbox_path)
	sonos = SoCo(sonos_ip) 
	sonos.volume = sonos_volume
	state = ''
	
	# check if we should stop the plaver
	if argument == '-s':
		sonos.stop();
		sys.exit()
	
	# enter main loop
	while True:
		state = sonos.get_current_transport_info()['current_transport_state']
		
		if state  == 'PLAYING':
			print 'Playing song. Waiting for it to finish...'
		else:			
			print 'checking for files...'
		
			# get files from directory
			file_list = [f for f in listdir(directory_path) if isfile(join(directory_path, f))]
		
			# pick the first file that starts with file_prefix
			song_id = ""
			if len(file_list) > 0:
				for file in file_list:
					if file.startswith(file_prefix):
						full_filepath = directory_path + '/' + file
						with io.open(full_filepath, 'r') as fileobj:
							song_id = fileobj.read()
						print 'File (' + file + ') found with ID: ' + song_id
						os.remove(full_filepath)
						print 'File deleted: ' + file
						break
		
			# play song for sonos_song_timeout seconds
			if len(song_id) > 0:
				sonos.play_uri(track_uri.replace(id_placeholder, song_id))
				track = sonos.get_current_track_info()
				print track['title']
				sonos.pause()
				sonos.play()
				if sonos_song_timeout > 0:
					print 'Timeout set to ' + str(sonos_song_timeout) + ' seconds. Waiting...'
					time.sleep(sonos_song_timeout)
					sonos.stop()
					
		time.sleep(1)