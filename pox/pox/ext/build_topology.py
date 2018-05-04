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

            leftHost = self.addHost( 'h1' )
            rightHost = self.addHost( 'h2' )
            leftSwitch = self.addSwitch( 's3' )
            rightSwitch = self.addSwitch( 's4' )
            # topSwitch = self.addSwitch( 's5')
            # topHost = self.addHost('h6')

            # # Add links
            # # self.addLink( leftHost, rightHost )

            self.addLink( leftHost, leftSwitch )
            self.addLink( leftSwitch, rightSwitch )
            self.addLink( rightSwitch, rightHost )
            # self.addLink( topHost, topSwitch )
            # self.addLink( leftSwitch, topSwitch )
            # self.addLink( rightSwitch, topSwitch )


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

