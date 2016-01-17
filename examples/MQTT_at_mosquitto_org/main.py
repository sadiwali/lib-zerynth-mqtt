################################################################################
# mqtt test
#
# Created: 2015-10-15 21:37:25.886276
#
################################################################################

import streams
import mqtt
from wireless import wifi

# the wifi module needs a networking driver to be loaded
# in order to control the board hardware.
# FOR THIS EXAMPLE TO WORK, A NETWORK DRIVER MUST BE SELECTED BELOW

# uncomment the following line to use the CC3000 driver (Particle Core or CC3000 Wifi shields)
# from cc3000 import cc3000 as wifi_driver

# uncomment the following line to use the BCM43362 driver (Particle Photon)
# from bcm43362 import bcm43362 as wifi_driver

# init the wifi driver!
# The driver automatically registers itself to the wifi interface
# with the correct configuration for the selected board
wifi_driver.auto_init()


streams.serial()


# use the wifi interface to link to the Access Point
# change network name, security and password as needed
print("Establishing Link...")
try:
    # FOR THIS EXAMPLE TO WORK, "Network-Name" AND "Wifi-Password" MUST BE SET
    # TO MATCH YOUR ACTUAL NETWORK CONFIGURATION
    wifi.link("Network-Name",wifi.WIFI_WPA2,"Wifi-Password")
except Exception as e:
    print("ooops, something wrong while linking :(", e)
    while True:
        sleep(1000)

# define MQTT callbacks
def is_sample(data):
    if ('message' in data):
        return (data['message'].qos == 1 and data['message'].topic == "desktop/samples")
    return False

def print_sample(client,data):
    message = data['message']
    print("sample received: ", message.payload)

def print_other(client,data):
    message = data['message']
    print("topic: ", message.topic)
    print("payload received: ", message.payload)

def send_sample(obj):
    print("publishing: ", obj)
    client.publish("temp/random", str(obj))

def publish_to_self():
    client.publish("desktop/samples","hello! "+str(random(0,10)))


try:
    # set the mqqt id to "vipermqtt"
    client = mqtt.Client("vipermqtt",True)
    # and try to connect to "test.mosquitto.org"
    for retry in range(10):
        try:
            client.connect("test.mosquitto.org", 60)
            break
        except Exception as e:
            print("connecting...")
    print("connected.")
    # subscribe to channels
    client.subscribe([["desktop/samples",1]])
    client.subscribe([["desktop/others",2]])
    # configure callbacks for "PUBLISH" message
    client.on("PUBLISH",print_sample,is_sample)
    # start the mqtt loop
    client.loop(print_other)
    # Every 3 seconds, send a random number to "temp/random"
    # you can check temp/random changing here: http://test.mosquitto.org/gauge/

    while True:
        sleep(3000)
        x = random(0,50)
        send_sample(x)
        # when x ends with 0, publish a message to desktop/samples
        # it is echoed back
        if x%10==0:
            publish_to_self()
except Exception as e:
    print(e)