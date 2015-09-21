"""
Your learning switch warm-up exercise for CS-168

Start it up with a commandline like...

  ./simulator.py --default-switch-type=learning_switch topos.rand --links=0
"""

import sim.api as api
import sim.basics as basics


class LearningSwitch (api.Entity):
  """
  A learning switch

  Looks at source addresses to learn where endpoints are.  When it doesn't
  know where the destination endpoint is, floods.

  This will surely have problems with topologies that have loops!  If only
  someone would invent a helpful poem for solving that problem...
  """

  def __init__ (self):
    """
    Do some initialization

    You probablty want to do something in this method.
    """
    super(LearningSwitch, self).__init__()
    self.forwarding_table = {} #forwarding table for this learning switch
    self.port_table = {} #contains a list of all sources connected to a port

  def handle_port_down (self, port):
    """
    Called when a port goes down (because a link is removed)

    You probably want to remove table entries which are no longer valid here.
    """
    lst_of_entities = self.port_table[port]
    for entity in lst_of_entities:
      del self.forwarding_table[entity]
    del self.port_table[port]

  def handle_rx (self, packet, in_port):
    """
    Called when a packet is received

    You most certainly want to process packets here, learning where they're
    from, and either forwarding them toward the destination or flooding them.
    """

    # The source of the packet can obviously be reached via the input port, so
    # we should "learn" that the source host is out that port.  If we later see
    # a packet with that host as the *destination*, we know where to send it!
    # But it's up to you to implement that.  For now, we just implement a
    # simple hub.
    if isinstance(packet, basics.HostDiscoveryPacket):
      # Don't forward discovery messages
      return 
    if packet.ttl <= 0:
      return;  
    packet.ttl -= 1 # reduce ttl count
    src = packet.src
    dst = packet.dst

    # check if src is in forwarding table, if not, add it. Also update port table.
    if src not in self.forwarding_table: 
      self.forwarding_table[src] = in_port
      if in_port not in self.port_table:
        self.port_table[in_port] = []
      self.port_table[in_port].append(src)

    #check if dst is in forwarding table, if it is, send it to that port, else flood
    if dst in self.forwarding_table:
      self.send(packet, self.forwarding_table[dst])
    else:
      # Flood out all ports except the input port
      self.send(packet, in_port, flood=True)

    
