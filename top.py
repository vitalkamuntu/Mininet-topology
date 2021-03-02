#!/usr/bin/python

"""                      h21 
                          |                                                   eve
                          |                                                    |
               ids1---   s2----------r1------------------------r2--------------r3---bob
                          |          |                         |
                         h22   ids2--s1---h12                  |
                                     |               ids3---  s3---mail
                                    h11                        |
                                                               web
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSController
from mininet.util import irange,dumpNodeConnections

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):


    def build( self, **_opts ):
	#Creation des hots des reseaux avec leurs @IP et passerelle: Departement RH

        h11 = self.addHost( 'h11', ip='192.168.6.3/29',
                           defaultRoute='via 192.168.6.1' )
        h12 = self.addHost( 'h12', ip='192.168.6.4/29',
                           defaultRoute='via 192.168.6.1' )
        ids2 = self.addHost( 'ids2', ip='192.168.6.2/29',
                           defaultRoute='via 192.168.6.1' )

        #Creation des hots des reseaux avec leurs @IP et passerelle: "Batiment RD" 
                 
        h21 = self.addHost( 'h21', ip='192.168.7.2/29',
                           defaultRoute='via 192.168.7.1' )
        h22 = self.addHost( 'h22', ip='192.168.7.4/29',
                           defaultRoute='via 192.168.7.1' )
        ids1 = self.addHost( 'ids1', ip='192.168.7.3/29',
                           defaultRoute='via 192.168.7.1' )                    
                           
      #Creation des hots des reseaux avec leurs @IP et passerelle:  "Zone des serveurs"  
                 
        web = self.addHost( 'web', ip='192.168.4.3/29',
                           defaultRoute='via 192.168.4.1' )
        mail = self.addHost( 'mail', ip='192.168.4.4/29',
                           defaultRoute='via 192.168.4.1' ) 
        ids3 = self.addHost( 'ids3', ip='192.168.4.2/29',
                           defaultRoute='via 192.168.4.1' ) 
                     
      #"Assignation @Ip au hotes externes bob et eve sur reseau public"

        bob = self.addHost('bob', ip='192.168.1.2/29', defaultRoute='via 192.168.1.1')
        eve = self.addHost('eve', ip='192.168.2.2/29', defaultRoute='via 192.168.2.1')

      #"Affectation d'addresse au interface de chaque routeur et dans son reseau"

        r1defaultIP = '192.168.5.1/29'   # set eth1 addr as default addr
        r1_eth2IP = '192.168.7.1/29'     # IP address for r1-eth2
        r1_eth3IP = '192.168.6.1/29'     # IP address for r1-eth3
       	r1_eth1IP = '192.168.5.1/29'     # IP address for r1-eth1


        r2_eth1IP = '192.168.3.1/29'  # IP address for r2-eth1
        r2_eth2IP = '192.168.5.2/29'  # IP address for r2-eth2
        r2_eth3IP = '192.168.4.1/29'  # IP address for r2-eth1


        r3_eth1IP = '192.168.3.2/29'  # IP address for r3-eth1
        r3_eth2IP = '192.168.2.1/29'  # IP address for r3-eth2
        r3_eth3IP = '192.168.1.1/29'  # IP address for r3-eth3



        


       
     #"Activation du node  sur les switch" 
       
        r1 = self.addNode( 'r1', cls=LinuxRouter, ip=r1defaultIP ) 
        r2 = self.addNode( 'r2', cls=LinuxRouter, ip=r2_eth2IP )
        r3=  self.addNode( 'r3', cls=LinuxRouter, ip=r3_eth1IP )

     #"Activation de la OpenFlow sur les switch avec ajout de lien et ID"

        s1 = self.addSwitch('s1', dpid='0000000000000001', protocols='OpenFlow13',)
        s2 = self.addSwitch('s2', dpid='0000000000000002', protocols='OpenFlow13',)
        s3 = self.addSwitch('s3', dpid='0000000000000003', protocols='OpenFlow13',)
        
       
     #"Liaison des hots a leur switch respectif" 

       
        self.addLink( h11, s1)
        self.addLink( h12, s1)
        self.addLink( ids2, s1) 
        self.addLink( h21, s2)
        self.addLink( h22, s2)
        self.addLink( ids1, s2)
        self.addLink( web, s3)
        self.addLink( mail, s3)
        self.addLink( ids3, s3)
        self.addLink( r1, r2, intfName1='r1-eth1', params1={ 'ip' : r1defaultIP }, intfName2='r2-eth2', params2={ 'ip' : r2_eth2IP } )
        self.addLink( s1, r1, intfName2='r1-eth3', params2={ 'ip' : r1_eth3IP } )
        self.addLink( s2, r1, intfName2='r1-eth2', params2={ 'ip' : r1_eth2IP } )
        self.addLink( s3, r2, intfName2='r2-eth3', params2={ 'ip' : r2_eth3IP } )

#liaison r3 bob et eve

        self.addLink( r2, r3, intfName1='r2-eth1', params1={ 'ip' : r2_eth1IP }, intfName2='r3-eth1', params2={ 'ip' : r3_eth1IP } )
        


# config pour les liaision entre le cloud bob et eve

        self.addLink( bob, r3, intfName2='r3-eth3', params2={'ip' : r3_eth3IP } )
        self.addLink( eve, r3, intfName2='r3-eth2', params2={'ip' : r3_eth2IP } )
                                


def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo, controller = OVSController )  # controller is used by s1-s3
    net.start()
    
#"Routage des hots du switch S1 du reseau 2.0"



    net['r1'].cmd('ip route add 192.168.5.0/29 via 192.168.5.1 dev r1-eth1')	
    net['r1'].cmd('ip route add 192.168.6.0/29 via 192.168.6.1 dev r1-eth3')
    net['r1'].cmd('ip route add 192.168.7.0/29 via 192.168.7.1 dev r1-eth2')
    net['r1'].cmd('ip route add 192.168.3.0/29 via 192.168.5.2 dev r1-eth1')
    net['r1'].cmd('ip route add 192.168.4.0/29 via 192.168.5.2 dev r1-eth1')
    net['r1'].cmd('ip route add 192.168.2.0/29 via 192.168.5.2 dev r1-eth1')
    net['r1'].cmd('ip route add 192.168.1.0/29 via 192.168.5.2 dev r1-eth1')


    net['r2'].cmd('ip route add 192.168.7.0/29 via 192.168.5.1 dev r2-eth2')
    net['r2'].cmd('ip route add 192.168.6.0/29 via 192.168.5.1 dev r2-eth2')
    net['r2'].cmd('ip route add 192.168.1.0/29 via 192.168.3.2 dev r2-eth1')
    net['r2'].cmd('ip route add 192.168.2.0/29 via 192.168.3.2 dev r2-eth1')

    net['r2'].cmd('ip route add 192.168.3.0/29 via 192.168.3.1 dev r2-eth1')
    net['r2'].cmd('ip route add 192.168.4.0/29 via 192.168.4.1 dev r2-eth3')
    net['r2'].cmd('ip route add 192.168.5.0/29 via 192.168.5.2 dev r2-eth2')


# routage bob et eve

#ajout des reseaux de bob et eve au routeur1
 

#ajout des reseaux de bob et eve au routeur2
  

#ajout des reseaux au routeur3

    net['r3'].cmd('ip route add 192.168.2.0/29 via 192.168.2.1 dev r3-eth2')
    net['r3'].cmd('ip route add 192.168.1.0/29 via 192.168.1.1 dev r3-eth3')
    net['r3'].cmd('ip route add 192.168.3.0/29 via 192.168.3.2 dev r3-eth1')
    net['r3'].cmd('ip route add 192.168.5.0/29 via 192.168.3.1 dev r3-eth1')
    net['r3'].cmd('ip route add 192.168.4.0/29 via 192.168.3.1 dev r3-eth1')
    net['r3'].cmd('ip route add 192.168.6.0/29 via 192.168.3.1 dev r3-eth1')
    net['r3'].cmd('ip route add 192.168.7.0/29 via 192.168.3.1 dev r3-eth1')
    net['r3'].cmd('iptables -A FORWARD -p icmp -d 192.168.6.0/29 -s 192.168.2.2 -j DROP > firewal.out')
    net['r3'].cmd('iptables -A FORWARD -p icmp -d 192.168.7.0/29 -s 192.168.2.2 -j DROP > firewal.out')
    net['r1'].cmd('iptables -A FORWARD -p icmp -d 192.168.6.0/29 -s 192.168.7.0/29 -j DROP > file2.out')
    net['r1'].cmd('iptables -A FORWARD -p icmp -d 192.168.7.0/29 -s 192.168.6.0/29 -j DROP > file3.out')    

	
   
   
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

