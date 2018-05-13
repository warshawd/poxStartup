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