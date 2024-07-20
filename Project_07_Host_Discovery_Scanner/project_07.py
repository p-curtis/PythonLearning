import ipaddress # Amazing article: https://docs.python.org/3/howto/ipaddress.html
import subprocess # Another amazing article: https://realpython.com/python-subprocess/
import colorama
from colorama import Fore, Style
from datetime import datetime

def network_selection(choice_selection):
    while True:
        network_input = input("Type in the network you want to scan including the '/' for the CIDR range. (Example: 192.168.1.0/24): ")
        # Assigns validated string to the variable.
        network = ip_validation(choice_selection, network_input)
        if network:
            while True:
                confirmation_check = input(f"You are about to perform a scan on {Fore.YELLOW}{network}{Style.RESET_ALL}\nAre you sure this is what you want to do ({Fore.GREEN}y{Style.RESET_ALL}/{Fore.RED}n{Style.RESET_ALL})? ")
                if confirmation_check == 'y':
                    return(network)
                elif confirmation_check == 'n':
                    break
                else:
                    print(f"Your input was: {Fore.YELLOW}{confirmation_check}{Style.RESET_ALL}. It needs to be {Fore.YELLOW}y{Style.RESET_ALL} or {Fore.YELLOW}n{Style.RESET_ALL}.\n")

def host_selection(choice_selection):
    while True:
        host_input = input("Type in the host IP you want to scan. (Example: 192.168.1.1): ")
        # Assigns validated string to the variable.
        host = ip_validation(choice_selection, host_input)
        if host:
            while True:
                confirmation_check = input(f"You are about to perform a scan on {Fore.YELLOW}{host}{Style.RESET_ALL}\nAre you sure this is what you want to do ({Fore.GREEN}y{Style.RESET_ALL}/{Fore.RED}n{Style.RESET_ALL})? ")
                if confirmation_check == 'y':
                    return(host)
                elif confirmation_check == 'n':
                    break
                else:
                    print(f"Your input was: {Fore.YELLOW}{confirmation_check}{Style.RESET_ALL}. It needs to be {Fore.YELLOW}y{Style.RESET_ALL} or {Fore.YELLOW}n{Style.RESET_ALL}.\n")

def is_rfc1918_network(network):
    rfc1918_networks = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16')
    ]
    # Check that "network" is a subnet of one of the "network ranges" within the "rfc1918_networks" list.
    return any(network.subnet_of(network_range) for network_range in rfc1918_networks)

def is_rfc1918_host(host):
    rfc1918_networks = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16')
    ]
    # Check that "host" is in one of the "network ranges" within the "rfc1918_networks" list.
    return any(host in network_range for network_range in rfc1918_networks)

# args was used because I wanted to dynamically send my variables (host_ or network_selection) to this single validation function.
def ip_validation(choice_selection, *args):
    # Choice 0 is a "network" scan.
    if choice_selection == '0':
        network_input = args[0]
        try:
            network = ipaddress.IPv4Network(network_input)
            if is_rfc1918_network(network):
                return(network)
            else:
                print(f"Your network ({Fore.YELLOW}{network}{Style.RESET_ALL}) is {Fore.RED}not{Style.RESET_ALL} within an RFC1918 range.\n")
        except Exception as error:
            print(f"\nYour input was {Fore.RED}bad{Style.RESET_ALL}. Here's the error:\n{error}\n")
    
    # Choice 1 is a singular "Host" scan.
    elif choice_selection == '1':
        host_input = args[0]
        try:
            host = ipaddress.IPv4Address(host_input)
            if is_rfc1918_host(host):
                return(host)
            else:
                print(f"Your host ({Fore.YELLOW}{host}{Style.RESET_ALL}) is {Fore.RED}not{Style.RESET_ALL} within an RFC1918 range.\n")
        except Exception as error:
            print(f"\nYour input was {Fore.RED}bad{Style.RESET_ALL}. Here's the error:\n{error}\n")

def ping_host(choice_selection, *args):
    date = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"{date}_ping_results.txt"
    
    # Choice 0 is a "network" scan.
    if choice_selection == "0":
        network_ping = args[0]
        with open(f"{filename}", "a") as file:
            for network_host in network_ping:
                ping = subprocess.run(["ping", "-c", "1", str(network_host)])
                if ping.returncode == 0:
                    file.write(f"Status: 1\t{network_host}\n")
                if ping.returncode == 1:
                    # write this line to the file
                    file.write(f"Status: 0\t{network_host}\n")
        print("Deciphering Results: 0=Inactive, 1=Active")
    # Choice 1 is a singular "Host" scan.
    if choice_selection == "1":
        ip = args[0]
        # Runs one ping against the specified host
        ping = subprocess.run(["ping", "-c", "1", str(ip)])
        print(f"{ping}\n")
        if ping.returncode == 0:
            print(f"{Fore.GREEN}Ping Successful{Style.RESET_ALL}. Host {Fore.YELLOW}{ip}{Style.RESET_ALL} is an active node.")
        if ping.returncode == 1:
            print(f"{Fore.RED}Ping Unsuccessful{Style.RESET_ALL}. Host {Fore.YELLOW}{ip}{Style.RESET_ALL} does not appear to be an active node.")
    """Temp Note
    Bad Data:
    PING 192.168.23.45 (192.168.23.45) 56(84) bytes of data.

    --- 192.168.23.45 ping statistics ---
    1 packets transmitted, 0 received, 100% packet loss, time 0ms

    CompletedProcess(args=['ping', '-c', '1', '192.168.23.45'], returncode=1)

    Good Data:
    PING 192.168.50.1 (192.168.50.1) 56(84) bytes of data.
    64 bytes from 192.168.50.1: icmp_seq=1 ttl=64 time=4.50 ms

    --- 192.168.50.1 ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 4.502/4.502/4.502/0.000 ms
    CompletedProcess(args=['ping', '-c', '1', '192.168.50.1'], returncode=0)"""


print(f"\nWelcome to the '{Fore.CYAN}Boring Internal Host Scanner{Style.RESET_ALL}'.\nYou can scan anything you want... so long as it's RFC1918 compatible and IPv4.\n")
print("*Please Note: Only Network Scans are written to disk.\n")
def main():
    while True:
        choice_selection = input(f"Please determine if you want to scan a network range ({Fore.YELLOW}0{Style.RESET_ALL}) or a singular host ({Fore.YELLOW}1{Style.RESET_ALL}): ")
        if choice_selection == '0':
            network_ping = network_selection(choice_selection)
            # Place holder, need to enumerate through individual objects to pass along to ping_host.
            ping_host(choice_selection, network_ping)
            break
        elif choice_selection == '1':
            ip = host_selection(choice_selection)
            ping_host(choice_selection, ip)
            break
        else:
            print(f"\nYour input was {Fore.RED}bad{Style.RESET_ALL}. Valid Inputs are ({Fore.YELLOW}0{Style.RESET_ALL}) or ({Fore.YELLOW}1{Style.RESET_ALL})")

main()