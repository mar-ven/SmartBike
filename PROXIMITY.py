# PROXIMITY
# Created at 2021-05-20 14:12:18.739293

class HC_SR04:

    def __init__(self, echo, trigger):
        self.echo_pin = echo
        self.trigger_pin = trigger
        
    def misura(self):
        # Trasmettiamo un segnale di 10 microsecondi per misurare la distanza
        digitalWrite(self.trigger_pin, HIGH)
        sleep(10, MICROS)
        digitalWrite(self.trigger_pin, LOW)
        
        distance = 0
        while(digitalRead(self.echo_pin) == LOW):
            sleep(10, MICROS)
            distance += 1
            if distance > 2500:
                return -1
                
        distance = 0
        while(digitalRead(self.echo_pin) == HIGH):
            sleep(10, MICROS)
            distance += 1
            if distance >= 3800:
                break 
        
        return distance / 2.46
        
    
    