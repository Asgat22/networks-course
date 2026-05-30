import socket
import sys

def scan_ports(ip, start_port, end_port):
    print(f"Сканирование {ip} в диапазоне {start_port}-{end_port}...")
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            result = s.connect_ex((ip, port))
            if result != 0:
                print(f"Порт {port} свободен")


target_ip = sys.argv[1]
start = int(sys.argv[2])
end = int(sys.argv[3])
scan_ports(target_ip, start, end)