class Period(object):
    def __init__(self, on, off):
        self.on = on
        self.off = off
    def __str__(self):
        return(self.on+'-'+self.off)
    def set_period(self, time_str):
        times = time_str.split('-')
        self.on = times[0]
        self.off = times[1]

class ProfileDay(object):
    def __init__(self, name):
        self.name = name
        self.periods = (Period('00:00', '23:00'), Period('00:00', '23:00'), Period('00:00', '23:00'), Period('00:00', '23:00'), Period('00:00', '23:00'))
    
class EndDevice(object):
    def __init__(self, name, addr):
        self.rssi = 0
        self.temp = 0
        self.name = name
        self.addr = addr
        self.days = {'Monday':ProfileDay('Monday'), 'Tuesday':ProfileDay('Tuesday'), 'Wednesday':ProfileDay('Wednesday'), 'Thursday':ProfileDay('Thursday'), 'Friday':ProfileDay('Friday'), 'Saturday':ProfileDay('Saturday'), 'Sunday':ProfileDay('Sunday')}
    
