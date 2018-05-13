import networkx

import pickle

numNodes = 14
degree = 3

routing = {}
neighbors = {}
neighbors2 = {}
neighbors3 = {}

graph = networkx.random_regular_graph(degree, numNodes)

graph2 = networkx.random_regular_graph(degree, numNodes)


with open('graph.pickle', 'wb') as handle:
    pickle.dump(graph, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('graph.pickle', 'rb') as handle:
    b = pickle.load(handle)

print "difference: "
for i in range(numNodes):
  neighbors[i] = list(graph[i].keys())
  neighbors[i].sort()
  # neighbors2[i] = list(graph2[i].keys())
  # neighbors2[i].sort()
  neighbors3[i] = list(b[i].keys())
  neighbors3[i].sort()
  print set(neighbors[i]) == set(neighbors3[i])
# print networkx.difference(graph, b)
# print networkx.difference(graph, graph2) 
print "should be no diff"


for i in range(numNodes):
  neighbors[i] = list(graph[i].keys())
  neighbors[i].sort()
  print "Node " + str(i) + " connects to " + str(neighbors[i])

print "Routing Table:\n"
for source in range(numNodes):
  routing[source] = {}
  string = str(source) + ":\t"
  for target in range (numNodes):
    path = networkx.shortest_path(graph, source, target)
    if len(path) == 1:
      string += 'x\t'
      routing[source][target] = -1
    else:
      string = string + str(path[1]) + '\t'
      routing[source][target] = path[1]
  print string

print """"
routing = {}
for source in range(14):
  routing[source] = {}

  """
for source in range(14):
  for target in range(14):
    print "\trouting[" + str(source) + "][" + str(target) + "] = " + str(routing[source][target])







    