import networkx

numNodes = 14
degree = 3

routing = {}
neighbors = {}

graph = networkx.random_regular_graph(degree, numNodes)

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