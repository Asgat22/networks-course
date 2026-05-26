import random
import socket
import threading
import time

class ThreadedRouter:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.neighbors = {}
        self.routing_table = {ip: (ip, 0)}
        self.lock = threading.Lock()
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', port))
        self.sock.settimeout(0.5)

    def add_neighbor(self, n_ip, n_port):
        with self.lock:
            self.neighbors[n_ip] = n_port
            self.routing_table[n_ip] = (n_ip, 1)

    def update_table(self, neighbor_ip, neighbor_table):
        updated = False
        with self.lock:
            for dest_ip, (_, neighbor_metric) in neighbor_table.items():
                if dest_ip == self.ip:
                    continue
                new_metric = neighbor_metric + 1
                if new_metric >= 16:
                    continue
                if dest_ip not in self.routing_table or new_metric < self.routing_table[dest_ip][1]:
                    self.routing_table[dest_ip] = (neighbor_ip, new_metric)
                    updated = True
        return updated

    def listen_for_updates(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(2048)
                text = data.decode('utf-8')
                parts = text.split(' | ')
                sender_ip = parts[0]
                neighbor_table = {}
                if parts[1]:
                    for item in parts[1].split(','):
                        d_ip, metric = item.split(':')
                        neighbor_table[d_ip] = (None, int(metric))
                self.update_table(sender_ip, neighbor_table)
            except socket.timeout:
                continue
            except Exception:
                break

    def send_table_to_neighbors(self):
        with self.lock:
            routes_str = ",".join([f"{k}:{v[1]}" for k, v in self.routing_table.items()])
            packet = f"{self.ip} | {routes_str}".encode('utf-8')
            for n_port in self.neighbors.values():
                try:
                    self.sock.sendto(packet, ('127.0.0.1', n_port))
                except Exception:
                    pass

    def print_table(self):
        with self.lock:
            print(f"\nState of router {self.ip} table (Port: {self.port}):")
            print(f"{'[Source IP]':<15} {'[Destination IP]':<18} {'[Next Hop]':<15} {'[Metric]'}")
            sorted_routes = sorted(self.routing_table.items(), key=lambda x: x[1][1])
            for dest, (next_hop, metric) in sorted_routes:
                print(f"{self.ip:<15} {dest:<18} {next_hop:<15} {metric}")


class ThreadedRIPNetwork:
    def __init__(self):
        self.routers = {}
        self.base_port = 6000
    
    def create_random_network(self, num_routers=4):
        ips = [f"192.168.1.{i}" for i in random.sample(range(1, 255), num_routers)]
        for i, ip in enumerate(ips):
            self.routers[ip] = ThreadedRouter(ip, self.base_port + i)
        for i in range(num_routers - 1):
            self.add_connection(ips[i], ips[i+1])
        if num_routers > 3:
            ip1, ip2 = random.sample(ips, 2)
            self.add_connection(ip1, ip2)

    def add_connection(self, ip1, ip2):
        if ip1 != ip2:
            r1, r2 = self.routers[ip1], self.routers[ip2]
            r1.add_neighbor(ip2, r2.port)
            r2.add_neighbor(ip1, r1.port)

    def simulate(self, run_time=8):
        print(f"Инициализация {len(self.routers)} роутеров")
        for router in self.routers.values():
            threading.Thread(target=router.listen_for_updates, daemon=True).start()
        start_time = time.time()
        step = 1
        while time.time() - start_time < run_time:
            for router in self.routers.values():
                router.send_table_to_neighbors() 
            time.sleep(2)
            print(f"прошло {step * 2} сек.")
            for ip in sorted(self.routers.keys()):
                self.routers[ip].print_table()
            step += 1
        print("Симуляция завершена")
        for router in self.routers.values():
            router.running = False
            router.sock.close()

if __name__ == "__main__":
    network = ThreadedRIPNetwork()
    network.create_random_network(4)
    network.simulate(run_time=6)