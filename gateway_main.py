from tkinter import *
from tkinter import ttk
from EndDevice import *
import queue
import time

from EndDeviceDialog import *
from GatewayInterface import *

root = Tk()

#list of addrs
device_count = 0
smpl_addr = list()
end_devices = dict()

# Failure modes to simulate
failures = { 'crc':'Crc Failure', 'timeout':'No Response'}

#gateway interface
gateway_queue = queue.Queue()
gateway = GatewayInterface("COM5", gateway_queue)

# State variables
failure = StringVar()
sentmsg = StringVar()
statusmsg = StringVar()
addrs = StringVar(value=smpl_addr)

# Called when the selection in the listbox changes
def show_end_device(*args):
    if isinstance(args[0], Event):
        #ui event
        idxs = lbox.curselection()
        if len(idxs)==1:
            idx = int(idxs[0])
            current_addr = smpl_addr[idx]
            dev = end_devices[current_addr]      
    else:
        current_addr = args[0]
        dev = end_devices[current_addr]

    statusmsg.set('Temp: {0:2.3f} RSSI: {1:3d}'.format(dev.temp/8.0, dev.rssi))
    sentmsg.set('')

def add_end_device(*args):
    global device_count

    if len(args) == 1:
        new_addr = args[0].addr
        new_device = EndDevice('Room' + str(device_count), new_addr)
    else:
        #this is really for debug only
        new_addr = device_count
        new_device = EndDevice('Room' + str(device_count), new_addr)
        dialog = EndDeviceDialog(root, new_device)
    
    lbox.insert(END, new_device.name)
    #if nothing selected then select latest
    idxs = lbox.curselection()
    if len(idxs) != 1:
        lbox.selection_set(END)
    #use the unique address for dict key
    end_devices[new_addr] = new_device
    #store address
    smpl_addr.append(new_addr)
    device_count += 1
    
def edit_end_device(*args):
    idxs = lbox.curselection()
    if len(idxs)==1:
        idx = int(idxs[0])
        addr = smpl_addr[idx]
        curr_device = end_devices[addr]
        dialog = EndDeviceDialog(root, curr_device)
        #delete old one..must be easier way
        lbox.delete(idx, idx)
        #insert new name
        lbox.insert(idx, curr_device.name)
        #
        lbox.selection_set(idx)

def Remove(*args):
    idxs = lbox.curselection()
    print(idxs)
    if len(idxs) == 1:
        idx = int(idxs[0])
        lbox.delete(idx, idx)
        #pop key from list then remove end device from dict
        del end_devices[smpl_addr.pop(idx)]
        statusmsg.set('')

#plot temp and dB
plot_x = 0
def plot(msg, dev):
    global plot_x
    x_step = 20

    #scale temps say -50 -> +50 deg -> 0 - 200
    temp_0 = 100 - int(100*(dev.temp/8.0)/50.0)
    temp_1 = 100 - int(100*(msg.air_temp/8.0)/50.0)

    temp_plot.create_line(plot_x, temp_0, plot_x + x_step, temp_1)
    dev.temp = msg.air_temp
    #in theory can go from -128 -> 127
    db_0 = 100 - int(100*dev.rssi/127.0)
    db_1 = 100 - int(100*msg.rssi/127.0)
    db_plot.create_line(plot_x, db_0, plot_x + x_step, db_1)
    dev.rssi = msg.rssi
    
    plot_x = plot_x + x_step
    if plot_x >= 200:
        plot_x = 0
        db_plot.delete('all')
        temp_plot.delete('all')

def ProcessMsg():
    """
        Handle all the messages currently in the queue (if any).
    """
    while gateway_queue.qsize():
        try:
            msg = gateway_queue.get(0)
            # Check contents of message and do what it says
            # As a test, we simply print it
            print(str(msg))

            if isinstance(msg, JoinMsg):
                add_end_device(msg)
            elif isinstance(msg, StatusMsg):
                try:
                    dev = end_devices[msg.addr]
                    plot(msg, dev)
                    #update status
                    idxs = lbox.curselection()
                    #if a device is selected, update
                    if len(idxs) == 1:
                        idx = int(idxs[0])
                        addr = smpl_addr[idx]
                        if addr == msg.addr:
                            show_end_device(msg.addr)

                except KeyError:
                    print("Unkown addr", msg.addr)                                
                
        except gateway_queue.Empty:
            pass    

    """
        Restart periodic UI timer
    """
    root.after(100, ProcessMsg)

def EndApplication():
    print("Exiting..")
    gateway.stop()
    root.destroy()
    
# Create and grid the outer content frame
c = ttk.Frame(root, padding=(5, 5, 12, 0))
c.grid(column=0, row=0, sticky=(N,W,E,S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0,weight=1)

#listbox
lbox = Listbox(c, height=5, selectmode=SINGLE)



sentlbl = ttk.Label(c, textvariable=sentmsg, anchor='center');
status = ttk.Label(c, textvariable=statusmsg, anchor=W);

send = ttk.Button(c, text='Add...', command=add_end_device, default='active')
remove = ttk.Button(c, text='Remove', command=Remove, default='active')
edit_btn = ttk.Button(c, text='Edit...', command=edit_end_device, default='active')

lbl = ttk.Label(c, text="Failure to Test:")
g1 = ttk.Radiobutton(c, text=failures['crc'], variable=failure, value='crc');
g2 = ttk.Radiobutton(c, text=failures['timeout'], variable=failure, value='timeout');


# listbox
lbox.grid(column=0, row=0, rowspan=6, sticky=(N,S,E,W))

#add/edit/remove buttons
send.grid(column=1, row=0, sticky=E)
remove.grid(column=1, row=1, sticky=E)
edit_btn.grid(column=1, row=2, sticky=E)

#radio buttons
lbl.grid(column=2, row=0, padx=10, pady=5)
g1.grid(column=2, row=1, sticky=W, padx=20)
g2.grid(column=2, row=2, sticky=W, padx=20)

#ploting canvas
db_title = ttk.Label(c, text="RSSI in dB")
db_title.grid(column=0, row=7)
db_plot = Canvas(c, bg="grey", height=200, relief="sunken", width=200)
db_plot.grid(column=0, row=8)

temp_title = ttk.Label(c, text="Temp in deg")
temp_title.grid(column=2, row=7)
temp_plot = Canvas(c, bg="grey", relief="sunken", height=200, width=200)
temp_plot.grid(column=2, row=8)


    
sentlbl.grid(column=1, row=5, columnspan=2, sticky=N, pady=5, padx=5)
status.grid(column=0, row=6, columnspan=2, sticky=(W,E))
c.grid_columnconfigure(0, weight=1)
c.grid_rowconfigure(5, weight=1)

# Set event bindings for when the selection in the listbox changes,
# when the user double clicks the list, and when they hit the Return key
lbox.bind('<<ListboxSelect>>', show_end_device)
lbox.bind('<Double-1>', edit_end_device)
root.bind('<Return>', edit_end_device)

#close function
root.protocol("WM_DELETE_WINDOW", EndApplication)

# Set the starting state of the interface, including selecting the
# default gift to send, and clearing the messages.  Select the first
# country in the list; because the <<ListboxSelect>> event is only
# generated when the user makes a change, we explicitly call showPopulation.
failure.set('timeout')
sentmsg.set('')
statusmsg.set('')
lbox.selection_set(0)

#set off periodic timer
ProcessMsg()

root.mainloop()
