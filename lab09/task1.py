import psutil
import socket

interfaces = psutil.net_if_addrs()

for interface_name, addresses in interfaces.items():
    for addr in addresses:
        if addr.family == socket.AF_INET:
            print(f"IP-адрес: {addr.address}")
            print(f"Маска сети: {addr.netmask}")
            print("=" * 69)
