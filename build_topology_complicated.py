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
from random import randint



class JellyFishTop(Topo):
    ''' TODO, build your topology here'''
    def build(self):

            k = 12
            r = 3 #for switch to switch
            #k-r = for servers
            num_switches = 14
            num_servers = 14
            switch_names = ["s" + str(i) for i in range(num_switches)]
            server_names = ["h" + str(i) for i in range(num_servers)]
            switch_neighbors = {}
            switches = []
            servers = []
            for i in range(num_switches) :
                switch_neighbors[i] = set([])
            for i in range(num_switches) :
                switches.append(self.addSwitch( switch_names[i] ))
            for i in range(num_servers) :
                servers.append(self.addHost( server_names[i] ))
                self.addLink(server_names[i], switch_names[i])


            def addLinks(source, targets):
              for i in range(len(targets)):
                if targets[1] < source:
                  continue
                self.addLink(switch_names[source], switch_names[targets[i]])

            addLinks(0, [2, 7, 10])
            addLinks(1, [3, 9, 11])
            addLinks(2, [0, 7, 11])
            addLinks(3, [1, 4, 8])
            addLinks(4, [3, 5, 12])
            addLinks(5, [4, 6, 11])
            addLinks(6, [5, 12, 13])
            addLinks(7, [0, 2, 8])
            addLinks(8, [3, 7, 9])
            addLinks(9, [1, 8, 10])
            addLinks(10, [0, 9, 13])
            addLinks(11, [1, 2, 5])
            addLinks(12, [4, 6, 13])
            addLinks(13, [6, 10, 12])




            # leftHost = self.addHost( 'h1' )
            # rightHost = self.addHost( 'h2' )
            # leftSwitch = self.addSwitch( 's3' )
            # rightSwitch = self.addSwitch( 's4' )

            # # Add links
            # self.addLink( leftHost, leftSwitch )
            # self.addLink( leftSwitch, rightSwitch )
            # self.addLink( rightSwitch, rightHost )


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

