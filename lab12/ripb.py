import random

class Router:
    def __init__(self, ip):
        self.ip = ip
        self.neighbors = set()
        self.routing_table = {ip: (ip, 0)}
    
    def add_neighbor(self, neighbor_ip):
        self.neighbors.add(neighbor_ip)
        self.routing_table[neighbor_ip] = (neighbor_ip, 1)
    
    def update_table(self, neighbor_ip, neighbor_table):
        updated = False
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

    def print_table(self, it):
        print(f"\nSimulation step {it} of router {self.ip} table:")
        print(f"{'[Source IP]':<15} {'[Destination IP]':<18} {'[Next Hop]':<15} {'[Metric]'}")
        for dest in sorted(self.routing_table.keys()):
            next_hop, metric = self.routing_table[dest]
            print(f"{self.ip:<15} {dest:<18} {next_hop:<15} {metric}")

class RIPNetwork:
    def __init__(self):
        self.routers = {}
    
    def create_random_network(self, num_routers=5):
        ips = [f"192.168.1.{i}" for i in random.sample(range(1, 255), num_routers)]
        for ip in ips:
            self.routers[ip] = Router(ip)
        for i in range(num_routers - 1):
            self.add_connection(ips[i], ips[i+1])
        for _ in range(num_routers // 2):
            ip1, ip2 = random.sample(ips, 2)
            self.add_connection(ip1, ip2)

    def add_connection(self, ip1, ip2):
        if ip1 != ip2:
            self.routers[ip1].add_neighbor(ip2)
            self.routers[ip2].add_neighbor(ip1)

    def simulate(self):
        print("START SIMULATION\n\n")
        for i in range(16):
            changed = False
            for r_ip, router in self.routers.items():
                for neighbor_ip in router.neighbors:
                    neighbor_table = self.routers[neighbor_ip].routing_table.copy()
                    if router.update_table(neighbor_ip, neighbor_table):
                        changed = True
            print(f"Iteration {i + 1} completed:\n")
            for j in sorted(self.routers.keys()):
                self.routers[j].print_table(i + 1)
            if not changed:
                print(f"\nRIP finished after {i + 1} iterations.")
                break

if __name__ == "__main__":
    network = RIPNetwork()
    network.create_random_network(4)
    network.simulate()