import networkx
import pickle
import random
import Queue

numNodes = 16
degree = 4

graph = networkx.random_regular_graph(degree, numNodes)

port_offset = 100
switch_dpid_offset = 100
host_dpid_offset = 200



routing_vanilla = {}
neighbors = {}



for i in range(numNodes):
  neighbors[i] = list(graph[i].keys())
  neighbors[i].sort()
  print "Node " + str(i) + " connects to " + str(neighbors[i])

#This goes in the controller, and we load same graph to put into "graph"
print "Routing Table:\n"
for source in range(numNodes):
  routing_vanilla[source] = {}
  string = str(source) + ":\t"
  for target in range (numNodes):
    path = networkx.shortest_path(graph, source, target)
    if len(path) == 1:
      string = string + str(path[0]) + '\t'
      routing_vanilla[source][target] = path[0]
    else:
      string = string + str(path[1]) + '\t'
      routing_vanilla[source][target] = path[1]
  print string



numServers = numNodes

kShortest = 8

def BFS(source, target):
  topK = []
  candidates = []
  candidates.append([source])
  doneWithECMP = False
  while (len(topK) < kShortest or not doneWithECMP) and len(candidates) > 0:
    current = candidates.pop(0)
    if len(topK) >= kShortest and len(current) + 1 > len(topK[0]):
      return topK
    neighbors = list(graph[current[len(current) - 1]].keys())
    random.shuffle(neighbors)

    # Skip neighbors already in the partial path to avoid loops
    for i in range(len(neighbors)):
      # if i not in current :
      #   for j in range(len(current)) :
      #     if current[j] == i :
      #       print("U DUMB")
      if neighbors[i] in current:
      # if i in current :
        continue
      new_current = list(current)
      new_current.append(neighbors[i])

      if neighbors[i] == target:
        topK.append(new_current)
        if len(new_current) > len(topK[0]) or len(topK) >= 64:
          doneWithECMP = True
      else:
        candidates.append(new_current)
  # for k in range(len(topK)) :
  #   for i in range(len(topK[k])) :
  #     for j in range(len(topK[k])) :
  #       if i == j :
  #         continue
  #       if topK[k][i] == topK[k][j] :
  #           print("SANITY FAILED")
  #           print(topK[k])
  return topK


ecmp8_routing = {}
ecmp64_routing = {}
kshortest_routing = {}

kshortest_routing_paths = {} #for sanity check

def find_next_hop(path, me_id) :
  end = len(path)
  # for i in range(end, -1, -1) :
  for i in range(end) :
    rev_i = (end - 1) - i
    if me_id == path[rev_i] :
      if rev_i == (end - 1) :
        return me_id #we are last hop - go to host
      else :
        return path[rev_i + 1] #next hop
  return -1 #we're not on this path...

def find_next_hops_in_paths(paths, me_id) :
  options = []
  for path in paths : 
    next_hop = find_next_hop(path, me_id)
    if next_hop != -1 :
      options.append(next_hop)
  return options

def routing_options(paths) :
  route_options_by_id = {}
  for i in range(numServers) :
    options = find_next_hops_in_paths(paths, i)
    if len(options) != 0 :    #if want sanity check with single option, can just pull out option[0] (THOUGH CHANGE BACK AFTER)
      route_options_by_id[i] = options #if no options, not reach here, which is fine because we'll never use
  return route_options_by_id

def next_hop_map(path) :
  next_hop_map = {}
  for i in range(len(path)-1) :
    next_hop_map[path[i]] = path[i+1]
  next_hop_map[path[len(path)-1]] = path[len(path)-1] #jump to our host
  return next_hop_map

def routing_next_hop_maps(paths) :
  routing_next_hop_maps = []
  for path in paths :
    routing_next_hop_maps.append(next_hop_map(path))
  return (routing_next_hop_maps, len(paths)) #tuple of options & len (len so we can avoid computing it when forwarding packets)


for source in range(numServers) :
  ecmp8_routing[source] = {}
  ecmp64_routing[source] = {}
  kshortest_routing[source] = {}
  kshortest_routing_paths[source] = {}
  for destination in range(numServers) :
    if destination == source :
      continue
    ecmp8_paths = []
    ecmp64_paths = []
    kshortest_paths = []
    paths = BFS(source, destination)
    if len(paths) == 0:
      print "Graph is not fully connected"
      continue
    minLen = len(paths[0])
    kShortestUpperBound = min(kShortest, len(paths))
    for i in range(0, kShortestUpperBound):
      currentPath = paths[i]
      kshortest_paths.append(list(currentPath)) ##MEEEEE SANITY CHECK ITTTTT##
      if len(currentPath) == minLen:
        ecmp64_paths.append(list(currentPath)) ##MEEEEE SANITY CHECK ITTTTT##
        ecmp8_paths.append(list(currentPath)) ##MEEEEE SANITY CHECK ITTTTT##
    if len(paths) > kShortest:
      for i in range(kShortest, len(paths)):
        currentPath = paths[i]
        if len(currentPath) > minLen:
          break
        ecmp64_paths.append(list(currentPath)) ##MEEEEE SANITY CHECK ITTTTT##
    ecmp8_routing[source][destination] = routing_next_hop_maps(ecmp8_paths)
    ecmp64_routing[source][destination] = routing_next_hop_maps(ecmp64_paths)
    kshortest_routing[source][destination] = routing_next_hop_maps(kshortest_paths)
    # ecmp8_routing[source][destination] = routing_options(ecmp8_paths)
    # ecmp64_routing[source][destination] = routing_options(ecmp64_paths)
    # kshortest_routing[source][destination] = routing_options(kshortest_paths)
    kshortest_routing_paths[source][destination] = kshortest_paths

# print(ecmp8_routing[1][2][5])
# print('print everything!!!')
# # print(ecmp8_routing[3][3])
# for i in range(numServers) :
#   for j in range(numServers) :
#     if i == j :
#       continue
#     print(ecmp8_routing[i][j])
#     print(kshortest_routing[i][j])


save_obj = [numNodes, degree, neighbors, routing_vanilla, ecmp8_routing, ecmp64_routing, kshortest_routing, kshortest_routing_paths, kShortest, port_offset, switch_dpid_offset, host_dpid_offset]

with open('../../graph_items.pickle', 'wb') as handle:
  pickle.dump(save_obj, handle, protocol=pickle.HIGHEST_PROTOCOL)















