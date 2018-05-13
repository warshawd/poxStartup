import networkx
import pickle

numNodes = 14
degree = 3

graph = networkx.random_regular_graph(degree, numNodes)

port_offset = 100
switch_dpid_offset = 100
host_dpid_offset = 200



routing = {}
neighbors = {}



for i in range(numNodes):
  neighbors[i] = list(graph[i].keys())
  neighbors[i].sort()
  print "Node " + str(i) + " connects to " + str(neighbors[i])

#This goes in the controller, and we load same graph to put into "graph"
print "Routing Table:\n"
for source in range(numNodes):
  routing[source] = {}
  string = str(source) + ":\t"
  for target in range (numNodes):
    path = networkx.shortest_path(graph, source, target)
    if len(path) == 1:
      string = string + str(path[0]) + '\t'
      routing[source][target] = path[0]
    else:
      string = string + str(path[1]) + '\t'
      routing[source][target] = path[1]
  print string





save_obj = [numNodes, degree, neighbors, routing, port_offset, switch_dpid_offset, host_dpid_offset]

with open('../../graph_items.pickle', 'wb') as handle:
  pickle.dump(save_obj, handle, protocol=pickle.HIGHEST_PROTOCOL)















