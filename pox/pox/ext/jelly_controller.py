# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's roughly similar to the one Brandon Heller did for NOX.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.util import str_to_bool, dpid_to_str
from pox.lib.recoco import Timer

import pox.openflow.libopenflow_01 as of

from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

from pox.lib.addresses import IPAddr,EthAddr,parse_cidr
from pox.lib.addresses import IP_BROADCAST, IP_ANY
from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.proto.dhcpd import DHCPLease, DHCPD
from collections import defaultdict
from pox.openflow.discovery import Discovery
import time
import pickle

from pox.lib.packet.packet_utils import checksum

import random


log = core.getLogger()


# Timeout for flows
FLOW_IDLE_TIMEOUT = 10

# Timeout for ARP entries
ARP_TIMEOUT = 60 * 2

# Maximum number of packet to buffer on a switch for an unknown IP
MAX_BUFFERED_PER_IP = 5

# Maximum time to hang on to a buffer for an unknown IP in seconds
MAX_BUFFER_TIME = 5

numNodes, degree, neighbors, routing_vanilla = None, None, None, None
ecmp8_routing, ecmp64_routing, kshortest_routing, kshortest_routing_paths = None, None, None, None
kShortest, port_offset, switch_dpid_offset, host_dpid_offset = None, None, None, None
with open('graph_items.pickle', 'rb') as handle:
    numNodes, degree, neighbors, routing_vanilla, ecmp8_routing, ecmp64_routing, kshortest_routing, kshortest_routing_paths, kShortest, port_offset, switch_dpid_offset, host_dpid_offset = pickle.load(handle)

packet_num = 0

class Entry (object):
  """
  Not strictly an ARP entry.
  We use the port to determine which port to forward traffic out of.
  We use the MAC to answer ARP replies.
  We use the timeout so that if an entry is older than ARP_TIMEOUT, we
   flood the ARP request rather than try to answer it ourselves.
  """
  def __init__ (self, port, mac):
    self.timeout = time.time() + ARP_TIMEOUT
    self.port = port
    self.mac = mac

  def __eq__ (self, other):
    if type(other) == tuple:
      return (self.port,self.mac)==other
    else:
      return (self.port,self.mac)==(other.port,other.mac)
  def __ne__ (self, other):
    return not self.__eq__(other)

  def isExpired (self):
    if self.port == of.OFPP_NONE: return False
    return time.time() > self.timeout


def dpid_to_mac (dpid):
  return EthAddr("%012x" % (dpid & 0xffFFffFFffFF,))


