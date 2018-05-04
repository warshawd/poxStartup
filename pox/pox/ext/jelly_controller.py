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


log = core.getLogger()

switch_i_dpid = {}
switch_i_dpid_a = []
switch_number_wa = 0
switch_dpid_i = {}

switches_by_dpid = {}
switch_to_dest_to_next_port = {}


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
      self.resend_packet(packet_in, of.OFPP_ALL)
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
    self.act_like_switch(packet, packet_in)



  # def _handle_openflow_ConnectionUp (self, event):
  #   sw = switches_by_dpid.get(event.dpid)

  #   if sw is None:
  #     # New switch

  #     sw = TopoSwitch()
  #     switches_by_dpid[event.dpid] = sw
  #     sw.connect(event.connection)
  #   else:
  #     sw.connect(event.connection)



class topo_addressing (object):
  def __init__ (self):
    core.listen_to_dependencies(self, listen_args={'openflow':{'priority':0}})

  def _handle_ARPHelper_ARPRequest (self, event):
    pass # Just here to make sure we load it

  def _handle_openflow_discovery_LinkEvent (self, event):
    def flip (link):
      return Discovery.Link(link[2],link[3], link[0],link[1])

    l = event.link
    sw1 = switches_by_dpid[l.dpid1]
    sw2 = switches_by_dpid[l.dpid2]

    # Invalidate all flows and path info.
    # For link adds, this makes sure that if a new link leads to an
    # improved path, we use it.
    # For link removals, this makes sure that we don't use a
    # path that may have been broken.
    #NOTE: This could be radically improved! (e.g., not *ALL* paths break)
    # clear = of.ofp_flow_mod(command=of.OFPFC_DELETE)
    # for sw in switches_by_dpid.itervalues():
    #   if sw.connection is None: continue
    #   sw.connection.send(clear)
    # path_map.clear()

    # if event.removed:
    #   # This link no longer okay
    #   if sw2 in adjacency[sw1]: del adjacency[sw1][sw2]
    #   if sw1 in adjacency[sw2]: del adjacency[sw2][sw1]

    #   # But maybe there's another way to connect these...
    #   for ll in core.openflow_discovery.adjacency:
    #     if ll.dpid1 == l.dpid1 and ll.dpid2 == l.dpid2:
    #       if flip(ll) in core.openflow_discovery.adjacency:
    #         # Yup, link goes both ways
    #         adjacency[sw1][sw2] = ll.port1
    #         adjacency[sw2][sw1] = ll.port2
    #         # Fixed -- new link chosen to connect these
    #         break
    # else:
      # # If we already consider these nodes connected, we can
      # # ignore this link up.
      # # Otherwise, we might be interested...
      # if adjacency[sw1][sw2] is None:
      #   # These previously weren't connected.  If the link
      #   # exists in both directions, we consider them connected now.
      #   if flip(l) in core.openflow_discovery.adjacency:
      #     # Yup, link goes both ways -- connected!
      #     adjacency[sw1][sw2] = l.port1
      #     adjacency[sw2][sw1] = l.port2

    # for sw in switches_by_dpid.itervalues():
    #   sw.send_table()


  def _handle_openflow_ConnectionUp (self, event):
    log.debug("Controlling %s" % (event.connection,))
    sw = Tutorial(event.connection, event.dpid)
    # sw = switches_by_dpid.get(event.dpid)

    # if sw is None:
    #   # New switch

    #   sw = TopoSwitch()
    #   switches_by_dpid[event.dpid] = sw
    #   sw.connect(event.connection)
    # else:
    #   sw.connect(event.connection)




def launch ():
  """
  Starts the component
  """

  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    sw = Tutorial(event.connection, event.dpid)
    log.info("event")
    log.info(event)
    # print(event.dpid)
    # switches_by_dpid[event.dpid] = sw

  # def _handle_LinkEvent (event):
  #   log.info("\n\n\n WOFNOW ]n\n\n\n")
    # log.debug("Controlling %s" % (event.connection,))
    # sw = Tutorial(event.connection, event.dpid)


  # core.registerNew(jelly_addressing)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  # core.openflow_discovery.addListenerByName("LinkEvent", woz)
