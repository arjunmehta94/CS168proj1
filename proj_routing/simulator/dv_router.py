"""
Your awesome Distance Vector router for CS 168
"""

import sim.api as api
import sim.basics as basics


# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter (basics.DVRouterBase):
  #NO_LOG = True # Set to True on an instance to disable its logging
  #POISON_MODE = True # Can override POISON_MODE here
  #DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

  def __init__ (self):
    """
    Called when the instance is initialized.

    You probably want to do some additional initialization here.
    """
    self.start_timer() # Starts calling handle_timer() at correct rate
    super(DVRouter, self).__init__()
    self.port_table = {} # table of ports to neighbors, latencies: {port: (latency, neighbor)}
    self.neighbor_table = {} # table of neighbors to ports, {neighbor: port}
    self.distance_vectors = {} # table of distances to destination and next hops, {destination: [min_distance, next_hop]}

  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """
    if port not in self.port_table:
      self.port_table[port] = []
      self.port_table[port].append(latency)

  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """

  def handle_rx (self, packet, port):
    """
    Called by the framework when this Entity receives a packet.

    packet is a Packet (or subclass).
    port is the port number it arrived on.

    You definitely want to fill this in.
    """
    #self.log("RX %s on %s (%s)", packet, port, api.current_time())
    if isinstance(packet, basics.RoutePacket):
      if packet.destination not in self.distance_vectors:
        self.add_to_distance_vectors(packet.destination, self.get_latency_for_destination(packet.src) + packet.latency, packet.src)
        flood_packet(packet, packet.destination)
      else:
        curr_latency = self.get_latency_for_destination(packet.destination)
        if curr_latency > self.get_latency_for_destination(packet.src) + packet.latency:
          curr_latency = self.get_latency_for_destination(packet.src) + packet.latency
          self.set_latency_in_distance_vectors(packet.destination, curr_latency)
          self.set_next_hop_in_distance_vectors(packet.destination, packet.src)
          flood_packet(packet, packet.destination)
      
    elif isinstance(packet, basics.HostDiscoveryPacket):
      if port in self.port_table:
        self.port_table[port].append(packet.src)
        if packet.src not in self.neighbor_table:
          self.neighbor_table[packet.src] = port 
        if packet.src not in self.distance_vectors:
          self.add_to_distance_vectors(packet.src, self.get_latency_for_port(port), packet.dst)# self == packet.dst ?

      # flood packets to neighbors with distance of this new neighbor, except this new neighbor
      flood_packet(packet, packet.src)
    else:
      # Totally wrong behavior for the sake of demonstration only: send
      # the packet back to where it came from!
      self.send(packet, port=port)

  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
  
  def flood_packet(packet, destination):
    for neighbor in self.neighbor_table.keys():
        if neighbor is not packet.src:
          route_packet = RoutePacket(destination, self.get_latency_for_destination(destination)) # construct route packet with destination destination and latency for that destination
          self.send(route_packet, self.neighbor_table[neighbor])

  def set_latency_in_distance_vectors(destination, latency):
    self.distance_vectors[destination][0] = latency

  def set_next_hop_in_distance_vectors(destination, next_hop):
    self.distance_vectors[destination][1] = next_hop

  def add_to_distance_vectors(destination, latency, next_hop):
    self.distance_vectors[destination] = []
    self.distance_vectors.append(latency)
    self.distance_vectors.append(next_hop)

  def get_latency_for_destination(destination):
    return self.distance_vectors[destination][0]

  def get_next_hop_for_destination(destination):
    return self.distance_vectors[destination][1]

  def get_latency_for_port(port):
    return self.port_table[port][0]

  def get_neighbor_for_port(port):
    return self.port_table[port][1]
