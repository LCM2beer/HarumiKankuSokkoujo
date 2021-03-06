#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
import time
import os
import subprocess
import bme280

ROOTDIR = "/home/pi/HDO-Display"
CLIMATEHTML = ROOTDIR + "/html/climate.html"
CLIMATEBASE = ROOTDIR + "/html/climate.html.base"
GRAPHHTML = ROOTDIR + "/html/graph.html"
GRAPHBASE = ROOTDIR + "/html/graph.html.base"
GNUPLOT = "/usr/bin/gnuplot"
PLTFILE = ROOTDIR + "/bin/climate.plt"
PLTBASE = ROOTDIR + "/bin/climate.plt.base"

climatepngfull = ""


nowtemp, nowpress, nowhumid =  bme280.readData()
tmin = (int(nowtemp / 5) -1) *5
tmax = (int(nowtemp / 5) +3) *5
hmin = (int(nowhumid / 5) -1) *5
hmax = (int(nowhumid / 5) +3) *5

while 1:

    ## get temp and humidity

    nowtemp, nowpress, nowhumid =  bme280.readData()


    ## get localtime and check date
    logfile = ROOTDIR + '/data/' \
        + time.strftime("%Y-%m-%d") + '-logger.txt'
    
    logwrite = open(logfile, 'a')

    nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
    logwrite.write('{0} {1:-6.1f} {2:6.1f} {3:6.1f}\n'.\
    format(nowtime, nowtemp, nowhumid, nowpress))

    logwrite.close

    ## input data to climate.html
    ftemp = nowtemp * 9 /5 +32
    heatindex = -42.379 + 2.04901523 * ftemp + 10.14333127 * nowhumid\
     - 0.22475541 * ftemp * nowhumid - 6.83783e-3 * ftemp ** 2\
     -5.481717e-2 * nowhumid ** 2 + 1.22874e-3 * ftemp ** 2 * nowhumid\
     +8.5282e-4 * ftemp * nowhumid ** 2 - 1.99e-6 * ftemp ** 2 * nowhumid ** 2
    cheati = (heatindex - 32) * 5 / 9
    discomi = 0.81 * nowtemp + 0.01 * nowhumid * (0.99 * nowtemp - 14.3) + 46.3

    clhtml = codecs.open(CLIMATEHTML, 'w', 'utf_8')
    clbase = codecs.open(CLIMATEBASE, 'r', 'utf_8')
    for cbline in clbase:
        cline1 = cbline.replace('$$date$$', time.strftime("%Y-%m-%d"))\
        .replace('$$time$$', time.strftime("%H:%M"))\
        .replace('$$temp$$', '{0:-6.1f}'.format(nowtemp))\
        .replace('$$humid$$', '{0:6.1f}'.format(nowhumid))\
        .replace('$$press$$', '{0:6.1f}'.format(nowpress))

        if heatindex < 80:
           cline2 = cline1.replace('$$heatindex$$', '{0:6.1f}'.format(cheati))
        elif heatindex < 90:
           cline2 = cline1.replace('$$heatindex$$', '<span style=\"background-color:yellow;\">{0:6.1f}</span>'.format(cheati))
        elif heatindex < 103:
           cline2 = cline1.replace('$$heatindex$$', '<span style=\"background-color:orange;">{0:6.1f}</span>'.format(cheati))
        elif heatindex < 125:
           cline2 = cline1.replace('$$heatindex$$', '<span style=\"background-color:red;\">{0:6.1f}</span>'.format(cheati))
        else:
           cline2 = cline1.replace('$$heatindex$$', '<span style=\"background-color:black;color=white;\">{0:6.1f}</span>'.format(cheati))

        if discomi < 70:
           cline3 = cline2.replace('$$discomfort$$', '{0:6.1f}'.format(discomi))
        elif discomi < 75:
           cline3 = cline2.replace('$$discomfort$$', '<span style=\"background-color:yellow;\">{0:6.1f}</span>'.format(discomi))
        elif discomi < 80:
           cline3 = cline2.replace('$$discomfort$$', '<span style=\"background-color:orange;\">{0:6.1f}</span>'.format(discomi))
        elif discomi < 85:
           cline3 = cline2.replace('$$discomfort$$', '<span style=\"background-color:red;\">{0:6.1f}</span>'.format(discomi))
        else:
           cline3 = cline2.replace('$$discomfort$$', '<span style=\"background-color:black;color=white;\">{0:6.1f}</span>'.format(discomi))

        clhtml.write(cline3)
    clhtml.close
    clbase.close
    
    ## gnuplot graph
    if os.access(climatepngfull, os.F_OK): 
       os.remove(climatepngfull)
    climatepng = "climate" + time.strftime("%Y%m%d%H%M") + ".png"
    climatepngfull = ROOTDIR + "/html/" +  climatepng
    graphht = codecs.open(GRAPHHTML, 'w', 'utf_8')
    graphbs = codecs.open(GRAPHBASE, 'r', 'utf_8')
    for grpline in graphbs:
        grp1 = grpline.replace('$$climatepng$$', climatepng)
        graphht.write(grp1)
    graphht.close
    graphbs.close

    if tmin > nowtemp:
        tmin = tmin -5
        tmin = tmax -5
    if tmax < nowtemp:
        tmin = tmin +5
        tmin = tmax +5
    if hmin > nowhumid:
        hmin = hmin -5
        hmin = hmax -5
    if hmax < nowhumid:
        hmin = hmin +5
        hmin = hmax +5


    plttd = codecs.open(PLTFILE, 'w', 'utf_8')
    pltbs = codecs.open(PLTBASE, 'r', 'utf_8')
    for pltline in pltbs:
        plt1 = pltline.replace('$$datalog$$', "\"" + logfile + "\"")\
        .replace('$$climatepng$$', climatepngfull)\
        .replace('$$tmin$$', str(tmin)).replace('$$tmax$$', str(tmax))\
        .replace('$$hmin$$', str(hmin)).replace('$$hmax$$', str(hmax))
        plttd.write(plt1)
    plttd.close
    pltbs.close

    subprocess.call([GNUPLOT, PLTFILE])

    time.sleep(60 - int(time.strftime("%S")))

