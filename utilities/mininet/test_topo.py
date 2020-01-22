import argparse

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSSwitch
from p4rtovs_mininet import P4rtOVSSwitch


class TestTopo(Topo):

    def __init__(self, *args, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        s1 = self.addSwitch('s1', datapath = 'user')

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        self.addLink(h1, s1)
        self.addLink(h2, s1)

# def createSwitch(program=None):
#     """ Helper class that is called by Mininet to initialize
#         the virtual P4rt-OVS switches. The purpose is to load
#         arbitrary P4 program .
#     """
#     if not program:
#         return OVSSwitch
#
#     switch


def program_switches(switches, program):
    """ Helper class that is called by Mininet to initialize
        the virtual P4rt-OVS switches. The purpose is to load
        the P4 program to every switch in network.
    """
    for sw in switches:
        print "Loading P4 program to switch %s" % str(sw)
        sw.load_program(1, program)


def main(program):
    topo = TestTopo()

    net = Mininet(topo = topo,
                  switch = P4rtOVSSwitch,
                  controller = None)

    net.start()

    if program:
        program_switches(net.switches, program)

    CLI( net )
    net.stop()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--program', help="Path to P4 program to be installed in every switch.",
                        required=False)
    return parser.parse_args()


if __name__ == '__main__':
    setLogLevel( 'info' )

    args = get_args()
    main(args.program)
