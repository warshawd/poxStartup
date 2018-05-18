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
import pickle
import random
from mininet.util import quietRun, natural, custom


class JellyFishTop(Topo):
    ''' TODO, build your topology here'''
    def build(self):

            numNodes, degree, neighbors, routing_vanilla = None, None, None, None
            ecmp8_routing, ecmp64_routing, kshortest_routing, kshortest_routing_paths = None, None, None, None
            kShortest, port_offset, switch_dpid_offset, host_dpid_offset = None, None, None, None

            with open('../../graph_items.pickle', 'rb') as handle:
                numNodes, degree, neighbors, routing_vanilla, ecmp8_routing, ecmp64_routing, kshortest_routing, kshortest_routing_paths, kShortest, port_offset, switch_dpid_offset, host_dpid_offset = pickle.load(handle)


            def createHost(num) :
                ip_str= '9.9.9.' + str(num)
                mac_str = '99:00:00:00:00:'
                if num < 10 :
                    mac_str += '0' + str(num)
                else : #more explicit, if longer
                    mac_str += str(num)
                dpid_str = 'h' + str(host_dpid_offset + num) #Can't have DPID 0
                return self.addHost( dpid_str, ip=ip_str, mac=mac_str)

            # leftSwitch = self.addSwitch( 's55', ip='10.6.6.6', mac='00:00:00:00:00:66')
            def createSwitch(num) :
                ip_str= '10.10.10.' + str(num)
                mac_str = '00:00:00:00:00:'
                if num < 10 :
                    mac_str += '0' + str(num)
                else : #more explicit, if longer
                    mac_str += str(num)
                dpid_str = 's' + str(switch_dpid_offset + num) #Can't have DPID 0
                return self.addSwitch( dpid_str, ip=ip_str, mac=mac_str)

            def createLink(sw1, sw2, pt1, pt2) :
                return self.addLink(sw1, sw2, port1=(port_offset + pt2), port2=(port_offset + pt1), bw=5)

            switches = {}
            hosts = {}

            print('\n\n\n' + str(numNodes) + ' ' + str(degree) + '\n\n\n')

            for i in range(numNodes) :
                switches[i] = createSwitch(i)
                hosts[i] = createHost(i)

            for i in range(numNodes) :
                #"self" link from the port that usually routes to my switch, but here routes from my switch to the associated host
                createLink( switches[i], hosts[i], i, i)

            for i in range(numNodes):
                for j in neighbors[i] : #connecting i to j via ports j & i respectively [so that if I go to j, I go over port j, etc]
                    if j >= i : #we've already linked if j < i
                        createLink( switches[i], switches[j], i, j )
                        print("\nlinked: " + str(i) + ", " + str(j))


            # return hosts, switches
            # hosts[0] = createHost(0)
            # hosts[1] = createHost(1)
            # switches[0] = createSwitch(0)
            # switches[1] = createSwitch(1)

            # # leftHost.setMAC()
            # # rightHost.setMAC()
            # # leftSwitch.setMAC()
            # # rightSwitch.setMAC()

            # switches[2] = createSwitch(2)
            # hosts[2] = createHost(2)

            # # # Add links
            # # # self.addLink( leftHost, rightHost )

            # # dpid==55 -> left switch
            # # dpid==77 -> left switch
            # # 10.9.9.9 left host
            # # 10.5.5.5 right host

            # # dpid==55 :
            # #     if (10.9.9.9 dest) :
            # #         send over port 2
            # #     else :
            # #         send over port 3

            # # dpid==77 :
            # #     if (10.9.9.9 dest) :
            # #         send over port 4
            # #     else :
            # #         send over port 5

            # # self.addLink( leftHost, leftSwitch, port1=(port_offset + 0), port2=(port_offset + 0) )
            # # self.addLink( leftSwitch, rightSwitch, port1=(port_offset + 1), port2=(port_offset + 0) )
            # # self.addLink( rightSwitch, rightHost, port1=(port_offset + 1), port2=(port_offset + 1) )
            # # self.addLink( topHost, topSwitch, port1=(port_offset + 2), port2=(port_offset + 2) )
            # # self.addLink( leftSwitch, topSwitch, port1=(port_offset + 2), port2=(port_offset + 0) )
            # # self.addLink( rightSwitch, topSwitch, port1=(port_offset + 2), port2=(port_offset + 1) )
            # createLink(hosts[0], switches[0], 0, 0)
            # createLink(switches[0], switches[1], 0, 1)
            # createLink(switches[1], hosts[1], 1, 1)
            # createLink(hosts[2], switches[2], 2, 2)
            # createLink(switches[0], switches[2], 0, 2)
            # createLink(switches[1], switches[2], 1, 2)

def listening( src, dest, port=5001 ):
    "Return True if we can connect from src to dest on port"
    cmd = 'echo A | telnet -e A %s %s' % (dest.IP(), port)
    result = src.cmd( cmd )
    return 'Connected' in result




def genPermutationTraffic(num_items) :
    traffic = {}
    redo = True
    while redo:
        traffic = {}
        unused = set([i for i in range(num_items)])
        redo = False
        for source in range(num_items):
            target = source
            while target == source:
                target = random.sample(unused, 1)[0]
                if target == source and len(unused) == 1:
                    break
            if (target == source):
                redo = True
                print "Had to restart the graph gen"
                break
            else:
                traffic[source] = target
                unused.remove(target)
    return traffic


def experiment(net):
        flows_8 = False

        net.start()
        sleep(3) #3
        print 'Begin'
        # CLI( net )
        hosts = net.hosts
        # h1 = [hosts[0],hosts[1],hosts[2],hosts[3],hosts[4],hosts[5]]
        # res = []
        # res2  = []
        for h in hosts :
            h.cmd('iperf -s &')
        print("listening")
        sleep(1)

        traffic = genPermutationTraffic(len(hosts))
        with open('traffic.pickle', 'wb') as handle:
            pickle.dump(traffic, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # with open('traffic.pickle', 'rb') as handle:
        #     traffic = pickle.load(handle)

        for k, v in traffic.items() :
            print("key, value: " + str(k) + "," + str(v))
            if flows_8: #set to True for 8 flows
                # iperf_cmd = 'iperf -t 10 -i 0.5 -c 9.9.9.' + str(v) + ' &'
                iperf_cmd = 'iperf -t 10 -c 9.9.9.' + str(v) + ' &'
                for i in range(7) :
                    hosts[k].cmd(iperf_cmd)
            # iperf_cmd = 'iperf -t 10 -i 0.5 -c 9.9.9.' + str(v)
            iperf_cmd = 'iperf -t 10 -c 9.9.9.' + str(v)
            hosts[k].sendCmd(iperf_cmd)


        sleep(.5)
        results = []
        for h in hosts:
            x = h.waitOutput()
            results.append(x)
        for r in results :
            print r
        print "Done"

        sleep(1)
        quietRun( "pkill -9 iperf" )
        sleep(1) #3
        net.pingAll()
        net.stop()


def main():
    topo = JellyFishTop()
    net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink, controller=JELLYPOX)
    experiment(net)

if __name__ == "__main__":
    main()

