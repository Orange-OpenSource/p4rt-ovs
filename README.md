P4rt-OVS: Programming Protocol-Independent, Runtime Extensions for Open vSwitch using P4
----------------------------------------------------------------------------------------

## Table of contents
1. [Overview](#overview)
2. [Getting started](#getting-started)
    - [How to install?](#how-to-install?)
    - [How to use?](#how-to-use?)
3. [Contributing](#contributing)
4. [License](#license)
5. [Contacts](#contacts)
6. [Acknowledgment](#acknowledgment)

The original Open vSwitch README is available at [README-original.rst](./README-original.rst).

# Overview

[Open vSwitch](https://www.openvswitch.org/) (OVS) is a widely adopted high-performance programmable virtual switch. 
P4rt-OVS is an extension of Open vSwitch that integrates the BPF virtual machine with the userspace datapath of OVS. 
Hence, P4rt-OVS allows to extend the OVS packet processing pipeline without recompilation by
injecting BPF programs at runtime. BPF programs act as programmable actions and they are referenced as a new OVS action (`prog`) in the OpenFlow tables.
Programmable actions are allowed to write to packets as well as read and write to persistent maps (hash tables) to retain information on flows.

Furthermore, a user can use [the P4 language](https://p4.org/) to develop new, protocol-independent data plane extensions (BPF programs) for Open vSwitch. 
P4 provides a high-level and declarative language, so writing a new network features becomes super easy! [p4c-ubpf](https://github.com/p4lang/p4c/pull/2134), the uBPF back-end for the P4 compiler, provides 
the architecture model to write P4 programs making use of wide range of P4 features including stateful registers.

P4rt-OVS is based on Open vSwitch v2.13 and relies on a modified version of [the ubpf project](https://github.com/iovisor/ubpf)
to execute BPF programs.

P4rt-OVS was presented during Open vSwitch and OVN Fall 2019 Conference. [ [link](https://www.openvswitch.org/support/ovscon2019/#s4.3F) ]

# Getting started


## Prerequisites

* `clang-6.0` installed to compile from C to BPF. 

## How to install?

P4rt-OVS works only with the userspace datapath of OVS. Currently, there are two implementations
of userspace datapath: DPDK and AF_XDP. We tested P4rt-OVS with both solutions. However, we recommend AF_XDP as a more
lightweight solution.

### DPDK

To install P4rt-OVS on top of DPDK, you can follow the usual [guidelines to install Open
vSwitch-DPDK](./Documentation/intro/install/dpdk.rst). No additional dependencies are required.

### AF_XDP

Running OVS on top of DPDK requires some configuration effort. Additionally, DPDK is not integrated with `veth` interfaces.

The easiest and fastest way to test P4rt-OVS (without environment's preparation and configuration overhead) is to use
AF_XDP interfaces. AF_XDP allows to use `veth` interfaces with our P4rt-OVS, what makes testing really easy.

To install P4rt-OVS on top of AF_XDP, you can follow the usual [guidelines to install Open
vSwitch-AFXDP](./Documentation/intro/install/afxdp.rst). No additional dependencies are required.

### Docker

TBD

## How to use?

P4rt-OVS allows to inject a new data plane program to the OVS packet processing pipeline at runtime.
The process can be decomposed into two phases: Design (programming data plane module in either P4 or C)
and Runtime (using already developed data plane module in Open vSwitch).

### Design phase - Writing data plane extensions

Data plane programs for P4rt-OVS can be created in P4 or C. We recommend the former as writing data plane programs
in P4 is easier and less error-prone.

#### P4 (the recommended way)

P4rt-OVS is well-integrated with the [uBPF back-end for the P4 compiler](https://github.com/p4lang/p4c/pull/2134). We recommend users to
use P4 to develop data plane extensions for Open vSwitch. P4 provides a high-level and declarative
programming language, which makes development much easier than using C.

Firstly, you need to install the `p4c` compiler locally by following [the official guide](https://github.com/p4lang/p4c#getting-started).

**Note!** As `p4c-ubpf` is still under review, you should use [forked `p4c` from the P4-Research repository](https://github.com/P4-Research/p4c) temporarily.

To learn how to write data plane programs for P4rt-OVS in the P4 language refer to the following materials:

* [Introduction to the uBPF back-end for P4c](https://github.com/P4-Research/p4c/blob/master/backends/ubpf/README.md)
* [The ubpf_model.p4 architecture model](https://github.com/P4-Research/p4c/blob/master/backends/ubpf/p4include/ubpf_model.p4)
* [p4c-ubpf examples](https://github.com/P4-Research/p4c/blob/master/backends/ubpf/docs/EXAMPLES.md)

#### C

The data plane extensions for P4rt-OVS can be also developed in the C language. 

To find out how to develop data plane programs for P4rt-OVS in C take a look at [examples](./examples/tunneling).

### Runtime phase - using data plane extensions in OVS

Once a data plane program is ready, we can test it using P4rt-OVS. As P4 is the recommended way to extend the P4rt-OVS
pipeline all below examples assume using P4.

**Note!** We didn't finished the implementation of P4rt-OVS CLI (P4-compatible), 
so that a user has to use the low-level API of Open vSwitch.

The below snippet shows how to configure ports, install the P4 program, invoke P4 program
for the incoming traffic and control the BPF maps that represent Match-Action tables of the P4 program.

We use [tunneling.p4](https://github.com/P4-Research/p4c/blob/master/backends/ubpf/tests/testdata/test-tunneling.p4) program to show the basic
functionality of P4rt-OVS. The `tunneling.p4` program implements simple MPLS encapsulation and decapsulation.

```bash
# AF_XDP is used in this example. Let's add two veth interfaces as OVS ports.
$ ovs-vsctl add-port br0 peer0 -- set interface peer0 external-ids:iface-id="port0" type="afxdp"
$ ovs-vsctl add-port br0 peer1 -- set interface peer1 external-ids:iface-id="port1" type="afxdp"
$ ovs-vsctl show
e7c40460-0252-4c98-a225-44416c01ead2
  Bridge br0
      datapath_type: netdev
      Port peer1
          Interface peer1
              type: afxdp
      Port br0
          Interface br0
              type: internal
      Port peer0
          Interface peer0
              type: afxdp
# For the demo purpose, tunneling.p4 is used. Compile it from P4 to C.
$ p4c-ubpf -o tunneling.c tunneling.p4
# compile tunneling.c to BPF machine code 
$ clang-6.0 -O2 -target bpf -c tunneling.c -o /tmp/tunneling.o
# Load compiled program to OVS
$ ovs-ofctl load-bpf-prog br0 1 /tmp/tunneling.o
$ ovs-ofctl show-bpf-prog br0 1
NXT_BPF_SHOW_PROG_REPLY (xid=0x4):
The number of BPF programs already loaded: 1
id 2:   loaded_at=2020-02-19 T13:00:52 
    map_ids 0,1
# Setup rules to forward traffic (bidirectional). By default, the BPF program will pass all packets.
$ ovs-ofctl add-flow br0 in_port=2,actions=prog:1,output:1
$ ovs-ofctl add-flow br0 in_port=1,actions=prog:1,output:2
# Install BPF map entry (P4 table entry) to invoke mpls_encap() (value=0) for packets destined to 172.16.0.14 through downstream_tbl (map=1) of the P4 program (prog=1)..
# Template: ovs-ofctl update-bpf-map <BRIDGE> <PROGRAM-ID> <MAP-ID> key <KEY-DATA> value <VALUE-DATA>
$ ovs-ofctl update-bpf-map br0 1 1 key 14 0 16 172 value 0 0 0 0
# Dump content of the downstream_tbl (map=1) of the tunneling.p4 program (prog=1).
$ ovs-ofctl dump-bpf-map br0 1 1 hex
NXT_DUMP_MAP_REPLY (xid=0x4):
The map contains 1 element(s)
Key: 
0e 00 10 ac
Value: 
00 00 00 00

# To delete the above entry:
$ ovs-ofctl delete-bpf-map 1 1 key 14 0 16 172
$ ovs-ofctl dump-bpf-map br0 1 1
NXT_DUMP_MAP_REPLY (xid=0x4):
The map contains 0 element(s)
# Unload the P4 program from OVS:
$ ovs-ofctl unload-bpf-prog 1 1
$ ovs-ofctl show-bpf-prog br0
NXT_BPF_SHOW_PROG_REPLY (xid=0x4):
The number of BPF programs already loaded: 0
```

#### Mininet

P4rt-OVS can be also integrated into Mininet. The only modification required is to add `datapath = 'user` option to
`addSwitch()` function, as follows:

```python
s1 = self.addSwitch('s1', datapath = 'user')
```

**Note!** Make sure both `ovsdb-server` and `ovs-vswitchd` daemons are started before running Mininet script.

We also developed the wrapper for P4rt-OVS (based on the OVSSwitch class of Mininet) to make loading P4 programs to
Mininet's switches more straightforward. The example of Mininet script for P4rt-OVS can be found in `utilities/mininet/`.

Remember that there are no flow rules configured by default. In the above example (with only one switch in the network)
you can configure the following rules to enable communication between hosts:

```bash
$ sudo ovs-ofctl add-flow s1 in_port=1,actions=prog:1,output:2
$ sudo ovs-ofctl add-flow s1 in_port=2,actions=prog:1,output:1
```

### Known limitations

- Data plane modules can only make a decision whether to drop a packet or pass it back to the OVS pipeline. An output port cannot be determined from within a data plane program.

# Contributing

The P4rt-OVS project welcomes new contributors. This version of P4rt-OVS is still a research prototype. It may contain
serious bugs and should be used only for experimentation and research purposes.

Nevertheless, we are looking forward to your feedback regarding the current functionality or new features. Our goal is
to find the best way to bring the P4 support to Open vSwitch in order to make programming data plane programs less complex
and leverage OVS in new areas of use cases.

- To start contributing and get familiar with P4rt-OVS check out [Open issues](https://github.com/Orange-OpenSource/p4rt-ovs/issues)
- If you will find a bug, please submit the [new issue](https://github.com/Orange-OpenSource/p4rt-ovs/issues/new).
- We are also waiting for your PRs with new features!

# License

Except for the `lib/bpf/lookup3.c` file in the public domain, all new files
introduced by Oko compared to Open vSwitch are licensed under Apache 2.0.
Modified files from both Open vSwitch and ubpf are also licensed under their
original license, Apache 2.0.

# Contacts

Tomasz Osiński &lt;tomasz.osinski2@orange.com&gt;

Mateusz Kossakowski &lt;mateusz.kossakowski@orange.com&gt;

Paul Chaignon &lt;paul.chaignon@orange.com&gt;

# Acknowledgment

This work was made in cooperation with Warsaw University of Technology.