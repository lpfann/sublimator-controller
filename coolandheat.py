#!/usr/bin/python
# Programm zur Steuerung des Sublimator-Prototypen
# Autor: Dennis Paulus

#import Anweisungen der genutzten Libraries 
import spidev
import time
import RPi.GPIO as GPIO
import atexit

# Konfiguration der GPIO Pins
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT)
GPIO.output(16, True)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, True)

# Initialisierung des A/D Wandlers, Quelle https://gist.github.com/yoggy/7096133  
class MCP3208:
        def __init__(self, spi_channel=0):
                self.spi_channel = spi_channel
                self.conn = spidev.SpiDev(0, spi_channel)
                self.conn.max_speed_hz = 1000000 # 1MHz

        def __del__( self ):
                self.close

        def close(self):
                if self.conn != None:
                        self.conn.close
                        self.conn = None

        def bitstring(self, n):
                s = bin(n)[2:]
                return '0'*(8-len(s)) + s

        def read(self, adc_channel=0):
                # build command
                cmd  = 128 # start bit
                cmd +=  64 # single end / diff
                if adc_channel % 2 == 1:
                        cmd += 8
                if (adc_channel/2) % 2 == 1:
                        cmd += 16
                if (adc_channel/4) % 2 == 1:
                        cmd += 32

                # send & receive data
                reply_bytes = self.conn.xfer2([cmd, 0, 0, 0])

                reply_bitstring = ''.join(self.bitstring(n) for n in reply_bytes)
                # print reply_bitstring

                reply = reply_bitstring[5:19]
                return int(reply, 2)

# Funktion um die GPIO Pins auszuschalten
def gpiooff():
	GPIO.output(18, False)
	GPIO.output(16, False)

# ruft die Funktion beim Beenden des Skriptes auf
atexit.register(gpiooff)


if __name__ == '__main__':
        spi = MCP3208(0)
	
	# Variablen Initialisierung
        count = 0
        a0 = 0
        a1 = 0

        while True:
		# Counter zaehlt hoch und Werte 
		# werden aus dem A/D Wandler gelesen
                count += 1
                a0 += spi.read(0)
                a1 += spi.read(2)
		
		# 2 Hilfsvariablen um Temperatur 
		# konstanter zu halten
		cool_help = a0/10
		heat_help = a1/10
		
		# Variablen zur Berechnung der Temperatur,
		# und heat Variable in Float Zahl umwandeln
		cool = a0/10
		heat = (a1+.0001)/10000
		
		# Berechnung der Temperatur mit den 
		# Bit-Werten aus dem A/D Wandler
		tempcool = ((cool * 2.5043) / (4096 * 4.7)- 0.14993)*100
		tempheat = 3.606 * (heat * heat) + 128.58 * heat - 242.86
		
		# Wenn Counter hochgezaehlt ist,
		# ausdrucken der Temperaturen und
		# der entsprechenden Bitzahl
		if count == 10:
			round(tempcool,2)
			round(tempheat,2)
                        print "Kuehlung = %2f C, Bit = %2d, Heizung  = %2f C, Bit = %2d" % (tempcool, cool, tempheat, heat_help)
			
			# Abfragen um die Temperatur einzugrenzen,
			# GPIO Pins werden bei bestimmten Bitzahlen
			# an- oder ausgeschaltet

			# entspricht ca 160 Grad Celsius
			if heat_help >= 2898:
				GPIO.output(18, False)

			# entspricht ca 161 Grad Celsius
			if heat_help < 2905:
				GPIO.output(18, True)

			# entspricht ca 4 Grad Celsius
			if cool_help >= 1456:
				GPIO.output(16, True)

			# entspricht ca 3 Grad Celsius		
			if cool_help < 1385:
				GPIO.output(16, False)
			
			# Variablen wieder auf 0 setzen um
			# neue Werte auslesen zu koennen
			count = 0
                        a0 = 0
                        a1 = 0