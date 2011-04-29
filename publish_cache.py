#!/usr/bin/python
''' This script is for browsing through local cache and return a set of contents'''
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



import os
base = "ccnx:/ccnx.org/"
myset = set()
mylist = []


if __name__ == '__main__':
    print 'This is not supposed to run as standalone module'

def __browsecache__():
    din, dout = os.popen4("ccnlsrepo ccnx:/ccnx.org/")
    out = dout.read()
    elements = out.split('segment 0\n')[-1].split('\n')
    #print elements
    for item in elements:
        mylist.append(base + item)

    while len(mylist) > 0:
        ele_now = mylist.pop(0)
        if ele_now not in myset and ele_now != base:
            myset.add(ele_now)
        #   mystr = "ccnlsrepo" + base + ele_now
            print ele_now
            din, dout1 = os.popen4("ccnlsrepo " + ele_now)
            out1 = dout1.read()
        #    print out1
            elements1 = out1.split('segment 0\n')[-1].split('\n')
    #    print elements1
            for item1 in elements1:
                if item1 != '' and item1.count('%') == 0:
                #fix trailing /
                    if ele_now[-1] != '/':
                        mylist.append(ele_now + '/' + item1)
                    else:
                        mylist.append(ele_now + item1)
    myset1 = set()
#longest string match
    for item in myset:
        for item1 in myset:
            if item in item1:
                item = item1                
        myset1.add(item)                      
   # print myset1
    return sorted(myset1)

def __getpit__():
    ein, eout = os.popen4("ccndstatus")
    pit_stat = eout.read()
    pit_table = pit_stat.split('Forwarding\n')[0]
    return pit_stat
