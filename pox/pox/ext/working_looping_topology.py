import os
import sys
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import OVSController
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.cli import CLI
sys.path.append("../../")
from pox.ext.jelly_pox import JELLYPOX
from subprocess import Popen
from time import sleep, time



class JellyFishTop(Topo):
    ''' TODO, build your topology here'''
    def build(self):


            # for i in range(5) :
            #     name = 'h'
            #     name += str((i+1))
            #     host = self.addHost( name )
            #     hosts.append(host)
            # for i in range(5) :
            #     name = 's'
            #     name += str((i+5))
            #     switch = self.addSwitch( name )
            #     self.addLink(hosts[i], switch)
            #     switches.append(switch)

            # for i in range(5) :
            #     for j in range(5) :
            #         if i < j :
            #             self.addLink( switches[i], switches[j])

            leftHost = self.addHost( 'h1', ip='10.1.1.1', mac='00:00:00:00:00:11')
            rightHost = self.addHost( 'h2', ip='10.2.2.2', mac='00:00:00:00:00:22')
            leftSwitch = self.addSwitch( 's55', ip='10.6.6.6', mac='00:00:00:00:00:66')
            rightSwitch = self.addSwitch( 's77', ip='10.7.7.7', mac='00:00:00:00:00:77')

            # leftHost.setMAC()
            # rightHost.setMAC()
            # leftSwitch.setMAC()
            # rightSwitch.setMAC()

            topSwitch = self.addSwitch( 's99', ip='10.9.9.9', mac='00:00:00:00:00:99')
            topHost = self.addHost('h3', ip='10.3.3.3', mac='00:00:00:00:00:33')

            # # Add links
            # # self.addLink( leftHost, rightHost )

            # dpid==55 -> left switch
            # dpid==77 -> left switch
            # 10.9.9.9 left host
            # 10.5.5.5 right host

            # dpid==55 :
            #     if (10.9.9.9 dest) :
            #         send over port 2
            #     else :
            #         send over port 3

            # dpid==77 :
            #     if (10.9.9.9 dest) :
            #         send over port 4
            #     else :
            #         send over port 5

            self.addLink( leftHost, leftSwitch, port1=1, port2=2 )
            self.addLink( leftSwitch, rightSwitch, port1=3, port2=4 )
            self.addLink( rightSwitch, rightHost, port1=5, port2=6 )
            self.addLink( topHost, topSwitch, port1=7, port2=8 )
            self.addLink( leftSwitch, topSwitch, port1=9, port2=10 )
            self.addLink( rightSwitch, topSwitch, port1=11, port2=12 )


def experiment(net):
        net.start()
        sleep(3)
        net.pingAll()
        net.stop()

def main():
    topo = JellyFishTop()
    net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink, controller=JELLYPOX)
    experiment(net)

if __name__ == "__main__":
    main()

