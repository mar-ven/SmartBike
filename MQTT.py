# MQTTprova
# Created at 2021-05-18 18:19:18.466864

# ExampleMQTT
# Created at 2019-05-16 09:37:59.069627

import streams
from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver
from mqtt import mqtt

s0 = streams.serial()

class MQTTpublisher:
    def __init__(self, topic):
        self.topic = str(topic)
        self.connect()
        sleep(1000)
        self.my_client = mqtt.Client("scheda",True)
        #self.my_client.set_will(topic, 'Disconnected!', 0, False)
        for retry in range(10):
            self.my_client.connect("marven.zapto.org", 1883)
        s0.write("Connected to broker\n")
        self.my_client.loop()
        
    def connect(self):
        try:
            wifi_driver.auto_init()
            sleep(3000)
            for retry in range(20):
                s0.write('Connecting... \n')
                try:
                    wifi.link('VodafoneTONINO', wifi.WIFI_WPA2, 'ciruzzo27')
                    s0.write('Connected to wifi \n')
                    break
                except IOError:
                    sleep(1000)
            sleep(1000)
        except IOError as e:
            s0.write('Exception:', e)
            s0.write('\n')
            sleep(10000)
            
    def publish(self, message):
        self.my_client.publish(self.topic , str(message))
    
    def subscribe(self, topic, function):
        self.my_client.subscribe([[topic , 0]])
        self.my_client.on(mqtt.PUBLISH, function)
        self.my_client.loop()
        
        