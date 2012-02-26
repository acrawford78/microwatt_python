from tkinter import *
from tkinter import ttk
import tkSimpleDialog
class EndDeviceDialog(tkSimpleDialog.Dialog):

    def __init__(self, root, end_device):
        self.end_device = end_device
        super().__init__(root, title = 'End Device')
    def body(self, master):
  
        Label(master, text="Addr:").grid(row=0, column=0, sticky=W)
        Label(master, text=str(self.end_device.addr)).grid(row=0, column=1, sticky=W)    
        Label(master, text="Name:").grid(row=1, column=0, sticky=W)
        
        #name change
        self.e1 = Entry(master)
        self.e1.insert(0, self.end_device.name)
        self.e1.grid(row=1, column=1, sticky=W)

        #profile frame
        self.profile_frame = LabelFrame(master, text='Set Profile')
        self.profile_frame.grid(row=2, column=0, pady=5, columnspan=2, sticky=W)
        self.days = ttk.Combobox(self.profile_frame, state="readonly", values=('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))
        self.days.grid(row=0, column=1, columnspan=2, sticky=W)
        self.days.set('Monday')
        self.days.bind('<<ComboboxSelected>>',self.change_day)
        
        Label(self.profile_frame, text="Day:").grid(row=0, column=0)
        self.periods = list()
        self.change_day()
            
        return self.e1 # initial focus

    def apply(self):
        self.end_device.name = self.e1.get()
        #for day in self.end_device.days
        print("Name: ", self.e1.get())

    def change_day(self, *args):
        #if previous read periods
        if len(self.periods):
            last_day = self.end_device.days[self.prev_day]
            #save old settings to object
            for i, period in enumerate(self.periods):
                last_day.periods[i].set_period(period.get())
                
        day = self.end_device.days[self.days.get()]        
        print("change_day")
        self.periods = list()
        for period in day.periods:
            period_entry = Entry(self.profile_frame)
            period_entry.insert(0, str(period))
            self.periods.append(period_entry)
            row_num = len(self.periods)
            period_entry.grid(row=row_num, column=1)
            print("row"+ str(row_num))
            Label(self.profile_frame, text='Period {0:d}:'.format(row_num)).grid(row=row_num, column=0, sticky=W)

        #save the last selectet day for next time around
        self.prev_day = self.days.get()
