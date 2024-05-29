import numpy
import time
from scipy.signal import argrelextrema
import src.gdpr as GDPR
import matplotlib.pyplot as plt
from time import sleep
import serial
from termcolor import colored

offset=35
AMP=255-offset
Min_DRange=7500 # minimum dinamic range

def write(_Obj,_String):
	_Obj.write(bytes(_String+'\n', 'ASCII'))
	#sleep(0.05)
#	print(_String)

def F2I(_F): #frequncy to index
	return int(_F/UPS)

def Send2Wristband(_Obj,_Frq,_Amp):
	if(_Frq==0):
		write(_Obj,"%d 0 0" %  (_Amp+offset))
	elif(_Frq==1):
		write(_Obj,"%d %d 0" % ((_Amp)+offset,(_Amp)+offset))
	elif(_Frq==2):
		write(_Obj,"0 %d 0" %  (_Amp+offset))
	elif(_Frq==3):
		write(_Obj,"0 %d %d" % ((_Amp)+offset,(_Amp)+offset))
	elif(_Frq==4):
		write(_Obj,"0 0 %d" %  (_Amp+offset))
	elif(_Frq==5):
		write(_Obj,"0 0 0")


UPS=50  #updates per second
UB=7500 #upperband frequncy
LB=300  #Lowerband frequncy
NOI=5   #Number of frequncy intervals

EPF=10**(numpy.log10(UB/LB)*(1/NOI)) #exponential factor for division of frequncy band into intervals
LI=F2I(LB)
UI=F2I(UB)+1

FRQP=numpy.full(NOI,range(0,NOI))
pcm_history=numpy.array([],dtype=numpy.int16)
PHL=10 #pcm history length in seconds

ear = GDPR.GDPR(updatesPerSecond = UPS)
ear.stream_start()

Portal = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=.1)

#PC=numpy.full(PHL*UPS,range(0,PHL*UPS))
#PC2=numpy.full(PHL*UPS,[32700]*(PHL*UPS))


#plt.ion()  # tbr
#fig = plt.figure() 
#ax = fig.add_subplot(111)
#sleep(0.12) 
#line1, = ax.plot(PC,PC2, 'b-') 
last_pcm=0

while True:
    if not ear.data is None and not ear.fft is None:
#        print(numpy.mean(ear.data**2))
#        pcm =numpy.sqrt(   numpy.average(  ( (numpy.abs(ear.data)).astype(numpy.float64) )**2   )   ) # RMS of the signal
        pcm=numpy.max(numpy.abs(ear.data))
        if pcm != last_pcm:
            pcm_history=numpy.append(pcm_history,[pcm])
            last_pcm=pcm
        if(len(pcm_history) > PHL*UPS):
            pcm_history=numpy.delete(pcm_history,0)
#            line1.set_ydata(pcm_history) #tbr
#            fig.canvas.draw()   #tbr
#            fig.canvas.flush_events()  #tbr

        Minp=numpy.min(pcm_history)
        Maxp=numpy.max(pcm_history)
        if (Maxp-Minp)<Min_DRange:
            Maxp=Minp+Min_DRange
        pcmc=abs((pcm-Minp)/(Maxp-Minp)) # correctd pcm percentage
        Power=numpy.zeros(NOI)
        for i in range(0,NOI):
            P=0
            for amp in ear.fft[F2I(LB*(EPF**i)):F2I(LB*(EPF**(i+1)))]:
                P+=amp**2  #parseval's eqn
            Power[i]=P
        Power=10*numpy.log10(Power)
        Power-=numpy.min(Power)
        print(pcm,pcmc,Maxp,Minp)
        Main_Frq=numpy.argmax(Power)
#        Amp=(AMP/15)*numpy.log2(pcmc*(2**15)+1) #pcm ranges form 0 to 2**15 this maps it to 0 to 220
#        Amp=AMP*pcmc
        if(pcmc>0.05):
             pcmc=(pcmc-0.05)/0.95
             Amp=AMP*(numpy.log10(pcmc*9+1))
             Send2Wristband(Portal,Main_Frq,abs(Amp))
        else:
             pcmc=0
#        Amp=AMP*(numpy.log10(pcmc*9+1))
#        if(pcmc>0.05):
#             Send2Wristband(Portal,Main_Frq,abs(Amp))
#        else:
             Send2Wristband(Portal,5,0) # send zero

#        line1.set_ydata(Power) #tbr
#        fig.canvas.draw()   #tbr
#        fig.canvas.flush_events()  #tbr

