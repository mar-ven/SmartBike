
# Progetto
# Created at 2021-05-18 17:04:55.069503
import streams
import threading
import gps
import lcd
import MQTT
import PROXIMITY
import pwm
import math
import ACCEL

s0 = streams.serial()
gps = gps.GPS(SERIAL2)
gps.setTimeZone(2)
lcd = lcd.LCD(0x27, 16, 2, I2C0)
lcd.setBacklight(True)
lcd.cursor_off()
lock = threading.Lock()
publisher = MQTT.MQTTpublisher('/com/iot/smartbike/gps')
trigger_pin = D23   
echo_pin = D22
led = D5 
photo = A1
pinMode(led, OUTPUT)
pinMode(photo, INPUT_ANALOG)
accel = ACCEL.ACCEL(I2C2)
emergencybtn = BTN0
pinMode(trigger_pin, OUTPUT)
pinMode(echo_pin, INPUT)
        
prox = PROXIMITY.HC_SR04(echo_pin, trigger_pin)
buzzerpin = D21.PWM
pinMode(BTN0, INPUT)
distance = 0

def onEmergency():
    global lock
    lock.acquire()
    dati = gps.standardData()
    dati = gps.convertNMEA(dati[0], dati[1] , dati[2], dati[3])
    publisher.publish('EMERGENCY ' + str(dati[0]) + " " + str(dati[1]))
    lock.release()
    
onPinRise(emergencybtn, onEmergency)

magnete=D13
pinMode(magnete,INPUT)


counter=0
check=True

def onMagnete():
    print("INTERRUPT")
    global counter
    global check
    if check:
        counter+=1 

onPinRise(magnete,onMagnete)

def zfill(num_of_zeros,string):
    if len(string) < num_of_zeros:
        for i in range(0, num_of_zeros - len(string)):
            string = "0" + string 
    return string

def spacefill(num_of_zeros,string):
    if len(string) < num_of_zeros:
        for i in range(0, num_of_zeros - len(string)):
            string = " " + string 
    return string

def aggiorna_velocità():
    global counter
    global check
    global lock
    global distance
    while True:
        check=False
        rpm=counter*12
        diametro = 0.4
        velocità=rpm*3.14159*diametro/60*3.6
        lock.acquire()
        lcd.setCursor(0, 1)
        temp = str(int(accel.getTemperature()))
        s0.write(temp + "\n")
        lcd.printString(spacefill(2, str(int(velocità * 3.6))) + " Km/h " + spacefill(2, temp) + " C")
        publisher.publish('SPEED ' + str(velocità))
        distance += (velocità/3.6)*5
        publisher.publish('DISTANCE ' + str(distance))
        lock.release()
        s0.write("Velocita': " + str(velocità) + "\n")
        counter=0
        check=True
        sleep(5000)

def aggiorna_schermo_e_luci():
    global lock
    while True:
        try:
            lock.acquire()
            lcd.setCursor(0, 0)
            (anno, mese, giorno, ora, minuto, secondo, tz) = gps.dateTime()
            lcd.printString(zfill(2,str(giorno))+"/"+zfill(2,str(mese))+"/"+zfill(4,str(anno))+ " " + zfill(2,str(ora))+":"+zfill(2,str(minuto)))
            lock.release()
        except Exception as e:
            sleep(100)
        value=analogRead(photo)
        if value>3800:
            digitalWrite(led,HIGH)
        else:
            digitalWrite(led,LOW)
        sleep(1000)

def aggiorna_pos():
    global lock
    global publisher
   # global distance
    try:
        lock.acquire()
        dati = gps.standardData()
        (last_lat, last_long) = gps.convertNMEA(dati[0], dati[1] , dati[2], dati[3])
        lock.release()
        while True:
            try:
                lock.acquire()
                dati = gps.standardData()
                dati = gps.convertNMEA(dati[0], dati[1] , dati[2], dati[3])
                lock.release()
                """lat1, lon1 = last_lat, last_long
                (lat2, lon2) = dati
                #formula di Haversine
                R = 6371e3; # metres
                φ1 = lat1 * math.pi/180; # φ, λ in radians
                φ2 = lat2 * math.pi/180;
                Δφ = (lat2-lat1) * math.pi/180;
                Δλ = (lon2-lon1) * math.pi/180;
                a = math.sin(Δφ/2) * math.sin(Δφ/2) +math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2) * math.sin(Δλ/2);
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
                d = R * c; # in metres
                distance += d"""
                s0.write("GPS : "+ str(dati)+ '\n')
                if len(dati) == 2:
                    lock.acquire()
                    publisher.publish(str(dati[0]) + " " + str(dati[1]))
                    lock.release()
            except Exception as e:
                sleep(100)
            sleep(500)
    except Exception as e:
        sleep(100)
        
def aggiorna_ostacolo():
    distance = prox.misura()
    s0.write('Distance=%.1f\n' % distance)
    while True:
        if (distance>7 and distance<=13):
            f=660
            pwm.write(buzzerpin,1000000//f,1000000//(f*2),MICROS)
            sleep(300)
            pwm.write(buzzerpin,0,0)
            sleep(250)
        if distance>13:
            f=440
            pwm.write(buzzerpin,1000000//f,1000000//(f*2),MICROS)
            sleep(300)
            pwm.write(buzzerpin,0,0)
            sleep(500)
        if distance<=7:
            f=880
            pwm.write(buzzerpin,1000000//f,1000000//(f*2),MICROS)
            sleep(300)
            pwm.write(buzzerpin,0,0)
            sleep(20)
        else:
            sleep(1000)
        distance = prox.misura()
        s0.write('Distance=%.1f\n' % distance)


t = thread(aggiorna_pos)
t.start()
t1 = thread(aggiorna_schermo_e_luci)
t1.start()
t2 = thread(aggiorna_ostacolo)
t2.start()
t3=thread(aggiorna_velocità) 
t3.start()
