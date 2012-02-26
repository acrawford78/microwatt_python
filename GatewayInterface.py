from struct import *


class GatewayEvent(object):
    def Print(self):
        print("default")
    def parse_raw(self, buffer):
        pass
    def Response(self):
        return False
class StatusMsg(GatewayEvent):
    def __init__(self):
        self.addr = self.dev = self.req = self.air_temp = self.pipe_temp = self.valve_pos = self.rssi = self.lqi = self.hop_count = self.recv_crc = 0
    def __str__(self):
        return('StatusMsg(addr: {0:x} dev: {1:x} req: {2:x} air_temp: {3:f} pipe_temp: {4:f} valve_pos: {5:d} rssi: {6:f} lqi: {7:d} hop_count: {8:d} recv_crc: {9:x})'.format(self.addr, self.dev, self.req, self.air_temp/8, self.pipe_temp/8, self.valve_pos, self.rssi, self.lqi, self.hop_count, self.recv_crc))
    def parse_raw(self, buffer):
        self.addr, self.dev, self.req, self.air_temp, self.pipe_temp, self.valve_pos, self.rssi, self.lqi, self.hop_count, self.recv_crc = unpack_from('>IBBhhBbBBH', buffer, offset=2)
    def Response(self):
        if(self.req > 0):
            return True
        else:
            return False   
class  JoinMsg(GatewayEvent):
    def __init__(self):
        self.status = self.connect_id = self.dev_type = self.addr = self.rssi = self.lqi = self.hop_count = self.recv_crc = 0
    def __str__(self):
        return('JoinMsg(status: 0x{0:x}, connect_id: {1:d}, dev_type: {2:d}, addr: 0x{3:x}, rssi: {4:f}, lqi: {5:d}, hop_count: {6:d}, recv_crc: 0x{7:x},'.format(self.status, self.connect_id, self.dev_type, self.addr, self.rssi, self.lqi, self.hop_count, self.recv_crc)) 
    def parse_raw(self, buffer):
        self.status, self.connect_id, self.dev_type, self.addr, self.rssi, self.lqi, self.hop_count, self.recv_crc = unpack_from('>BBBIbBBH', buffer, offset=2)
    def Response(self):
        return True   
# msg_id -> object
msg_id_dict = {
    0x03 : StatusMsg,
    0x06 : JoinMsg,
    }

class GatewayInterface:
    def __init__(self, port, queue):
        import sys
        sys.path.append('.\pycrc-0.7.7')
        import threading        
        from crc_algorithms import Crc
        import serial

        self.xport_serial = serial.Serial(port, 115200, timeout=5.0)
        self.crc = Crc(width = 16, poly = 0x1021, reflect_in = True, xor_in = 0xffff, reflect_out = False, xor_out = 0x0000)
        self.reading = threading.Event()
        """
        We spawn a new thread for the worker.
        """
        self.queue = queue
        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.worker_thread)
        self.thread1.start()
        
    def stop(self):
        self.running = 0
        self.reading.wait(5.0)
        self.xport_serial.close()
    def get_msg(self, queue):
        self.reading.clear()
        raw_msg = bytearray()
        raw_msg.extend(self.xport_serial.read(1))
        if len(raw_msg) > 0:
            print("MSG RECV", raw_msg[0])
            try:
                msg = msg_id_dict[raw_msg[0]]()
            except KeyError:
                print("Unkown msg", raw_msg[0])
            else:
                #Success
                raw_msg.extend(self.xport_serial.read(1))
                raw_msg.extend(self.xport_serial.read(raw_msg[1]-2))
                #parse msg
                msg.parse_raw(raw_msg)
                #remove crc bytes for end of raw and then calc crc
                calc_crc = self.crc.bit_by_bit_fast_array(raw_msg[0:len(raw_msg) - 2])
                #response
                resp_msg = bytearray(2)
                resp_msg[0] = 0x80 | raw_msg[0]
                if(calc_crc == msg.recv_crc):
                    resp_msg[1] = 0xA5
                    queue.put(msg)
                else:
                    print("CRC fail")
                    resp_msg[1] = 0x00
                #send resp is expected
                if(msg.Response() == True):               
                    write_len = self.xport_serial.write(resp_msg)
                    print("RESP_MSG: len", len(resp_msg), write_len, resp_msg)
                self.reading.set()
                return True
            self.reading.set()
        return False
    
    def worker_thread(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        while self.running:
            if self.get_msg(self.queue) == False:
                print("Timeout waiting for read")
        """
        Clean up 
        """
        #self.gateway.stop()              
