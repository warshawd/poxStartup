import pickle
import networkx

# numNodes, degree, graph, port_offset, switch_dpid_offset, host_dpid_offset

with open('graph_items.pickle', 'rb') as handle:
  # graph_items = pickle.load(handle)

  # print graph_items

  numNodes, degree, neighbors, routing, port_offset, switch_dpid_offset, host_dpid_offset = pickle.load(handle)

  print degree
  print numNodes
  print neighbors
  print routing
  print port_offset
  print switch_dpid_offset
  print host_dpid_offset