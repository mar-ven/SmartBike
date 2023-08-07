# MircoGPS
# Created at 2021-05-08 15:32:30.288979
# GPS driver for Zerynth
# Created at 2021-05-08 10:26:11.500666
import streams
import datetime

s0 = streams.serial()
s0.write("inizio programma \n")

class GPS:
    def __init__(self, serialname):
        self.ser = streams.serial(serialname, baud = 9600, rxsize = 16 , txsize = 16)

    def getDataRaw(self, format):
        finished = False
        data = ""
        while not finished:
            length = self.ser.available()
            while length <= 0:
                sleep(100)
                length = self.ser.available()
            data = self.ser.read(length)
            if data.split(",")[0] == format:
                finished = True
        return data.split(",")
          
    def getDataGPRMC(self):
        elements = self.getDataRaw("$GPRMC")
        if len(elements) > 0:
            time = elements[1]
            status = elements[2]
            latitude = elements[3]
            latitudeHemisphere = elements[4]
            longitude = elements[5]
            longitudeMeridian = elements[6]
            speedKnots = elements[7]
            trackAngle = elements[8]
            date = elements[9]
            magneticVaration = elements[10]
            magneticVarationOrientation = elements[11]
            return (time, status, latitude, latitudeHemisphere, longitude, longitudeMeridian, speedKnots, trackAngle, date, magneticVaration, magneticVarationOrientation)
        else:
            return ()
    
    def time(self):
        tuple = self.getDataGPRMC()
        if len(tuple) > 0:
            string = str(tuple[0])
        return (int(string[0]+""+string[1]), int(string[2]+""+string[3]), int(string[4]+""+string[5]))
      
    def status(self):
        return self.getDataGPRMC()[1]
    
    def latitude(self):
        return self.getDataGPRMC()[2]
    
    def latitudeHemisphere(self):
        return self.getDataGPRMC()[3]
        
    def longitude(self):
        return self.getDataGPRMC()[4]
    
    def longitudeMeridian(self):
        return self.getDataGPRMC()[5]
    
    def speedKnots(self):
        return self.getDataGPRMC()[6]
    
    def trackAngle(self):
        return self.getDataGPRMC()[7]
    
    def date(self):
        tuple = self.getDataGPRMC()
        if len(tuple) > 0:
            string = str(tuple[8])
        return (int(string[0]+""+string[1]), int(string[2]+""+string[3]), int("20" + str(string[4]+""+string[5])))
        
    
    def magneticVaration(self):
        return self.getDataGPRMC()[9]
    
    def magneticVarationOrientation(self):
        return self.getDataGPRMC()[10]
    
    def standardData(self):
        result = self.getDataGPRMC()
        return (result[2], result[3], result[4], result[5])

    def convertNMEA(self, lat, latHem, long, longMer):
        if lat != "" and latHem != "" and long != "" and longMer != "":
            ddlat = int(float(lat)) // 100
            finalLat = ddlat + ((float(lat) % 100) / 60) * ((-1) if latHem == "S" else 1)
            ddlong = int(float(long)) // 100
            finalLong = ddlong + ((float(long) % 100) / 60) * ((-1) if longMer == "W" else 1)
            return (finalLat, finalLong)
        else:
            return ("","")
    
    def convertHour(ora):
        sora = str(ora)
        sora1 = (sora[0]+sora[1] + ':'+ sora[2]+sora[3] + ':'+sora[4]+sora[5] )
        return(sora1)
    
    def convertDate(data):
        sdata= str(data)
        sdata1 = (sdata[0]+sdata[1] + '/'+ sdata[2]+sdata[3] + '/'+sdata[4]+sdata[5] )
        return(sdata1)
        
    def setTimeZone(self, offset):
        self.timeZone = datetime.timezone(datetime.timedelta(hours = offset))
        
    def dateTime(self):
        data = self.date()
        hour = self.time()
        time = datetime.datetime(data[2], data[1], data[0], hour[0], hour[1], hour[2], datetime.timezone.utc)
        return time.astimezone(self.timeZone).tuple()
