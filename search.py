import os
while True:
	ip = raw_input("Search: ").strip()
	garbage, neig = os.popen4("ccndstatus|grep ccnx:/ccnx.org|grep -v self|awk '{print $1}'")
	neigb = neig.read()
	print "Searching...."
	my_result = set()
	for item in neigb.split('\n'):
	    if item != '':
		#print item.strip()+ '/' + ip
		garbage, op = os.popen4("ccnslurp %s"%(item.strip()+ '/' + ip))
		output = op.read()
		print output

