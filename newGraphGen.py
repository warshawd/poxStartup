import networkx
import random
import Queue
import pickle


explore = False
debug = False

bestTotalPort = 10
bestSwitchPort = 8


for totalPortSelect in range(6, 20):
  for switchPortSelect in range(4, totalPortSelect):

    if not explore:
      if totalPortSelect != bestTotalPort or switchPortSelect != bestSwitchPort:
        continue

    if (totalPortSelect == switchPortSelect):
      continue




    numPorts = totalPortSelect # k in the paper
    toSwitchPorts = switchPortSelect # r in the paper, also implicitly the degree
    degree = toSwitchPorts
    toServerPorts = numPorts - toSwitchPorts # k-r in the paper, also the number of servers per switch

    numServers = 686
    numSwitches = numServers / toServerPorts
    if numServers % toServerPorts != 0:
      numSwitches += 1

    if (degree * numSwitches) % 2 != 0:
      continue

    kShortest = 8

    sourceServers = [i for i in range(numServers)]
    targetServers = [-1 for i in range(numServers)]
    serversToSwitches = {}

    for server in range(numServers):
      serversToSwitches[server] = server / toServerPorts


    kShortestCounts = {}
    ECMP8Counts = {}
    ECMP64Counts = {}

    redo = False
    first = True


    def BFS(sourceSwitch, targetSwitch):
      source = sourceSwitch
      target = targetSwitch
      topK = []
      candidates = []
      candidates.append([source])
      doneWithECMP = False
      while (len(topK) < kShortest or not doneWithECMP) and len(candidates) > 0 and len(candidates) < 20000:
        current = candidates.pop(0)
        if len(topK) >= kShortest and len(current) + 1 > len(topK[0]):
          return topK
        neighbors = list(graph[current[len(current) - 1]].keys())
        random.shuffle(neighbors)

        # Skip neighbors already in the partial path to avoid loops
        for i in range(len(neighbors)):
          if neighbors[i] in current:
            continue
          new_current = list(current)
          new_current.append(neighbors[i])

          if neighbors[i] == target:
            topK.append(new_current)
            if len(new_current) > len(topK[0]) or len(topK) >= 64:
              doneWithECMP = True
          else:
            candidates.append(new_current)

      return topK


    # Generate the random traffic permutation
    print "Generating random traffic permutation"
    while first or redo:
      unused = set(sourceServers)
      first = False
      for source in range(len(sourceServers)):
        target = source
        while target == source:
          target = random.sample(unused, 1)[0]
          if target == source and len(unused) == 1:
            break
        if (target == source):
          redo = True
          if debug:
            print "Had to restart the graph gen"
          break;
        else:
          targetServers[source] = target
          unused.remove(target)

    # Generate the degree regular random graph
    graph = networkx.random_regular_graph(degree, numSwitches)

    # Initialize the link counts
    for edge in graph.edges():
      kShortestCounts[tuple([edge[0], edge[1]])] = 0
      kShortestCounts[tuple([edge[1], edge[0]])] = 0
      ECMP8Counts[tuple([edge[0], edge[1]])] = 0
      ECMP8Counts[tuple([edge[1], edge[0]])] = 0
      ECMP64Counts[tuple([edge[0], edge[1]])] = 0
      ECMP64Counts[tuple([edge[1], edge[0]])] = 0

    # Start computing the shortest paths
    print "Computing shortest paths for k = " + str(totalPortSelect) + " and r = " + str(switchPortSelect) + "..."
    for sourceServer in range(len(sourceServers)):
      if sourceServer % 100 == 0:
        print "Computing path for server " + str(sourceServer)
      source = serversToSwitches[sourceServer]
      targetServer = targetServers[sourceServer]
      target = serversToSwitches[targetServer]
      if source == target:
        if debug:
          print "Sending to a server on the same rack"
        continue
      if debug:
        print "Starting k shortest for path " + str(source)
      paths = BFS(source, target)
      if debug:
        print "Length of path vector is " + str(len(paths))
      if len(paths) == 0:
        print "Graph is not fully connected"
        continue
      minLen = len(paths[0])
      kShortestUpperBound = min(kShortest, len(paths))
      for i in range(0, kShortestUpperBound):
        currentPath = paths[i]
        for j in range(len(currentPath) - 1):
          link = tuple([currentPath[j], currentPath[j+1]])
          kShortestCounts[link] += 1
          if debug:
            if kShortestCounts[link] > 100:
              print "Link " + link + " is greater than 100"
          if len(currentPath) == minLen:
            ECMP8Counts[link] += 1
            ECMP64Counts[link] += 1
      if len(paths) > kShortest:
        for i in range(kShortest, len(paths)):
          currentPath = paths[i]
          if len(currentPath) > minLen:
            break
          for j in range(len(currentPath) - 1):
            link = tuple([currentPath[j], currentPath[j+1]])
            ECMP64Counts[link] += 1

    print "Done computing shortest paths"

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
      if debug:
        if i > 80:
          print "Testing"
          for key, value in kShortestCounts.items():
            if value == i:
              print "Link in question was " + str(key)

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

    buckets = [kShortestBuckets, ECMP8Buckets, ECMP64Buckets]

    with open('k' + str(totalPortSelect) + 'r' + str(switchPortSelect) + '.pickle', 'wb') as handle:
      pickle.dump(buckets, handle, protocol=pickle.HIGHEST_PROTOCOL)