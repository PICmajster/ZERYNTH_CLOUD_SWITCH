# WolkAbout_MySwitch
# Created at 2019-10-29 10:32:20.682272

import streams
from wolkabout.iot import iot
from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver

# Insert your WiFi credentials
network_SSID = "???????"
network_SECURITY = wifi.WIFI_WPA2  # wifi.WIFI_OPEN , wifi.WIFI_WEP, wifi.WIFI_WPA, wifi.WIFI_WPA2
network_password = "?????????"

# Insert the device credentials received from WolkAbout IoT Platform when creating the device
device_key = "?????????"
device_password = "??????????"
actuator_references = ["SW"]

pinMode(D23,OUTPUT)

publish_period_milliseconds = 1000
streams.serial()

# Enable debug printing by setting flag to True
iot.debug_mode = False


class MyActuator:
    def __init__(self, value):
        self.value = value


switch_simulator = MyActuator(False)

class ActuatorStatusProviderImpl(iot.ActuatorStatusProvider):
    def get_actuator_status(self, reference):
        if reference == "SW":
            return  iot.ACTUATOR_STATE_READY, switch_simulator.value
      

class ActuationHandlerImpl(iot.ActuationHandler):
    def handle_actuation(self, reference, value):
          if reference == "SW":
             switch_simulator.value = value


class ConfigurationSimulator:
    def __init__(self, value):
        self.value = value


# Connect to WiFi network
try:
    print("Initializing WiFi driver..")
    # This setup refers to spwf01sa wi-fi chip mounted on flip n click device slot A
    # For other wi-fi chips auto_init method is available, wifi_driver.auto_init()
    wifi_driver.auto_init()

    print("Establishing connection with WiFi network...")
    wifi.link(network_SSID, network_SECURITY, network_password)
    print("Done")
except Exception as e:
    print("Something went wrong while linking to WiFi network: ", e)

try:
    device = iot.Device(device_key, device_password, actuator_references)
except Exception as e:
    print("Something went wrong while creating the device: ", e)

try:
    wolk = iot.Wolk(
        device,
        host="api-demo.wolkabout.com",
        port=1883,
        actuation_handler=ActuationHandlerImpl(),
        actuator_status_provider=ActuatorStatusProviderImpl(),
        outbound_message_queue=iot.ZerynthOutboundMessageQueue(200),
        keep_alive_enabled=True,
    )
except Exception as e:
    print("Something went wrong while creating the Wolk instance: ", e)

try:
    print("Connecting to WolkAbout IoT Platform")
    wolk.connect()
    print("Done")
except Exception as e:
    print("Something went wrong while connecting to the platform: ", e)

# Initial state of actuators and configuration must be delivered to the platform
# in order to be able to change their values from the platform
wolk.publish_actuator_status("SW")

try:
    while True:
       
        switch = switch_simulator.value  # get switch value with cloud
      
        if switch == True:
            digitalWrite(D23, HIGH)  # turn the LED ON by setting the voltage HIGH
        else:
            digitalWrite(D23, LOW)   # turn the LED OFF by setting the voltage LOW
       
        print(
            "Publishing readings"
            + " Sw: "
            + str(switch)
            )

        sleep(publish_period_milliseconds)
except Exception as e:
    print("Something went wrong: ", e)
