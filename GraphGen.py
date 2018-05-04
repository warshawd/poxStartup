import networkx
import random
import Queue


numPorts = 12 # k in the paper
switchPorts = 8 # r in the paper, also the degree
serverPorts = numPorts - switchPorts # k-r in the paper, also the number of servers per switch

numServers = 686
numSwitches = numServers / serverPorts
degree = switchPorts
kShortest = 8

sources = [i for i in range(numServers)]
targets = [-1 for i in range(numServers)]
unused = set(sources)
serversToSwitches = {}
for server in range(numServers):
  switch = 0
  for i in range(serverPorts):
    serversToSwitches[server] = switch
  switch += 1

kShortestCounts = {}
ECMP8Counts = {}
ECMP64Counts = {}

redo = False
first = True


def BFS(source, target):
  source = serversToSwitches[source]
  target = serversToSwitches[target]
  topK = []
  candidates = []
  candidates.append([source])
  while len(topK) < kShortest and len(candidates) > 0:
    current = candidates.pop(0)
    if len(topK) >= kShortest and len(current) + 1 > len(topk[0]):
      return topK
    neighbors = list(graph[current[len(current) - 1]].keys())
    random.shuffle(neighbors)
    for i in range(len(neighbors)):
      if i in current:
        continue
      new_current = list(current)
      new_current.append(neighbors[i])

      if neighbors[i] == target:
        topK.append(new_current)
      else:
        candidates.append(new_current)


  return topK

# Generate the random traffic permutation
while first or redo:
  first = False
  for source in range(len(sources)):
    target = source
    while target == source:
      target = random.sample(unused, 1)[0]
      if target == source and len(unused) == 1:
        break
    if (target == source):
      redo = True
    else:
      targets[source] = target
      unused.remove(target)

# Generate the random graph
graph = networkx.random_regular_graph(degree, numSwitches)

# Initialize the link counts
for edge in graph.edges():
  kShortestCounts[edge] = 0
  kShortestCounts[tuple([edge[1], edge[0]])] = 0
  ECMP8Counts[edge] = 0
  ECMP8Counts[tuple([edge[1], edge[0]])] = 0
  ECMP64Counts[edge] = 0
  ECMP64Counts[tuple([edge[1], edge[0]])] = 0

# Start computing shortest paths
for source in range(len(sources)):
  target = targets[source]
  print "Starting k shortest for path " + str(source)
  paths = BFS(source, target)
  print "Length of path vector is " + str(len(paths))
  if len(paths) == 0:
    continue
  minLen = len(paths[0])
  upperBound = min(kShortest, len(paths))
  for i in range(0, upperBound):
    current = paths[i]
    for j in range(len(current) - 1):
      link = tuple([current[j], current[j+1]])
      kShortestCounts[link] += 1
      if kShortestCounts[link] > 100:
        print link
      if (len(current) == minLen):
        ECMP8Counts[link] += 1
        ECMP64Counts[link] += 1
  for i in range(kShortest, len(paths)):
    current = paths[i]
    if len(current) > minLen:
      break
    for j in range(len(current) - 1):
      link = tuple([current[j], current[j+1]])
      ECMP64Counts[link] += 1


kShortestBuckets = [0 for i in range(1000)]
ECMP8Buckets = [0 for i in range(1000)]
ECMP64Buckets = [0 for i in range(1000)]
for key, value in kShortestCounts.items() :
  kShortestBuckets[value] += 1

for key, value in ECMP8Counts.items() :
  ECMP8Buckets[value] += 1

for key, value in ECMP64Counts.items() :
  ECMP64Buckets[value] += 1

for i in range(len(kShortestBuckets)):
  if kShortestBuckets[i] == 0:
    continue
  print "k-Shortest: Num on " + str(i) + " paths: " + str(kShortestBuckets[i])

print "\n"

for i in range(len(ECMP8Buckets)):
  if ECMP8Buckets[i] == 0:
    continue
  print "ECMP-8: Num on " + str(i) + " paths: " + str(ECMP8Buckets[i])

print "\n"

for i in range(len(ECMP64Buckets)):
  if ECMP64Buckets[i] == 0:
    continue
  print "ECMP-64: Num on " + str(i) + " paths: " + str(ECMP64Buckets[i])
