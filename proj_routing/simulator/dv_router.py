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
    if self.port_table[port] is None:
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
      pass
    elif isinstance(packet, basics.HostDiscoveryPacket):
      if self.port_table[port] is not None:
        self.port_table[port].append(packet.src)
        if self.neighbor_table[packet.src] is None:
          self.neighbor_table[packet.src] = port 
        if self.distance_vectors[packet.src] is None:
          self.distance_vectors[packet.src] = []
          self.distance_vectors[packet.src].append(self.get_latency_for_port(port))
          self.distance_vectors[packet.src].append(packet.dst) # self == packet.dst ?

      # flood packets to neighbors with distance of this new neighbor, except this new neighbor
      for neighbor in self.neighbor_table.keys():
        if neighbor is not packet.src:
          route_packet = RoutePacket(packet.src, self.get_latency_for_destination(packet.src)) # construct route packet with destination your neighbor and latency
          self.send(route_packet, self.neighbor_table[neighbor])
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

  def get_latency_for_destination(destination):
    return self.distance_vectors[destination][0]

  def get_next_hop_for_destination(destination):
    return self.distance_vectors[destination][1]

  def get_latency_for_port(port):
    return self.port_table[port][0]

  def get_neighbor_for_port(port):
    return self.port_table[port][1]