class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection, dpid):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    self.dpid = dpid

    # self.robin = 0

    # self.robin_per_route_node = {}
    #fine to do expensive stuff during initialization
    # for i in range(numNodes) :
    #    self.robin_per_route_node[i] = {}
    #   for j in range(numNodes) :
    #     self.robin_per_route_node[i][j] = {}
    #     for k in range(numNodes) :
    #       self.robin_per_route_node[i][j][k] = 0

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}

        # These are "fake gateways" -- we'll answer ARPs for them with MAC
    # of the switch they're connected to.
    # self.fakeways = set(fakeways)

    # # If this is true and we see a packet for an unknown
    # # host, we'll ARP for it.
    # self.arp_for_unknowns = arp_for_unknowns

    # (dpid,IP) -> expire_time
    # We use this to keep from spamming ARPs
    self.outstanding_arps = {}

    # (dpid,IP) -> [(expire_time,buffer_id,in_port), ...]
    # These are buffers we've gotten at this datapath for this IP which
    # we can't deliver because we don't know where they go.
    self.lost_buffers = {}

    # For each switch, we map IP addresses to Entries
    self.arpTable = {}


  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)


  def act_like_hub (self, packet, packet_in):
    """
    Implement hub-like behavior -- send all packets to all ports besides
    the input port.
    """
    # We want to output to all ports -- we do that using the special
    # OFPP_ALL port as the output port.  (We could have also used
    # OFPP_FLOOD.)
    self.resend_packet(packet_in, of.OFPP_ALL)

    # Note that if we didn't get a valid buffer_id, a slightly better
    # implementation would check that we got the full data before
    # sending it (len(packet_in.data) should be == packet_in.total_len)).


  def act_like_switch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """


    #tldr: who are we?  Then look up who we should send to.  Done.
    # self.
    # dest = dest_to_next_port[packet.dst]



    # port
    # file = open('myfile.txt', 'w+')
    # write("Hello World again")
    # fh.close
    # log.debug("WOWOW")
    # log.warning("range")

    log.info("\n str \n")
    # log.info(self.dpid)
    log.info("\n end \n")

    ip = packet.find('ipv4')
    if ip is None:
      # This packet isn't IP!
      # self.resend_packet(packet_in, of.OFPP_ALL)
      return
    log.info("IP!")
    log.info(ip.dstip)
    log.info(dir(packet))
    dest = int(str(ip.dstip).split('.')[3])
    log.info(dest)

    dest_port = dest #here coincidentally the same, not true in general esp for nontrivial topologies

    self.resend_packet(packet_in, dest_port)
    # else :
    # self.resend_packet(packet_in, 0)





    # port = self.macToPort[packet.dst]
    # msg = of.ofp_flow_mod()
    # msg.match = of.ofp_match.from_packet(packet, event.port)
    # msg.idle_timeout = 10
    # msg.hard_timeout = 30
    # msg.actions.append(of.ofp_action_output(port = port))
    # msg.data = event.ofp # 6a
    # self.connection.send(msg)



    """ # DELETE THIS LINE TO START WORKING ON THIS (AND THE ONE BELOW!) #

    # Here's some psuedocode to start you off implementing a learning
    # switch.  You'll need to rewrite it as real Python code.

    # Learn the port for the source MAC
    self.mac_to_port ... <add or update entry>

    if the port associated with the destination MAC of the packet is known:
      # Send packet out the associated port
      self.resend_packet(packet_in, ...)

      # Once you have the above working, try pushing a flow entry
      # instead of resending the packet (comment out the above and
      # uncomment and complete the below.)

      log.debug("Installing flow...")
      # Maybe the log statement should have source/destination/port?

      #msg = of.ofp_flow_mod()
      #
      ## Set fields to match received packet
      #msg.match = of.ofp_match.from_packet(packet)
      #
      #< Set other fields of flow_mod (timeouts? buffer_id?) >
      #
      #< Add an output action, and send -- similar to resend_packet() >

    else:
      # Flood the packet out everything but the input port
      # This part looks familiar, right?
      self.resend_packet(packet_in, of.OFPP_ALL)

    """ # DELETE THIS LINE TO START WORKING ON THIS #


  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    dpid = event.connection.dpid
    inport = event.port

    dest_ip_str = ''


    arpp = packet.find('arp')
    ip = packet.find('ipv4')
    if arpp is not None :
      # log.info("spageti")
      # log.info(arpp.next)
      a = packet.next
      dest_ip_str = str(a.protodst)
      src_ip_str = str(a.protosrc)

      # msg = of.ofp_packet_out(in_port = inport, data = event.ofp,
      #     action = of.ofp_action_output(port = out_port))
      # event.connection.send(msg)
      # return
    elif ip is not None :
      dest_ip_str = str(ip.dstip)
      src_ip_str = str(ip.srcip)
    else :
      # This packet isn't IP!
      log.info("\n\n\nWELP\n\n\n")
      # self.resend_packet(packet_in, of.OFPP_ALL)
      return


    # dest = int(ip_str.split('.')[3])

    me_id = self.dpid - switch_dpid_offset
    target_id = int(dest_ip_str.split('.')[3])
    # log.info(dest_ip_str)
    # log.info("SRC")
    # log.info(src_ip_str)
    source_id = int(src_ip_str.split('.')[3])
    # log.info(source_id)

    #all the inefficiency of computing this is handled in setup now!

    #note: this actually does load balancing even for the weighted cases
    #(e.g. for me->x->dst, me->x->q->dst, me->y->dst, twice as many packets should get sent to x as y)
    #which we do!  because when we computed this dictionary, it will have 2 elements that say x next, and one saying y

    # ROUTING_TYPE[source_id][target_id][me_id] will give us all routing options for this flow, from this node, and will be weighted
    # - e.g. the list will have 2 identical options if they should be weighted more
    # options = ecmp64_routing[source_id][target_id][me_id]
    # options = ecmp8_routing[source_id][target_id][me_id]

    # self.robin_per_route_node[source_id][target_id][me_id]
    if me_id == target_id :
      out_port = me_id + port_offset
      self.resend_packet(packet_in, out_port)
      # self.robin += 1
      return


    # log.info("SPAG")
    # log.info(str(source_id) + " " + str(target_id) + " " + str(me_id))



    options, options_len = ecmp8_routing[source_id][target_id]
    # log.info(options)
    # log.info(packet_in)
    # log.info(packet_in.data)
    # log.info(packet_in.data[:4])
    # log.info(packet_in.data[:4])
    # log.info(packet.payload)

    #this is LAST REMAINING PART - need to find some way to "hash" packet s.t. it always ends up with same hash
    # bucketize = int(packet_in.total_len)
    # bucketize = int(checksum(packet_in.data))
    bucketize = int(packet_in.total_len)
    if ip is not None :
      bucketize = ip.csum
    bucketize = bucketize % options_len

    # options_len = len(options) #we can also include this in the precomputed data structure, if we want more efficiency -e.g. a tuple of len & the options list
    
    #note: because the packet always hashes to the same bucket, we will never look up a path we are not on
    #(b/c the only way the packet could get to this switch was by following a path that we are on, and it
    #will hash to that same bucket)
    
    # out_port = options[bucketize%options_len][me_id] + port_offset
    #(1)
    # out_port = options[0][me_id] + port_offset

    #(2)
    out_port = options[bucketize][me_id] + port_offset

    #(3)
    # out_port = options[bucketize][me_id] + port_offset
    # if True :
    #   out_port = options[0][me_id] + port_offset

    # options = kshortest_routing[source_id][target_id][me_id]
    # paths = kshortest_routing_paths[source_id][target_id]

    # random_source = source_id + target_id + me_id #THIS IS NOT GOOD, JUST SANITY CHECKING
    # if source_id == 1 and target_id == 5 :
    #   log.info("SPAG")
    #   log.info(str(source_id) + " " + str(target_id) + " " + str(me_id))
    #   log.info(options)
    #   log.info(paths)
    #   log.info(packet_in)
      # log.info(packet.next)
      # log.info(aarp)
      # log.info(ip)

    # if source_id == 3 and target_id == 5 :
    #   log.info("SPAG")
    #   log.info(str(source_id) + " " + str(target_id) + " " + str(me_id))
    #   log.info(options)
    #   log.info(paths)
    # out_port = random.choice(options) + port_offset
    # bucketize = int(packet_in.buffer_id)
    # option_len = len(options)
    # # out_port = options[option_len - 1] + port_offset
    # out_port = options[(bucketize % option_len)] + port_offset
    # self.robin += 1 #this works out to be pretty much random & goes according to option weights as planned


    # def find_next_hop(path, me_id) :
    #   end = len(path)
    #   # for i in range(end, -1, -1) :
    #   for i in range(end) :
    #     rev_i = (end - 1) - i
    #     if me_id == path[rev_i] :
    #       if rev_i == (end - 1) :
    #         return me_id #we are last hop - go to host
    #       else :
    #         return path[rev_i + 1] #next hop
    #   return -1 #we're not on this path...

    # if target_id == me_id :
    #   out_port = me_id + port_offset
    # else :
    #   paths = ecmp8_routing[source_id][target_id] #we could just shuffle this - that would actually do the right thing!
    #   for path in paths :
    #     next_hop = find_next_hop(path) #we are necessarily on one of these paths
    #     if next_hop != -1 :
    #       out_port = next_hop + port_offset
    # if i in range(2) :
    #   out_port += 1
    # x = 0

    # out_port = routing_vanilla[me_id][target_id] +  port_offset
    # log.info("\n" + dest_ip_str + "  " + str(out_port))

    # log.info(self.dpid)
    # if (self.dpid == switch_dpid_offset + 0) :
    #     if (dest_ip_str == '9.9.9.0') :
    #         out_port = port_offset + 0
    #     elif (dest_ip_str == '9.0.0.1') :
    #         out_port = port_offset + 1
    #     else :
    #         out_port = port_offset + 2
    # elif (self.dpid == switch_dpid_offset + 1) :
    #     if (dest_ip_str == '9.9.9.0') :
    #         out_port = port_offset + 0
    #     elif (dest_ip_str == '9.9.9.1') :
    #         out_port = port_offset + 1
    #     else :
    #         out_port = port_offset + 2
    # elif (self.dpid == switch_dpid_offset + 2) :
    #     if (dest_ip_str == '9.9.9.0') :
    #         out_port = port_offset + 0
    #     elif (dest_ip_str == '9.9.9.1') :
    #         out_port = port_offset + 1
    #     else :
    #         out_port = port_offset + 2
    # else:
    #     log.info("WTF\n")

    # dest_port = dest #here coincidentally the same, not true in general esp for nontrivial topologies


    
    # if me_id == target_id :
    #   out_port = me_id + port_offset

    self.resend_packet(packet_in, out_port)#dest_port)

    # msg = of.ofp_packet_out(in_port = inport, data = event.ofp,
    #     action = of.ofp_action_output(port = out_port))
    # event.connection.send(msg)
    return


  # def _handle_openflow_ConnectionUp (self, event):

  #   if sw is None:
  #     # New switch

  #     sw = TopoSwitch()
  #     sw.connect(event.connection)
  #   else:
  #     sw.connect(event.connection)





#you can set IPs & even macs
#you can copy paste arp code from l2, l3 learning, etc
#in the build topology
#Example: ARP messages
#http://mininet.org/api/classmininet_1_1node_1_1Node.html


#if you do simple version of ECMP thing, want to actually install routing into routing tables (there's no barriers into this)

#handle packet is only 

#expect us to put it into a flow table, if we don't do per-jump balancing (because there's no reason we can't)
#use 000000s for your mac address - ffffs gets you random mac addresses

#how to specify mac address in mininet - how to specify port in mininet - etc.  All this stuff you should be able to specify in mininet
#-> just google this stuff - all should be able to be specified in mininet (build)

#all the examples show how to run them, you need to set flags & a bunch of other stuff to get them to work, but it's all covered somewhere in the wiki

#you will need to probably change Saachi's "exec" command - it's currently just hacky, you need different stuff

#sometimes people run into errors, you can just fix this by sending an arm sometimes.  Hypothetically if you just hardcoded everything, this shouldn't be an issue... but in practice might be

#buffer_id

#ofp.action port
#Example: sending a packet (packetout?)

# iperf -p -8 (8 flows)

# https://stackoverflow.com/questions/30496161/how-to-set-bandwidth-on-mininet-custom-topology


# save_obj = {numNodes, degree, neighbors, routing, port_offset, switch_dpid_offset, host_dpid_offset}


def launch ():
  """
  Starts the component
  """

  with open('graph_items.pickle', 'rb') as handle:
    numNodes, degree, neighbors, routing_vanilla, ecmp8_routing, ecmp64_routing, kshortest_routing, kshortest_routing_paths, kShortest, port_offset, switch_dpid_offset, host_dpid_offset = pickle.load(handle)
    # log.info(numNodes)
    # log.info(degree)




  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    sw = Tutorial(event.connection, event.dpid)
    log.info("start_switch w/: ")
    log.info(event.dpid)
    log.info(event.connection.dpid)
    # print(event.dpid)

  # def _handle_LinkEvent (event):
  #   log.info("\n\n\n WOFNOW ]n\n\n\n")
    # log.debug("Controlling %s" % (event.connection,))
    # sw = Tutorial(event.connection, event.dpid)


  # core.registerNew(jelly_addressing)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  # core.openflow_discovery.addListenerByName("LinkEvent", _handle_LinkEvent)
