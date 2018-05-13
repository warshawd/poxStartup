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

            k = 10
            r = 5 #for switch to switch
            #k-r = for servers
            num_switches = 100
            num_servers = 100
            switch_neighbors = {}
            num_ports_used = [0 for i in range(100)]
            free_candidates = set([])
            break_links_set = set([])
            switches = []
            for i in range(num_switches) :
                switch_neighbors[i] = set([])
            for i in range(num_switches) :
                name = 's' + i
                switches[i]= self.addSwitch( name )
                free_candidates.add(i)
            for i in range(num_servers) :
                name = 'h' + i
                switches[i]= self.addSwitch( name )


            while (len(free_candidates) >= 2) :
                pair = random.sample(free_candidates,2)
                src = pair[0]
                dst = pair[1]
                if src == dst :
                    continue #probably unneed, better safe than sorry
                if dst in switch_neighbors[src] :
                    has_available_connections = False
                    for available in free_candidates :
                        if available not in switch_neighbors[src] :
                            has_available_connections = True
                            break
                    if not has_available_connections :
                        break_links_set.add(src)
                        free_candidates.remove(src)
                    continue

                self.addLink(switches[src], switches[dst])
                num_ports_used[src] += 1
                num_ports_used[dst] += 1
                if num_ports_used[src] == r :
                    free_candidates.remove(src)
                if num_ports_used[dst] == r :
                    free_candidates.remove(dst)
                switch_neighbors[src].add(dst)
                switch_neighbors[dst].add(src)

            break_links_set = free_candidates.union(break_links_set)
            for switch_i in break_links_set :
                while num_ports_used[switch_i] < (r-2) :
                    random_switch_a = random.randint(num_switches)
                    if random_switch_a in switch_neighbors[switch_i] :
                        continue
                    random_switch_b = random.sample(switch_neighbors[random_switch_a],1)
                    if random_switch_b in switch_neighbors[switch_i] :
                        continue
                    self.delLink(switches[random_switch_a], switches[random_switch_b])
                    self.addLink(switches[random_switch_a], switches[switch_i])
                    self.addLink(switches[random_switch_b], switches[switch_i])
                    num_ports_used[switch_i] += 2






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

