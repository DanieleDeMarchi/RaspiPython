import time
import os
import psutil

class CpuMemoryLoad:
    def __init__(self):
        self.coreCount = psutil.cpu_count()
        self.cpus_percent = psutil.cpu_percent(percpu=True)
        self.media_cpu = psutil.cpu_percent(percpu=False)

    def getCoreLoad(self):
        return psutil.cpu_percent(percpu=True)
    
    def getCpuLoad(self):
        return psutil.cpu_percent(percpu=False)

    def getCpuFreq(self):
        return psutil.cpu_freq().current
    
    def getLiveCpuData(self):
        return {"CpuLoad": self.getCpuLoad()}

    def getDetailCpuData(self):
        data = {"core_count": self.coreCount,
                "Frequency": self.getCpuFreq()}

        core_load =  self.getCoreLoad()
        for core in range(self.coreCount):
            data["core_{}".format(core)] = core_load[core]

        return data

    def getMemoryData(self):
        ramData = psutil.virtual_memory()
        swapData = psutil.swap_memory()
        return {
            "total": int(ramData.total/1024**2),
            "available": int(ramData.available/1024**2),
            "swap_total": int(swapData.total/1024**2),
            "swap_used": int(swapData.used/1024**2)
        }   


def main():
    os.system("cls")
    cpuMemoryStats = CpuMemoryLoad()
    while True:
        print(cpuMemoryStats.getLiveCpuData())
        print(cpuMemoryStats.getDetailCpuData())
        print(cpuMemoryStats.getMemoryData())

        time.sleep(1)
        os.system("cls")


if __name__ == "__main__":
    main()