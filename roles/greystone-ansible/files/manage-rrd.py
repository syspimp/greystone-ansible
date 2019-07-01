#!/usr/bin/python3

import rrdtool
import os
import sys 
from decimal import Decimal

DATABASE_PATH = '/tmp/'
LAST_DAY_GRAPH_FILE = '/tmp/{{ greystone_graph_name }}.png'
COLORS = ('#AA3939', '#226666', '#AA6C39', '#2D882D')
METER_NAMES = {
    '{{ greystone_meter_number }}': '{{ greystone_meter_name }}'
}
GRAPH_STARTDATE = '1546300800' # 1/1/2019 00:00:00
# this is for the interval power comsumption
# for example, I never consume more than 2 kilowatts at any moment
# daily would use "100 and 0"
# because I consume up to 60 or so kwh a day
UPPERLIMIT_FOR_GRAPH = "2"
LOWERLIMIT_FOR_GRAPH = "0"
def sensor_name(id):
    if SENSOR_NAMES.has_key(id):
        return SENSOR_NAMES[id]
    else:
        return id

def create_rrd_unless_exists(filename):
    if os.path.isfile(filename):
        return

    print("Creating RRD database file %s" % filename)
    rrdtool.create(
        filename,
        '--step', '300', '--start', GRAPH_STARTDATE,
        'DS:ds0:GAUGE:900:U:U',
        'RRA:AVERAGE:0.5:1:300',
        'RRA:AVERAGE:0.5:6:1800',
        'RRA:AVERAGE:0.5:24:7200',
        'RRA:AVERAGE:0.5:288:86400',
        'RRA:MAX:0.5:6:1800',
        'RRA:MAX:0.5:24:7200',
        'RRA:MAX:0.5:288:86400'
    )

def graph_last_day():
    print("Creating Graphs ...")
    defs = []
    lines = []
    i = 1
    current_power = ['COMMENT: \l']
    for meter, name in METER_NAMES.items():
        color = COLORS[i % len(COLORS)];
        defs.append('DEF:' + meter + '=' +
                    DATABASE_PATH + sys.argv[1] + '.rrd:ds0:AVERAGE')
        lines.append('LINE1:' + meter + color + ':' + name)
        current_power.append('GPRINT:' + meter +
                             ':LAST:' + name + '\: %4.2lf\l')

    params = [
        LAST_DAY_GRAPH_FILE,
        '-a', 'PNG',
        '-w', '500',
        '-h', '250',
        '--start', '-259200',
        '--end', 'now',
        '--lower-limit', LOWERLIMIT_FOR_GRAPH,
        '--upper-limit', UPPERLIMIT_FOR_GRAPH,
        '--rigid',
        '--vertical-label', 'KWH'] + defs + lines + current_power


if len(sys.argv) > 2:
    print(sys.argv)
    filename = sys.argv[1] + '.rrd'
    #kwh = sys.argv[2]
    # convert kwh to negative watts to offset solar power graph
    kwh = float(sys.argv[2]) * 1000 * -1
    if sys.argv[3]:
      timestamp = os.popen('date -d "' + sys.argv[3] + '" "+%s"').read()
    else:
      timestamp = "N"
    create_rrd_unless_exists(DATABASE_PATH + filename)
    print("updating rrd file with timestamp %s" % timestamp)
    error = rrdtool.update(DATABASE_PATH + filename, "%s:%s" % (timestamp.strip(),float(kwh)))
    print("%s used %.2f kwh of power on %s" % (sys.argv[1], float(kwh), timestamp))
    graph_last_day()
else:
    print("Usage: " + sys.argv[0] +  "<filename of graph to create> <unit to graph> <optional timestamp or letter N for now [default]>")

