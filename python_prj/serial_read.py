import serial
import time
import sys

ser = serial.Serial()
ser.port = sys.argv[1]
ser.baudrate = 115200
ser.timeout = None;
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits

try: 
    ser.open()
except Exception, e:
    print "error open serial port: " + str(e)
    sys.exit(-1)

log = open(sys.argv[2], 'a')
count = 0;

if ser.isOpen():
    while True:
        try:
            ser.flushInput() #flush input buffer, discarding all its contents
            ser.flushOutput() #flush output buffer, aborting current output 
                         #and discard all that is in buffer

            numOfLines = 0
            while True:
                response = ser.readline().strip()
                if response:
                    print '%s: %s' % (time.ctime(), response.decode())
                    log.write('%s: %s\n' % (time.ctime(), response.decode()))
                    #print '%f: %s' % (time.time(),time.strftime("%T"), response.decode())
                count += 1
                #if count % 2 == 0:
                    #print "getthis..."
                    #ser.write("getthis\n")

            ser.close()
        except Exception, e1:
            print "Error: " + str(e1)

else:
    print "cannot open serial port "

log.close()
