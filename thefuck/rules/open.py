# Opens URL's in the default web browser
# 
# Example:
# > open github.com
# The file ~/github.com does not exist.
# Perhaps you meant 'http://github.com'?
#
# 

def match(command, settings):
	return (command.script.startswith ('open')
			and (
			# Wanted to use this:
			# 'http' in command.stderr
			'.com' in command.script
			or '.net' in command.script
			or '.org' in command.script
			or '.ly' in command.script
			or '.io' in command.script
			or '.se' in command.script
			or '.edu' in command.script))

def get_new_command(command, settings):
	return 'open http://' + command.script[5:]
