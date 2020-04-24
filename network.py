from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink


class CustomRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( CustomRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( CustomRouter, self ).terminate()

class CustomTopo(Topo):

    def build(self):

        router = self.addNode('r0',cls = CustomRouter,ip = '192.168.1.1/24')

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        self.addLink(s1,router,intfName2='r0-eth1',params2={'ip':'192.168.1.1/24'})
        self.addLink(s2,router,intfName2='r0-eth2',params2={'ip':'172.16.1.1/24'})

        h1 = self.addHost('h1',ip='192.168.1.100',defaultRoute='via 192.168.1.1')
        h2 = self.addHost('h2',ip='172.16.1.100',defaultRoute='via 172.16.1.1')

        self.addLink(h1,s1,cls=TCLink,delay = '10ms',bw = 15)
        self.addLink(h1,s1,cls=TCLink,delay = '25ms',bw = 25)
        self.addLink(h2,s2,cls=TCLink,delay = '15ms',bw = 12)
        self.addLink(h2,s2,cls=TCLink,delay = '30ms',bw = 27)

        # h1.setIP('192.168.1.100', intf='h1-eth0')
        # h1.setIP('192.168.1.101', intf='h1-eth1')

        # h2.setIP('172.16.1.100', intf='h2-eth0')
        # h2.setIP('172.16.1.101', intf='h2-eth1')



def run():
    "Test linux router"
    topo = CustomTopo()
    net = Mininet( topo=topo, link=TCLink )  # controller is used by s1-s3
    net.start()
    h1, h2 = net.get( 'h1', 'h2' )
    h1.setIP('192.168.1.100', intf='h1-eth0')
    h1.setIP('192.168.1.101', intf='h1-eth1')

    h2.setIP('172.16.1.100', intf='h2-eth0')
    h2.setIP('172.16.1.101', intf='h2-eth1')
    info( '*** Routing Table on Router:\n' )
    info( net[ 'r0' ].cmd( 'route' ) )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()