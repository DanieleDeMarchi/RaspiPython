import ntplib
from datetime import datetime, timezone, timedelta
import time


class NtpSyncTime:
    def __init__(self, ntpServer="pool.ntp.org"):
        self.ntpServer = ntpServer
        self.ntpClient = ntplib.NTPClient()
        self.offset = 0
        self.syncTime()

    def syncTime(self):
        try:
            response = self.ntpClient.request(self.ntpServer, version=3)
            self.offset = response.offset
            return response.offset
        except:
            return self.offset

    @staticmethod
    def getPcTime():
        diff = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
        timestampPc = diff.days * 24 * 60 * 60 + diff.seconds + diff.microseconds * (10 ** (-6))
        return timestampPc

    def getInfluxTimestamp(self, risoluzione="s"):
        timestampSincronizzato = self.getPcTime() + self.offset
        if risoluzione == "s":
            return int(timestampSincronizzato)
        elif risoluzione == "ms":
            return int(timestampSincronizzato * 1000)
        elif risoluzione == "us":
            return int(timestampSincronizzato * 10 ** (6))
        return None

    def getUnixTimestamp(self):
        return self.getPcTime() + self.offset

    def getOffset(self):
        return self.offset

    def getIsoTimestamp(self):
        return datetime.fromtimestamp(self.getUnixTimestamp(), tz=timezone.utc).isoformat()
