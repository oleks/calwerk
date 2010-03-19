import re, datetime, urllib2, sys

from datetime import datetime
from datetime import date

def recRead(f, e, r):
    if e == []:
        return r
    while True:
        line = f.readline()
        if line == '':
            return r
        result = re.search(e[0], line)
        if result:
            r.append(result)
            return recRead(f, e[1:], r)

def daycmp(d1,d2):
    if d1[0] > d2[0]:
        return 1
    elif d1[0] == d2[0]:
        return 0
    else:  #x < y
        return -1

def repeat(c, w):
    return "" if w == 0 else c+repeat(c,w-1)

def centerline(t,l):
    tl = l - len(t)
    w = tl/2
    spc = repeat(" ", w)
    return spc + t + (spc if (tl % 2) == 0 else spc+" ")
    
def frame(t, l, v = "-", h="|", c="+"):
    l = l-2
    hb = c + repeat(v,l) + c
    print hb
    print h + centerline(t, l) + h
    print hb


def read(url, startdate=None, enddate=None):
    print url
    f = urllib2.urlopen(url)

    #read title
    r = recRead(f,[re.compile("CALNAME:(.*?)[\r\n]")],[])
    title = r[0].group(1)

    #event vars
    days = []   #will contain [date, hours, description]
    hourstotal = 0

    #regexes to find start, end and description
    startex = re.compile(r"DTSTART:(\d{8})T(\d{4})")
    endex = re.compile(r"DTEND:\d{8}T(\d{4})")
    notex = re.compile(r"SUMMARY:(.+?)\s[^\s]*\n")
    e = [startex, endex, notex]

    while True:
        #read instance of startex+endex+notex
        r = recRead(f,e,[])

        #if none read, exit infinite loop
        if r == []:
            break
        #read day and check if it's within bounds
        day = datetime.strptime(r[0].group(1), "%Y%m%d")
        if startdate != None and day < startdate:
            continue
        if enddate != None and day >= enddate:
            continue

        #get the hours
        stime = datetime.strptime(r[0].group(2), "%H%M")
        etime = datetime.strptime(r[1].group(1), "%H%M")
        dtime = etime - stime
        hours = dtime.seconds/3600.0

        #append the data
        days.append([day, hours, r[2].group(1)])
        hourstotal += hours
    f.close()

    #sort days by date
    days = sorted(days, daycmp)

    l = len(title) + 4
    for day in days:
        lt = len(str(day[1])+str(day[2])) + 20
        if  lt > l:
            l = lt
    if len(days) > 0:
        #print working hours
        frame(title, l, v="=")
        for day in days:
            s = "| " + day[0].strftime("%d-%m-%Y") + " | " + str(day[1]) + " | " + day[2]
            print s + repeat(" ", l-len(s)-2) + " |"
        frame(str(len(days)) + " dag(e), " + str(hourstotal) + " timer.", l)
    else:
        #print no working hours message
        s = "no "
        ls = len(s) + 4
        if ls > l:
            l = ls
        print title, l
        frame(title, l, "=")
        frame(s, l)

if __name__ == "__main__":
    startdate = enddate = None
    for arg in sys.argv[1:]:
        if arg.startswith("s:"):
            startdate = datetime.strptime(arg[2:], "%d-%m-%Y")
        elif arg.startswith("e:"):
            enddate = datetime.strptime(arg[2:], "%d-%m-%Y")
        else:
            read(str(arg), startdate, enddate)
