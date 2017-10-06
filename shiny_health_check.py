import urllib.request
import time
import os
import datetime
import json

with open('settings.json') as json_data:
    settings = json.load(json_data)


def alert(recipients, subject, content):
	with open("message.txt", "w") as f:
		f.write(content)

	for recipient in recipients:
		email_command = "cat message.txt | mail -s '"+subject+"' "+recipient
		print(email_command)
		os.system(email_command)

shiny_health_url = "http://"+settings['host']+":"+str(settings['port'])+"/__health-check__"

#hit with urllib
try:	
	response_raw = urllib.request.urlopen(shiny_health_url)	
	if response_raw.status != 200:
		subject = 'childes-db Shiny App alert: non-200 response from server'
		content = "The Shiny server at "+settings['host']+":"+str(settings['port'])+ " has responded with status "+str(response_raw.status)	
		alert(settings['emails'], subject, content)
		exit()
	else:		
		response = response_raw.read().decode("utf-8") 
		print(response)

except:
	subject = 'childes-db Shiny App alert: no response from server'
	content = "The Shiny server at "+settings['host']+":"+str(settings['port'])+ " is not responding"	
	alert(settings['emails'], subject, content)
	exit()

response_items = [line.split(": ") for line in response.split("\n")]
response_items = [x for x in response_items if len(x) ==2]
response_dict = dict(zip([x[0] for x in response_items], [x[1] for x in response_items]))
print(response_dict)


#checks
failed = []
if float(response_dict['active-connections']) > 100:
	failed += ['active-connections']

if float(response_dict['cpu-percent']) > .9:
	failed += ['cpu-percent']

if float(response_dict['swap-percent']) > .5:
	failed += ['swap-percent']	

if float(response_dict['load-average']) > .8:		
	failed += ['swap-percent']	

if len(failed) > 0:
	if len(failed) == 1:
		issue = failed[0]+ " out of acceptable bounds"
	else:
		issue = "multiple issues"	
	subject = 'childes-db Shiny App alert: '+ issue
	content = "For the Shiny server at "+settings['host']+":"+str(settings['port'])+ " the following variable(s) is/are outside of acceptable bounds: "+', '.join(failed)
	content += "\n\n"+response

	alert(settings['emails'], subject, content)
	exit()

# if everything is normal, save it locally
else:
	# append to the log that the server was checked; include local time
	with open(settings['host']+".log", "a") as f:
		f.write("All OK at "+str(datetime.datetime.now())+'\n')
