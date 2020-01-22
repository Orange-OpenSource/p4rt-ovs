from mininet.net import Mininet
from mininet.node import OVSSwitch

class P4rtOVSSwitch(OVSSwitch):
    """P4rt-OVS virtual switch based on Open vSwitch."""

    def __init__(self, *args, **kwargs):
        kwargs.update( datapath='user' )
        OVSSwitch.__init__( self, *args, **kwargs )

    def load_program(self, id, program):
        self.dpctl('load-bpf-prog', str(id), program)