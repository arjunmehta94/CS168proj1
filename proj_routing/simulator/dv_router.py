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
  DEFAULT_TIMER_INTERVAL = 20 # Can override this yourself for testing
  
  def __init__ (self):
    """
    Called when the instance is initialized.

    You probably want to do some additional initialization here.
    """
    self.start_timer() # Starts calling handle_timer() at correct rate
    super(DVRouter, self).__init__()
    self.port_table = {} # table of ports to neighbors, latencies: {port: (latency, neighbor)}
    #self.neighbor_table = {} # table of neighbors to ports, {neighbor: port}
    self.distance_vectors = {} # table of distances to destination and next hops, {destination: [min_distance, next_hop]}

  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """
    if port not in self.port_table:
      self.port_table[port] = []
      if latency >= 16:
        latency = INFINITY
      self.port_table[port].append(latency)
    route_packet = basics.RoutePacket(self, 0)
    self.send(route_packet, port)

  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """
    neighbor = self.get_neighbor_for_port(port)
    for destination in self.distance_vectors.keys():
      if destination is neighbor or self.get_next_hop_for_destination(destination) is neighbor:
        del self.distance_vectors[destination]
        del self.port_table[port]
        route_packet = basics.RoutePacket(destination, INFINITY)
        self.send(route_packet, port, True)


  def handle_rx (self, packet, port):
    """
    Called by the framework when this Entity receives a packet.

    packet is a Packet (or subclass).
    port is the port number it arrived on.

    You definitely want to fill this in.
    """
    #self.log("RX %s on %s (%s)", packet, port, api.current_time())
    current_time = api.current_time()
    if isinstance(packet, basics.RoutePacket):
      if packet.destination is self:
        if packet.src in self.distance_vectors:
          self.set_latency_in_distance_vectors(packet.src, packet.latency)
          self.set_current_time_in_distance_vectors(packet.src, current_time)
      else:
        if packet.destination not in self.distance_vectors:
          if packet.latency == 0: #coming from a neighbor
            self.add_to_distance_vectors(packet.destination, self.get_latency_for_port(port), self, current_time)
            self.port_table[port].append(packet.destination)
          else:
            self.add_to_distance_vectors(packet.destination, self.get_latency_for_port(port) + packet.latency, packet.src, current_time)

          # print str(self) + "reached here"
          # print str(self.distance_vectors)
          # print str(packet.src)
          # packet_not_in_neighbor_table = packet.src not in self.neighbor_table
          # if packet_not_in_neighbor_table:
          #   self.neighbor_table[packet.src] = port
          #   self.add_to_distance_vectors(packet.destination, self.get_latency_for_port(port), self, current_time)
          distance = self.get_latency_for_destination(packet.destination)
          if distance >= 16:
            distance = INFINITY
            del self.distance_vectors[packet.destination] #self.set_latency_in_distance_vectors(packet.destination, distance)
          #self.flood_packet(packet, packet.destination) # should we flood if latency is INFINITY
          route_packet = basics.RoutePacket(packet.destination, distance)
          self.send(route_packet, port, True)
        else:
          curr_latency = self.get_latency_for_destination(packet.destination)
          if curr_latency > self.get_latency_for_port(port) + packet.latency:
            curr_latency = self.get_latency_for_port(port) + packet.latency
            if curr_latency >= 16:
              curr_latency = INFINITY
              del self.distance_vectors[packet.destination]
            else:
              self.set_latency_in_distance_vectors(packet.destination, curr_latency)
              self.set_next_hop_in_distance_vectors(packet.destination, packet.src)
            
            #self.flood_packet(packet, packet.destination)
            route_packet = basics.RoutePacket(packet.destination, curr_latency)
            self.send(route_packet, port, True)
          self.set_current_time_in_distance_vectors(packet.destination, current_time)
      
    elif isinstance(packet, basics.HostDiscoveryPacket):
      # print "i'm here"
      if port in self.port_table:
        #self.port_table[port].append(packet.src)
        # if packet.src not in self.neighbor_table:
        #   self.neighbor_table[packet.src] = port 
        if packet.src not in self.distance_vectors:
          self.add_to_distance_vectors(packet.src, self.get_latency_for_port(port), self, current_time)# self == packet.dst ?
          self.port_table[port].append(packet.src)

      # flood packets to neighbors with distance of this new neighbor, except this new neighbor
      #self.flood_packet(packet, packet.src)
      route_packet = basics.RoutePacket(packet.src, self.get_latency_for_destination(packet.src))
      self.send(route_packet, port, True)
    #else:
      # Totally wrong behavior for the sake of demonstration only: send
      # the packet back to where it came from!
      #self.send(packet, port=port)

  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    #print "timer has been called"
   
    for destination in self.distance_vectors.keys():
      current_time = api.current_time()
      #if self.get_latency_for_destination(destination) == INFINITY --> Check to see if infinite distance destination exists in table?
      
      distance = self.get_latency_for_destination(destination)
      #print(current_time - self.get_current_time_for_destination(destination))
      if (current_time - self.get_current_time_for_destination(destination)) > 15.0:
        #print "updating to infinity"
        distance = INFINITY
        del self.distance_vectors[destination]
        #self.set_latency_in_distance_vectors(destination, INFINITY)
      route_packet = basics.RoutePacket(destination, distance)
      self.send(route_packet, None, True)
      # for neighbor in self.neighbor_table.keys():
      #   if isinstance(neighbor, DVRouter):
      #     route_packet = basics.RoutePacket(destination, self.get_latency_for_destination(destination))
      #     self.send(route_packet, self.neighbor_table[neighbor])

  def flood_packet(self, packet, destination):
    print str(self.neighbor_table.keys())
    for neighbor in self.neighbor_table.keys():
        if isinstance(neighbor, DVRouter): #neighbor is not packet.src: # and :
          # print str(packet.src) + ' packet.src'
          # print str(neighbor) + ' neighbor'
          route_packet = basics.RoutePacket(destination, self.get_latency_for_destination(destination)) # construct route packet with destination destination and latency for that destination
          self.send(route_packet, self.neighbor_table[neighbor])

  def set_latency_in_distance_vectors(self, destination, latency):
    self.distance_vectors[destination][0] = latency

  def set_next_hop_in_distance_vectors(self, destination, next_hop):
    self.distance_vectors[destination][1] = next_hop

  def set_current_time_in_distance_vectors(self, destination, current_time):
    self.distance_vectors[destination][2] = current_time

  def add_to_distance_vectors(self, destination, latency, next_hop, current_time):
    self.distance_vectors[destination] = []
    self.distance_vectors[destination].append(latency)
    self.distance_vectors[destination].append(next_hop)
    self.distance_vectors[destination].append(current_time)

  def get_current_time_for_destination(self, destination):
    if destination in self.distance_vectors:
      return self.distance_vectors[destination][2]
    return None

  def get_latency_for_destination(self, destination):
    if destination in self.distance_vectors:
      return self.distance_vectors[destination][0]
    return None

  def get_next_hop_for_destination(self, destination):
    if destination in self.distance_vectors:
      return self.distance_vectors[destination][1]
    return None

  def get_latency_for_port(self, port):
    if port in self.port_table:
      return self.port_table[port][0]
    return None

  def get_neighbor_for_port(self, port):
    if port in self.port_table: 
      return self.port_table[port][1]
    return None
