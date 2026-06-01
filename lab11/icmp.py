import socket
import struct
import time
import argparse

def calc_checksum(data):
    s = sum(data[i] << 8 | data[i+1] for i in range(0, len(data) - 1, 2))
    if len(data) % 2: s += data[-1] << 8
    s = (s >> 16) + (s & 0xffff)
    s += (s >> 16)
    return (~s) & 0xffff

def traceroute(target_host, max_hops=30, probes_per_hop=3):
    dest_ip = socket.gethostbyname(target_host)
    print(f"traceroute {target_host} [{dest_ip}]\n")
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.settimeout(1.0)
    for ttl in range(1, max_hops + 1):
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        rtts = []
        hop_ip = None
        target_reached = False
        for _ in range(probes_per_hop):
            header = struct.pack("!bbHHh", 8, 0, 0, 1, ttl)
            packet = struct.pack("!bbHHh", 8, 0, calc_checksum(header), 1, ttl)
            t_start = time.time()
            sock.sendto(packet, (dest_ip, 0))
            try:
                data, addr = sock.recvfrom(1024)
                rtts.append(f"{(time.time() - t_start) * 1000:.1f} ms")
                hop_ip = addr[0]
                ihl = (data[0] & 0x0F) * 4
                if data[ihl] == 0:
                    target_reached = True
            except socket.timeout:
                rtts.append("*")
        rtt_str = "  ".join(rtts)
        
        if hop_ip:
            try:
                node_name = socket.gethostbyaddr(hop_ip)[0]
            except socket.herror:
                node_name = hop_ip
            print(f"{ttl:<2} {rtt_str:<25} {node_name} [{hop_ip}]")
        else:
            print(f"{ttl:<2} {rtt_str:<25}")
        if target_reached:
            break
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", type=str)
    parser.add_argument("-TTL", type=int)
    parser.add_argument("-tries", type=int)
    args = parser.parse_args()
    host = args.host
    TTL = args.TTL
    tries = args.tries
    traceroute(host, TTL, tries)