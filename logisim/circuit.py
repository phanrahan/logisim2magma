from .component import Splitter, Memory, FF, In, Out

#
# Net has a set of inputs and a single output
#
class Net:
    def __init__(self, port0, port1):
        self.ports = [port0, port1]
        self.outputs = []
        self.inputs = []

        self.visited = False
    
    def addPort(self, port):
        if port not in self.ports:
            self.ports.append(port)

    def addOutput(self, output):
        #print 'net: adding output', output
        if len(self.outputs) > 0:
             print 'Warning: more than 1 output on this net'
        self.outputs.append(output)

    def addInput(self, input):
        #print 'net: adding input', input
        self.inputs.append(input)

class Circuit:
    def __init__(self):
        self.nets = []  # list of all the nets
        self.ports = {} # maps from a port to net it is connected to

        self.inputs = []
        self.outputs = []
        self.components = []
        self.splitters = []

    def addWire(self, port0, port1):

        if   port0 in self.ports and port1 in self.ports:
            net0 = self.ports[port0]
            net1 = self.ports[port1]
            if net0 != net1:
                self.nets.remove(net0)
                self.nets.remove(net1)
                net = Net(port0, port1)
                self.nets.append(net)
                for port in net0.ports:
                    net.addPort(port)
                    self.ports[port] = net
                for port in net1.ports:
                    net.addPort(port)
                    self.ports[port] = net

        elif port0 not in self.ports and port1 not in self.ports:
            net = Net(port0,port1)
            self.nets.append(net)
            self.ports[port0] = net
            self.ports[port1] = net

        if port0 in self.ports:
            net = self.ports[port0]

        if port1 in self.ports:
            net = self.ports[port1]

        if port0 not in self.ports:
            self.ports[port0] = net
            net.addPort(port0)
        if port1 not in self.ports:
            self.ports[port1] = net
            net.addPort(port1)
              
    def addInput(self, component):
        self.inputs.append(component)

    def addOutput(self, component):
        self.outputs.append(component)

    def addComponent(self, component):
        if isinstance(component, Splitter):
            self.splitters.append(component)
        else:
            self.components.append(component)

    def connected(self, port):
        return port in self.ports

    #
    # wire up the inputs and outputs
    #  this means connect each point to the relevant net
    #
    def wire(self):
        for c in self.inputs:
            o = c.outputs[0]
            self.ports[o].addOutput((c,o))

        for c in self.outputs:
            i = c.inputs[0]
            self.ports[i].addInput((c,i))

        for c in self.components:
             for o in c.outputs:
                 if self.connected(o):
                     self.ports[o].addOutput((c,o))
             for i in c.inputs:
                 if self.connected(i):
                     self.ports[i].addInput((c,i))

    def tsort(self):
        for c in self.components:
            if isinstance(c, Memory) or isinstance(c, FF):
                for oport in c.outputs:
                    if self.connected(oport):
                        n = self.ports[oport]
                        n.visited = True

        stack = [i for i in self.inputs]
        path = []

        while stack != []:
            o = stack.pop()
            for oport in o.outputs:
                if self.connected(oport):
                    # find net connected to this port
                    n = self.ports[oport]
                    n.visited = True
                    for icomp, iport in n.inputs:
                        if icomp not in path:
                            # check that all the inputs are ready
                            fire = True
                            for port in icomp.inputs:
                                if self.connected(port):
                                    m = self.ports[port]
                                    if not m.visited:
                                        fire = False
                            if fire:
                                stack.append(icomp)
                                path.append(icomp)

        return path

    def getOutput(self, port):
        net = self.ports[port]
        ocomp, oport = net.outputs[0]
        if isinstance(ocomp, In):
            return str(ocomp)
        elif isinstance(ocomp, Splitter):
            if len(ocomp.outputs) == 1:
                return str(ocomp)
            else:
                o = ocomp.outputs.index(oport)
                return str(ocomp) + '[%d]' % o
        else:
            if len(ocomp.outputs) == 1:
                return str(ocomp) + '.O'
            else:
                o = ocomp.outputs.index(oport)
                return str(ocomp) + '.O[%d]' % o
