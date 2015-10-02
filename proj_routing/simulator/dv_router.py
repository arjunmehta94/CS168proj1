"""
Your awesome Distance Vector router for CS 168
"""

import sim.api as api
import sim.basics as basics


# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter (basics.DVRouterBase):
  #NO_LOG = True # Set to True on an instance to disable its logging
  POISON_MODE = True # Can override POISON_MODE here
  DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

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
      if not latency >= INFINITY and not latency < 0:
        self.port_table[port] = latency
        ## update neighbor as soon as link is established
        for destination in self.distance_vectors:
          route_packet = basics.RoutePacket(destination, self.distance_vectors[destination][0])
          self.send(route_packet, port)

  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """
    keys_to_delete = []
    if port in self.port_table:
      del self.port_table[port]
      for key, value in self.distance_vectors.iteritems():
        if value[1] is port:
          if self.POISON_MODE:
            route_packet = basics.RoutePacket(key, INFINITY)
            self.send(route_packet, port, True)
          keys_to_delete.append(key)
      for key in keys_to_delete:
        del self.distance_vectors[key]

        # TO BE IMPLEMENTED FOR POISON MODE
        ####################################
        # route_packet = basics.RoutePacket(key, INFINITY)
        # self.send(route_packet, port, True)

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
      #if packet.latency == INFINITY and self.POISON_MODE:
        #print("infinity seen")
      if port in self.port_table:
        # print self.port_table[port]
        # print packet.latency 
        if packet.latency == INFINITY:
          if self.POISON_MODE:
            if port == self.distance_vectors[packet.destination][1]:
              del self.distance_vectors[packet.destination]

          ## read https://en.wikipedia.org/wiki/Split_horizon_route_advertisement which says that 
          ## when a router receives -1, it should send it back to the originator with -1.


          # route_packet = basics.RoutePacket(packet.destination, -1)
          # self.send(route_packet, port, True)
          return
        distance = packet.latency + self.port_table[port]
        if not distance > INFINITY:
          if packet.latency < INFINITY and distance == INFINITY:
            routepkt = basics.RoutePacket(packet.destination,INFINITY)
            self.send(routepkt,port,True)
            return

          if packet.destination not in self.distance_vectors:
            self.distance_vectors[packet.destination] = []
            self.distance_vectors[packet.destination].append(distance)
            self.distance_vectors[packet.destination].append(port)
            self.distance_vectors[packet.destination].append(current_time)
            self.distance_vectors[packet.destination].append(False)
            
            if self.POISON_MODE:
              ports = self.port_table.keys()
              route_packet = basics.RoutePacket(packet.destination, INFINITY)
              self.send(route_packet, port)
              ports.remove(port)
              route_packet = basics.RoutePacket(packet.destination, distance)
              self.send(route_packet, ports)
            else:
              route_packet = basics.RoutePacket(packet.destination, distance)
              self.send(route_packet, port, True)
          else:

            # if current_time - self.distance_vectors[packet.destination][2] > 15 and not self.distance_vectors[packet.destination][3]:
            #   #print str(self) + str(destination)
            #   del self.distance_vectors[packet.destination]
            #else:

            curr_distance = self.distance_vectors[packet.destination][0]
            portNum = self.distance_vectors[packet.destination][1]
            if curr_distance != distance:
              if portNum == port:
                curr_distance = distance
                self.distance_vectors[packet.destination][0] = curr_distance
                self.distance_vectors[packet.destination][1] = port
                self.distance_vectors[packet.destination][2] = current_time
                self.distance_vectors[packet.destination][3] = False
                if self.POISON_MODE:
                  ports = self.port_table.keys()
                  route_packet = basics.RoutePacket(packet.destination, INFINITY)
                  self.send(route_packet, port)
                  ports.remove(port)
                  route_packet = basics.RoutePacket(packet.destination, curr_distance)
                  self.send(route_packet, ports)
                else:
                  route_packet = basics.RoutePacket(packet.destination, curr_distance)
                  self.send(route_packet, port, True)
              else:
                if distance < curr_distance:
                  curr_distance = distance
                  self.distance_vectors[packet.destination][0] = curr_distance
                  self.distance_vectors[packet.destination][1] = port
                  self.distance_vectors[packet.destination][2] = current_time
                  self.distance_vectors[packet.destination][3] = False
                  if self.POISON_MODE:
                    ports = self.port_table.keys()
                    route_packet = basics.RoutePacket(packet.destination, INFINITY)
                    self.send(route_packet, port)
                    ports.remove(port)
                    route_packet = basics.RoutePacket(packet.destination, curr_distance)
                    self.send(route_packet, ports)
                  else:
                    route_packet = basics.RoutePacket(packet.destination, curr_distance)
                    self.send(route_packet, port, True)
            elif curr_distance == distance:
              if port is not self.distance_vectors[packet.destination][1]:
                self.distance_vectors[packet.destination][1] = port
                if self.POISON_MODE:
                  route_packet = basics.RoutePacket(packet.destination, INFINITY)
                  self.send(route_packet, port)
              self.distance_vectors[packet.destination][2] = current_time
            # stored distance should never be infinity

            # POISON MODE IMPLEMENTATION
            # check if distance is actually infinite and delete that from your table
            
    elif isinstance(packet, basics.HostDiscoveryPacket):
      if port in self.port_table:
        self.distance_vectors[packet.src] = []
        self.distance_vectors[packet.src].append(self.port_table[port])
        self.distance_vectors[packet.src].append(port)
        self.distance_vectors[packet.src].append(current_time)
        self.distance_vectors[packet.src].append(True)
        route_packet = basics.RoutePacket(packet.src, self.port_table[port])
        self.send(route_packet, port, True)
    else:
      # Totally wrong behavior for the sake of demonstration only: send
      # the packet back to where it came from!
      #self.send(packet, port=port)
      if packet.dst in self.distance_vectors:
        outport = self.distance_vectors[packet.dst][1]
        if outport != port:
          self.send(packet, outport)

  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    current_time = api.current_time()
    keys_to_delete = []
    for destination in self.distance_vectors:
      if (current_time - self.distance_vectors[destination][2] > 15 and not self.distance_vectors[destination][3]): # or self.distance_vectors[destination][0] >= INFINITY:
        keys_to_delete.append(destination)
      else:
        #print destination

        ## not sending to port who we got the information from, before, we were doing that.
        if self.POISON_MODE:
          port = self.distance_vectors[destination][1]
          ports = self.port_table.keys()
          route_packet = basics.RoutePacket(destination, INFINITY)
          self.send(route_packet, port)
          ports.remove(port)
          route_packet = basics.RoutePacket(destination, self.distance_vectors[destination][0])
          self.send(route_packet, ports)
        else:
          port = self.distance_vectors[destination][1]
          route_packet = basics.RoutePacket(destination, self.distance_vectors[destination][0])
          self.send(route_packet, port, True)
    for key in keys_to_delete:
       #print "deleting"
       del self.distance_vectors[key]
        ## IMPLEMENT POISON REVERSE, BROAD
      

  def get_latency_for_destination(destination):
    return self.distance_vectors[destination][0]

  def get_next_hop_for_destination(destination):
    return self.distance_vectors[destination][1]

  def get_latency_for_port(port):
    return self.port_table[port][0]

  def get_neighbor_for_port(port):
    return self.port_table[port][1]
