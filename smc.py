#!/usr/bin/env python
from __future__ import division
from seism import *

def load_smc_v1(filename):
    record_list = []
    
    # loads station into a string
    fp = open(filename, 'r')
    channels = fp.read()
    fp.close()

    # splits the string by channels
    channels = channels.split('/&')
    del(channels[len(channels)-1])

    # splits the channels
    for i in range(len(channels)):
        channels[i] = channels[i].split('\r\n')

    # clean the first row in all but the first channel
    # this row corresponds to the channel delimiter
    for i in range(1,len(channels)):
        del channels[i][0]

    for i in range(len(channels)):

        # check this is the uncorrected acceleration data
        ctype = channels[i][0][0:24].lower()
        if ctype != "uncorrected accelerogram":
            return channels, 0


        tmp = channels[i][3].split('.')
        network = tmp[1]
        station_id = tmp[2]

        # get location's latitude and longitude 
        tmp = channels[i][4].split()
        location_lati = tmp[3][:-1]
        location_longi = tmp[4]
        depth = 0


        # get station name
        station = channels[i][5][0:40].strip()

        # get data type 
        tmp = channels[i][5].split()
        dtype = tmp[-1]
        if dtype == "Acceleration": 
        	dtype = 'a'
        elif dtype == "Velocity": 
        	dtype = 'v'
        elif dtype == "Displacement": 
        	dtype = 'd'
        else: 
        	dtype = "Unknown"


        # get orientation, convert to int if it's digit 
        tmp = channels[i][6].split()
        orientation = tmp[2]
        if orientation.isdigit():
            orientation = int(orientation)

        # get time 
        # start_time = channels[i][3][37:80]
        tmp = channels[i][14].split()
        hour = float(tmp[0])
        minute = float(tmp[1])
        seconds = float(tmp[2])
        # fraction = float(tmp[4])
        fraction = float(tmp[3])

        tzone = channels[i][3].split()[-2]
   

        # get number of samples and dt 
        tmp = channels[i][27].split()
        samples = int(tmp[0])
        dt = 1/int(tmp[4])

        # get signals' data 
        tmp = channels[i][28:]
        signal = str()
        for s in tmp:
            signal += s
        signal = signal.split()
         
         # make the signal a numpy array of float numbers
        data = []
        for s in signal: 
        	data.append(float(s)) 
        # print data 
        data = np.array(data)



        # =================For Testing==================================================
        # print "==================================================================="
        # print "channel: " + ctype
        # print "samples: " + str(samples)
        # print "dt: " + str(dt)
        # print "data type: " + dtype 
        # print data
        # record = seism_record(samples, dt, data, dtype, station, location_lati, location_longi, depth, hour, 
        #     minute, seconds, fraction, tzone, orientation)
        record = seism_record(samples, dt, data, dtype, station, location_lati, location_longi, depth = depth, 
            orientation = orientation, tzone = tzone, fraction = fraction, minute = minute, seconds = seconds, hour = hour)
        # record.print_attr()
        # signal = seism_signal(dt=dt, samples=samples, data=data, type=dtype)
        # signal = seism_signal(samples,dt,data,dtype)
        # signal = seism_signal(samples,dt,type=dtype,data=data)

        # signal.plot('s')
        record.plot('s')
        record_list.append(record)

    # return channels, 1
    # print record_list
    # print station_id
    # return a list of records and corresponding network code and station id 
    return record_list, network, station_id


def process_smc_v1(record_list, network, station_id):
    """
    The function process a list of records by converting orientation and multiplying data 
    """
    # if there are more than three channels, save for later 
    if len(record_list) > 3:
        print "==[The function is processing files with three channels only.]=="
        return 

    else: 
        for record in record_list:
            # process orientation **modify later**: multiply by -1 and convert  
            if record.orientation == 180 or record.orientation == 360:
                orientation = 'N'

            elif record.orientation == 270 or record.orientation == 90: 
                orientation = 'E'
 
            elif record.orientation == "Up" or record.orientation == "Down":
                orientation = 'Z'

            # header = "# " + str(record.hour) + ":" + str(record.minute) + ":" + str(record.seconds) + ":" + str(record.fraction) + " Samples: " 
            # + str(record.samples) + " dt: " + str(record.dt) + "\n"

            # TODO: add time string to header 
            header = "#Samples: " + str(record.samples) + " dt: " + str(record.dt) + "\n"

            # generate a text file 
            filename = network + "." + station_id + "." + orientation + ".txt"
            fp = open(filename, 'a')
            fp.write(header)
            # process data and write into file  
            for d in np.nditer(record.data):
                fp.write(str(d*981)+"\n")
            fp.close()
        return 
    return


# NOT USING
def print_smc_v1(filename, data):
    """
    The function generate files for each channel/record 
    """
    # open(filename, 'a').close()
    pass 

# test with two files 
record_list, network, station_id = load_smc_v1('NCNHC.V1')
process_smc_v1(record_list, network, station_id)

record_list, network, station_id = load_smc_v1('CIQ0028.V1')
process_smc_v1(record_list, network, station_id)


# TODO: 
# 1. change time parameters to an array of float number; or pass a single string as parameter, then process within subclass? 
