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

log = core.getLogger()

switch_i_dpid = {}
switch_i_dpid_a = []
switch_number_wa = 0
switch_dpid_i = {}

switches_by_dpid = {}
switch_to_dest_to_next_port = {}

# Timeout for flows
FLOW_IDLE_TIMEOUT = 10

# Timeout for ARP entries
ARP_TIMEOUT = 60 * 2

# Maximum number of packet to buffer on a switch for an unknown IP
MAX_BUFFERED_PER_IP = 5

# Maximum time to hang on to a buffer for an unknown IP in seconds
MAX_BUFFER_TIME = 5

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
    # switch_i_dpid[switch_number_wa] = dpid
    # switch_dpid_i[dpid] = switch_number_wa
    switch_i_dpid_a.append(dpid)
    # switch_number_wa += 1

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
    # dest_to_next_port = switch_to_dest_to_next_port[self.dpid]
    # dest = dest_to_next_port[packet.dst]



    # port
    # file = open('myfile.txt', 'w+')
    # write("Hello World again")
    # fh.close
    # log.debug("WOWOW")
    # log.warning("range")

    log.info("\n str \n")
    # log.info(self.dpid)
    # log.info(switch_i_dpid_a)
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

    # if self.dpid == switch_i_dpid_a[0] or self.dpid == switch_i_dpid_a[1] or self.dpid == switch_i_dpid_a[2] :
    self.resend_packet(packet_in, dest_port)
    # else :
    # self.resend_packet(packet_in, 0)

    # if (self.dpid != switch_i_dpid[2] && self.dpid != switch_i_dpid[3]) :
    #   self.resend_packet(packet_in, 1)
    # if packet.dst == switch_i_dpid[0] :
    #   self.resend_packet(packet_in, 0)
    # if packet.dst == switch_i_dpid[1] :
    #    self.resend_packet(packet_in, 0)
    # if packet.dst == switch_i_dpid[2] :
    #   self.resend_packet(packet_in, 0)
    # if packet.dst == switch_i_dpid[3] :
    #   self.resend_packet(packet_in, 0)




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
    # packet = event.parsed
    # if not packet.parsed:
    #   log.warning("%i %i ignoring unparsed packet", dpid, inport)
    #   return

    if dpid not in self.arpTable:
      # New switch -- create an empty table
      self.arpTable[dpid] = {}
      # for fake in self.fakeways:
      #   self.arpTable[dpid][IPAddr(fake)] = Entry(of.OFPP_NONE,
      #    dpid)


    arpp = packet.find('arp')
    if arpp is not None:
      a = packet.next
      log.info(a.opcode)
      log.info(str(a.protosrc))
      log.info(str(a.protodst))

      out_port = 0

      if (self.dpid == 55) :
          if (str(a.protodst) == '10.1.1.1') :
              out_port = 2
          elif (str(a.protodst) == '10.2.2.2') :
              out_port = 3
          else :
              out_port = 9
      if (self.dpid == 77) :
          if (str(a.protodst) == '10.1.1.1') :
              out_port = 4
          elif (str(a.protodst) == '10.2.2.2') :
              out_port = 5
          else :
              out_port = 11
      if (self.dpid == 99) :
          if (str(a.protodst) == '10.1.1.1') :
              out_port = 10
          elif (str(a.protodst) == '10.2.2.2') :
              out_port = 12     
          else :
              out_port = 8

      msg = of.ofp_packet_out(in_port = inport, data = event.ofp,
          action = of.ofp_action_output(port = out_port))
      event.connection.send(msg)
      return





    #   log.info("arp")
    # if False : 
      a = packet.next
      log.info("\n\naaaaaaarrrrrppp\n\n")
      log.info(a.opcode)
      log.info(str(a.protosrc))
      log.info(str(a.protodst))
      log.info("\n\nSAZZY\n\n")
      log.info("%i %i ARP %s %s => %s", dpid, inport,
       {arp.REQUEST:"request",arp.REPLY:"reply"}.get(a.opcode,
       'op:%i' % (a.opcode,)), str(a.protosrc), str(a.protodst))

      if a.prototype == arp.PROTO_TYPE_IP:
        if a.hwtype == arp.HW_TYPE_ETHERNET:
          if a.protosrc != 0:

            # Learn or update port/MAC info
            if a.protosrc in self.arpTable[dpid]:
              if self.arpTable[dpid][a.protosrc] != (inport, packet.src):
                log.info("%i %i RE-learned %s", dpid,inport,str(a.protosrc))
            else:
              log.debug("%i %i learned %s", dpid,inport,str(a.protosrc))
            self.arpTable[dpid][a.protosrc] = Entry(inport, packet.src)

            # Send any waiting packets...
            # self._send_lost_buffers(dpid, a.protosrc, packet.src, inport)

            if a.opcode == arp.REQUEST:
              # Maybe we can answer

              if a.protodst in self.arpTable[dpid]:
                # We have an answer...

                if not self.arpTable[dpid][a.protodst].isExpired():
                  # .. and it's relatively current, so we'll reply ourselves

                  r = arp()
                  r.hwtype = a.hwtype
                  r.prototype = a.prototype
                  r.hwlen = a.hwlen
                  r.protolen = a.protolen
                  r.opcode = arp.REPLY
                  r.hwdst = a.hwsrc
                  r.protodst = a.protosrc
                  r.protosrc = a.protodst
                  r.hwsrc = self.arpTable[dpid][a.protodst].mac
                  e = ethernet(type=packet.type, src=dpid_to_mac(dpid),
                               dst=a.hwsrc)
                  e.set_payload(r)
                  log.debug("%i %i answering ARP for %s" % (dpid, inport,
                   str(r.protosrc)))
                  msg = of.ofp_packet_out()
                  msg.data = e.pack()
                  msg.actions.append(of.ofp_action_output(port =
                                                          of.OFPP_IN_PORT))
                  msg.in_port = inport
                  event.connection.send(msg)
                  return

      # Didn't know how to answer or otherwise handle this ARP, so just flood it
      log.debug("%i %i flooding ARP %s %s => %s" % (dpid, inport,
       {arp.REQUEST:"request",arp.REPLY:"reply"}.get(a.opcode,
       'op:%i' % (a.opcode,)), str(a.protosrc), str(a.protodst)))

      log.info("\n\n\n\n\nFLOODER\n\n\n\n\n")

      msg = of.ofp_packet_out(in_port = inport, data = event.ofp,
          action = of.ofp_action_output(port = of.OFPP_FLOOD))
      event.connection.send(msg)

    # Comment out the following line and uncomment the one after
    # when starting the exercise.
    print "Src: " + str(packet.src)
    print "Dest: " + str(packet.dst)
    print "Event port: " + str(event.port)
    # self.act_like_hub(packet, packet_in)
    log.info("packet in on port")
    log.info(event.port)
    log.info("src, dst: ")
    log.info(packet.src)
    log.info(packet.dst)
    log.info("full packet")
    log.info(packet)
    log.info("full event")
    log.info(event)
    # ip = packet.find('ipv4')
    # if ip is None:
    #   # This packet isn't IP!
    #   self.act_like_switch(packet, packet_in)
    #   return
    # log.info("IP!")
    # log.info(ip.dstip)
    # dest = int(str(ip.dstip).split('.')[3]) - 1
    # log.info(IPAddr("10.0.0.1"))

    # self.act_like_switch(packet, packet_in)

    ip = packet.find('ipv4')
    if ip is None:
      # This packet isn't IP!
      log.info("\n\n\nWELP\n\n\n")
      # self.resend_packet(packet_in, of.OFPP_ALL)
      return
    log.info("IP! on dpid")
    log.info(self.dpid)
    log.info(ip.dstip)
    # log.info(dir(packet))
    dest = int(str(ip.dstip).split('.')[3])
    log.info(dest)


    # dpid==55 -> left switch
    # dpid==77 -> left switch
    # 10.9.9.9 left host
    # 10.5.5.5 right host


    out_port = 0

    if (self.dpid == 55) :
        if (str(ip.dstip) == '10.1.1.1') :
            out_port = 2
        elif (str(ip.dstip) == '10.2.2.2') :
            out_port = 3
        else :
            out_port = 9
    if (self.dpid == 77) :
        if (str(ip.dstip) == '10.1.1.1') :
            out_port = 4
        elif (str(ip.dstip) == '10.2.2.2') :
            out_port = 5
        else :
            out_port = 11
    if (self.dpid == 99) :
        if (str(ip.dstip) == '10.1.1.1') :
            out_port = 10
        elif (str(ip.dstip) == '10.2.2.2') :
            out_port = 12     
        else :
            out_port = 8

    # dest_port = dest #here coincidentally the same, not true in general esp for nontrivial topologies

    # if self.dpid == switch_i_dpid_a[0] or self.dpid == switch_i_dpid_a[1] or self.dpid == switch_i_dpid_a[2] :
    self.resend_packet(packet_in, out_port)#dest_port)


  # def _handle_openflow_ConnectionUp (self, event):
  #   sw = switches_by_dpid.get(event.dpid)

  #   if sw is None:
  #     # New switch

  #     sw = TopoSwitch()
  #     switches_by_dpid[event.dpid] = sw
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



def launch ():
  """
  Starts the component
  """

  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    sw = Tutorial(event.connection, event.dpid)
    log.info("start_switch w/: ")
    log.info(event.dpid)
    log.info(event.connection.dpid)
    # print(event.dpid)
    # switches_by_dpid[event.dpid] = sw

  # def _handle_LinkEvent (event):
  #   log.info("\n\n\n WOFNOW ]n\n\n\n")
    # log.debug("Controlling %s" % (event.connection,))
    # sw = Tutorial(event.connection, event.dpid)


  # core.registerNew(jelly_addressing)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  # core.openflow_discovery.addListenerByName("LinkEvent", _handle_LinkEvent)
