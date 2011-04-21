#!/usr/bin/python
''' This script is for generating topology for ccnx deployment '''
#
# copyright (C) 2011, Susmit Shannigrahi, <susmit AT netsec DOT colostate DOT edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



import os,sys
import random
import time

name = sys.argv[1]
protocol = sys.argv[2]
ip = sys.argv[3]
self_n_c  = "ccndc add ccnx:/ccnx.org/csu/topology/" + name + "/self " + protocol + " " + ip
print self_n_c
os.system("ccndlogging none")
os.system("ccn_repo ccnrepo")
os.system(self_n_c) 

   
#publish test1 for bw, ping for ping
os.system("ccnputfile ccnx:/ccnx.org/csu/topology/" + name + "/bw test1")
os.system("ccnputfile ccnx:/ccnx.org/csu/topology/" + name + "/ping ping")


#publish final file
f = file('final', 'wb')
f.close()
ping_flag = 0
init_flag = 0
counter = 0
bw = 0.0
mbw = 0.0


w_time = random.randint(1,5)

#publish a very small ping file


while (True): #infinite loop
    time.sleep(w_time)
    os.system("rm *.temp")         

    try:
	#get you name, identified by 'self'
	#naming convension is ccnx:/csu/topology/a
	#and ccnx:/csu/topology/self
        #publish a file under ccnx:/csu/topology/a/ping
        

        get_name_self = "ccndstatus|grep self|awk '{print $1}'"
        garbage, self_name_op = os.popen4(get_name_self)
        self_name = self_name_op.read()
        self_name = self_name.split('\n')[0]

        print 'self_name', self_name
        
        #get the remote connections, identified by 'topology'
        get_conn_remote = "ccndstatus |grep topology|grep -v self| " + "awk '{print $1}'"
        print get_conn_remote
        garbage, get_remote_op = os.popen4(get_conn_remote)
        remote_set = get_remote_op.read()
        remote_set_list = str.splitlines(remote_set)
        print 'remote set', remote_set_list
        
        #if you are starting up, publish your own topology, 
        if (init_flag == 0):
            f1 = file('topology','wb')
            for remote_item in remote_set_list:
                f1.write('"' + self_name.replace('/self','') + '"' + ' -> ' + '"' +  remote_item + '"' + ' [dir=both];\n')
            f1.close

            #ccnputfile ccnx:/csu/topology/a/topology topology
            pub_name = "ccnputfile " + self_name.replace('/self','') + " topology"
            print pub_name
            os.system(pub_name)
            init_flag = 1


        else:
	#see if remotes are up by fetching file, add them to your topology
        # if you can not fetch a file, it's dead
            f1 = file('topology','wb')
            f1.close()
            f1 = file('topology','wb')
            f1.write("self ->  self\n")
            for item in remote_set_list:
                if self_name.replace('/self','') not in item:
                    print "getting file"

                    #get file
                    get_file_com = "ccngetfile " + item + " " + item.split('/')[-1] + ".temp"
                    print get_file_com
                    garbage, std_err_out = os.popen4(get_file_com)
                    std_err = std_err_out.read()
                    #mark as stale
                    if 'Cannot retrieve first block of' in std_err:
		                print 'ERR: Can not fetch anything from %s' %(item)
                    else:
                        print "successfully fetched..writting"
                        mark_stale = "ccnrm " + item + "/bw"
                        os.system(mark_stale)

                        #get delay, update dict
                        try:
                            get_ping_file_com = "ccngetfile " + item + "/ping ping1"
                            print get_ping_file_com 
                            gabage, ping_file_stdout = os.popen4(get_ping_file_com)
	                    ping_file_op = ping_file_stdout.read()
#                            print ping_file_op
                            time_p = float(ping_file_op.split("ccngetfile took:")[1].split('\n')[0].replace('ms',''))
                        except:
                            time_p = 0
                        print "RTT: ", time_p

                        #at every 30 interation, check bw and delay
                        if (counter % 5) == 0:
                            print "checking bandwidth and delay"
                            get_bw_file_com = "ccngetfile " + item + "/bw test2"
                            
#                            print get_bw_file_com
                            try:
                                ccn_rem_com = "ccnrm " + item + "/bw"
                                garbage, std_err_out1 = os.popen4(get_bw_file_com)
                                std_err1 = std_err_out1.read()
#                                print std_err1
                                ccn_rem_com = "ccnrm " + item + "/bw"
                                os.system(ccn_rem_com)
                                time_m = float(std_err1.split("ccngetfile took:")[1].split('\n')[0].replace('ms',''))
                                print "CCNGETTIME: ",time_m
                                byte = float(std_err1.split("ccngetfile took:")[1].split('\n')[1].split('got')[1].split('bytes')[0])
    
                                print "BYTES", byte
                                bw = ((byte*8)/(time_m/1000))
                                mbw = bw /(1024*1024)
                                print "Bw %s %s Mbps" %(bw, mbw)
                                
                            except:
                                print "No bw file"
                                mbw = 0
                        
                        print "Bw %s Mbps", mbw    
			f1.write('"' + self_name.replace('/self','') + '"' + ' -> ' \
+ '"' + item + '"' + ' [label= "'+ 'BW= ' + str(mbw) +'Mbps,' + 'RTT = ' + str(time_p)\
+  'ms"' + 'dir=both];\n')

                        
            f1.close()
            os.system("cp topology topology.temp")
            os.system("ccnputfile " + self_name.replace('/self','') + " topology")


        #put together your own topology
        dirlist = os.listdir(".")
        f_w = open("final", 'wb')
        f_w.write("digraph G{\n")
        f_w.close()
        f_w = open("final", 'ab')
        lines_buffer = set()


        for fname in dirlist:
            if (os.path.splitext(fname)[-1] == '.temp'):
                f = open(fname,  'r')

                for line in f:
                    print line 
                    if "self" not in line: 
                        if line not in lines_buffer: #duplicate line
                            print "here"
                            if line.split('"')[1] != line.split('"')[3]: #self_loop
                                f_w.write(line)  
                                lines_buffer.add(line)
                    
        f_w.write("}")
        f_w.close()
        os.system("dot -Tpng final -o final.png")
	counter = counter + 1


    except:
        e = sys.exc_info()[1]
        print e
