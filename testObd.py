import obd
from obd import OBDStatus


obd.logger.setLevel(obd.logging.DEBUG)

ports = obd.scan_serial()
print(ports)

connection = obd.OBD("COM3") # auto-connects to USB or RF port

print (connection.status())

#cmd = obd.commands.SPEED # select an OBD command (sensor)

#response = connection.query(cmd) # send the command, and parse the response

#print(response.value) # returns unit-bearing values thanks to Pint
#print(response.value.to("mph")) # user-friendly unit conversions