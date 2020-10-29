import psutil
    
"""[summary]

    Classe per misurazione quantità di carica rimanente

"""
class Battery:
    def getStatus():
        batt = {}
        if not hasattr(psutil, "sensors_battery"):
            batt["status"] = "platform not supported"
            return bat

        battery = psutil.sensors_battery()
        if battery is None:
            batt["status"] = "no battery is installed"
            return batt

        batt["charge"] = round(battery.percent, 2)
        if battery.power_plugged:
            batt["status"] = "charging" if battery.percent < 100 else "fully charged"
        else:
            batt["min_left"] = int(battery.secsleft /60)
            batt["status"] = "discharging"
        
        return batt

    def secs2hours(secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)


    def getStatusString():
        batt = "Batteria: " 
        if not hasattr(psutil, "sensors_battery"):
            batt += "platform not supported"
            return bat

        battery = psutil.sensors_battery()
        if battery is None:
            batt += "Nessuna batteria presente" + "\n"
            return batt

        carica = round(battery.percent, 2)
        batt += str(carica) + "%\n"
        if battery.power_plugged:
            batt += "In carica" if battery.percent < 100 else "Carica completa"
        else:
            carica_rimanente = "autonomia: " + Battery.secs2hours(battery.secsleft)
            batt += carica_rimanente
        
        return batt



def main():
    print(Battery.getStatus())
    print(Battery.getStatusString())

if __name__ == '__main__':
    main()