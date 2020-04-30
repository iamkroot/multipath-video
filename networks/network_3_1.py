from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink


class CustomRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(CustomRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd("sysctl net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl net.ipv4.ip_forward=0")
        super(CustomRouter, self).terminate()


class CustomTopo(Topo):
    def build(self):

        router = self.addNode("router", cls=CustomRouter)
        server = self.addHost("server")
        client = self.addHost("client")

        self.addLink(server, router, intfName="server-eth0", intfName2="router-eth0")
        self.addLink(client, router, intfName="client-eth0", intfName2="router-eth1")
        self.addLink(client, router, intfName="client-eth1", intfName2="router-eth2")
        self.addLink(client, router, intfName="client-eth2", intfName2="router-eth3")


def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    router, server, client = net.get("router", "server", "client")

    # set router IPs
    router.setIP("10.0.0.1/24", intf="router-eth0")

    router.setIP("11.0.0.1/24", intf="router-eth1")
    router.setIP("11.0.1.1/24", intf="router-eth2")
    router.setIP("11.0.2.1/24", intf="router-eth3")

    routing_cmds = [
        "ip route add {subnet} dev {dev} src {ip} table {rt_table}",
        "ip route add default via {router_ip} dev {dev} table {rt_table}",
        "ip rule add from {ip}/32 table {rt_table}",
        "ip rule add to {ip}/32 table {rt_table}",
    ]

    # assign IPs and routes to hosts
    for host, ip_prefix, num_links in ((server, "10", 1), (client, "11", 3)):
        for i in range(0, num_links):
            params = {
                "dev": f"{host.name}-eth{i}",  # eg: server-eth0
                "subnet": f"{ip_prefix}.0.{i}.0/24",  # eg: 10.0.0.0/24
                "router_ip": f"{ip_prefix}.0.{i}.1",  # eg: 10.0.0.1
                "ip": f"{ip_prefix}.0.{i}.2",  # eg: 10.0.0.2
                "rt_table": f"rt_{host.name}_eth{i}",  # eg: rt_server_eth0
            }
            host.setIP(f"{params['ip']}/24", intf=params["dev"])
            for cmd in routing_cmds:
                host.cmd(cmd.format(**params))

    # add default gateways
    server.cmd("route add default gw 10.0.0.1 server-eth0")
    client.cmd("route add default gw 11.0.0.1 client-eth0")

    # rate limit links
    server.cmd("tc qdisc add dev server-eth0 root netem rate 5000kbit")

    client.cmd("tc qdisc add dev client-eth0 root netem rate 1000kbit")
    client.cmd("tc qdisc add dev client-eth1 root netem rate 750kbit")
    client.cmd("tc qdisc add dev client-eth2 root netem rate 500kbit")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
