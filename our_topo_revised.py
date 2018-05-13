import networkx
import pickle

# numNodes = 14
# degree = 3

routing = {}
neighbors = {}
# neighbors2 = {}
# neighbors3 = {}

# graph = networkx.random_regular_graph(degree, numNodes)

# graph2 = networkx.random_regular_graph(degree, numNodes)


# with open('graph.pickle', 'wb') as handle:
#   pickle.dump(graph, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('graph.pickle', 'rb') as handle:
  graph = pickle.load(handle)

# print "difference: "
# for i in range(numNodes):
#   neighbors[i] = list(graph[i].keys())
#   neighbors[i].sort()
#   # neighbors2[i] = list(graph2[i].keys())
#   # neighbors2[i].sort()
#   neighbors3[i] = list(b[i].keys())
#   neighbors3[i].sort()
#   print set(neighbors[i]) == set(neighbors3[i])
# # print networkx.difference(graph, b)
# # print networkx.difference(graph, graph2) 
# print "should be no diff"


# leftHost = self.addHost( 'h1', ip='10.1.1.1', mac='00:00:00:00:00:11')
# rightHost = self.addHost( 'h2', ip='10.2.2.2', mac='00:00:00:00:00:22')
# leftSwitch = self.addSwitch( 's55', ip='10.6.6.6', mac='00:00:00:00:00:66')
# rightSwitch = self.addSwitch( 's77', ip='10.7.7.7', mac='00:00:00:00:00:77')

# self.addLink( leftHost, leftSwitch, port1=1, port2=2 )
# self.addLink( leftSwitch, rightSwitch, port1=3, port2=4 )
# self.addLink( rightSwitch, rightHost, port1=5, port2=6 )

port_offset = 100
dpid_offset = 100
switches = {}
hosts = {}

def createHost(num) :
  ip_str= '9.0.0.' + str(num)
  mac_str = '99:00:00:00:00:'
  if num < 10 :
    mac_str += '0' + str(num)
  else : #more explicit, if longer
    mac_str += str(num)
  dpid_str = 'h' + str((dpid_offset*2) + num) #Can't have DPID 0
  return self.addHost( dpid_str, ip=ip_str, mac=mac_str)

# leftSwitch = self.addSwitch( 's55', ip='10.6.6.6', mac='00:00:00:00:00:66')
def createSwitch(num) :
  ip_str= '10.0.0.' + str(num)
  mac_str = '00:00:00:00:00:'
  if num < 10 :
    mac_str += '0' + str(num)
  else : #more explicit, if longer
    mac_str += str(num)
  dpid_str = 's' + str(dpid_offset + num) #Can't have DPID 0
  return self.addSwitch( dpid_str, ip=ip_str, mac=mac_str)



for i in range(numNodes) :
  switches[i] = createSwitch(i)
  hosts[i] = creatHost(i)

for i in range(numNodes) :
  #"self" link from the port that usually routes to my switch, but here routes from my switch to the associated host
  self.addLink( switches[i], hosts[i], port1=(port_offset + i), port2=(port_offset + i))

for i in range(numNodes):
  neighbors[i] = list(graph[i].keys())
  neighbors[i].sort()
  print "Node " + str(i) + " connects to " + str(neighbors[i])
  for j in neighbors[i] : #connecting i to j via ports j & i respectively [so that if I go to j, I go over port j, etc]
    if j >= i : #we've already linked if j < i
      self.addLink( switches[i], switches[j], port1=(port_offset + j), port2=(port_offset + i) )


#This goes in the controller, and we load same graph to put into "graph"
print "Routing Table:\n"
for source in range(numNodes):
  routing[source] = {}
  # string = str(source) + ":\t"
  for target in range (numNodes):
    path = networkx.shortest_path(graph, source, target)
    if len(path) == 1:
      # string += 'x\t'
      routing[source][target] = path[0]
    else:
      # string = string + str(path[1]) + '\t'
      routing[source][target] = path[1]
  # print string


def parse_dest_from_ip(ip) :
  ip_str = str(ip)
  dest_str = ip_str.split('.')[3]
  return int(dest_str)

# print """"
# routing = {}
# for source in range(14):
#   routing[source] = {}

#   """
# for source in range(14):
#   for target in range(14):
#     print "\trouting[" + str(source) + "][" + str(target) + "] = " + str(routing[source][target])







