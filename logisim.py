import sys
import xml.dom.minidom

if len(sys.argv) > 1:
     name = sys.argv[1]
else:
     print 'usage: python logisym.py file.circ'
     sys.exit(-1)

class Net:
    def __init__(self, port0, port1):
        self.ports = [port0, port1]
        #print 'net', self.ports 
        self.outputs = []
        self.inputs = []
    
    def addPort(self, port):
        if port not in self.ports:
            self.ports.append(port)
        #print 'net', self.ports 

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
        self.nets = []
        self.ports = {}
        self.inputs = []
        self.outputs = []
        self.components = []

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
        self.components.append(component)

    def wire(self):
        for c in self.inputs:
            o = c.outputs[0]
            self.ports[o].addOutput((c,o))

        for c in self.outputs:
            i = c.inputs[0]
            self.ports[o].addInput((c,i))

        for c in self.components:
             for o in c.outputs:
                 assert o in self.ports
                 self.ports[o].addOutput((c,o))
             c.inputs = [i for i in c.inputs if i in self.ports]
             for i in c.inputs:
                 self.ports[i].addInput((c,i))
   
class Component:
    def __str__(self):
        return self.inst

    def __repr__(self):
        return self.inst

    def getConstructor(self):
        return self.type + '()'


class Gate(Component):
    def __init__(self, ninputs, noutputs, loc, **kwargs):

        self.name = kwargs.get('label',None)

        facing = kwargs.get('facing', 'east')
        size = kwargs.get('size', 50)

        self.negated = kwargs.get('negated', False)

        self.outputs = []
        if noutputs > 0:
            self.outputs.append(loc)

        self.inputs = []
        for i in range(ninputs):
            self.inputs.append(self.getInputLoc(i, ninputs, loc, facing, size))

    def getConstructor(self):
        args = '()' if len(self.inputs) < 2 else '(%d)' % len(self.inputs)
        return self.type + args

    def getInputLoc(self, index, ninputs, loc, facing, size):

        if ninputs % 2 == 0: ninputs += 1

        #axisLength = size + bonusWidth + (negateOutput ? 10 : 0)
        axisLength = size

        if ninputs <= 3: 
            if size < 40:
                skipStart = -5
                skipDist = 10
                skipLowerEven = 10
            elif size < 60 or ninputs <= 2:
                skipStart = -10
                skipDist = 20
                skipLowerEven = 20
            else:
                skipStart = -15
                skipDist = 30
                skipLowerEven = 30
        elif ninputs == 4 and size >= 60:
            skipStart = -5
            skipDist = 20
            skipLowerEven = 0
        else:
            skipStart = -5
            skipDist = 10
            skipLowerEven = 10


        if ninputs & 1 == 1: 
            dy = skipStart * (ninputs - 1) + skipDist * index
        else:
            dy = skipStart * ninputs + skipDist * index
            if index >= ninputs / 2:
                dy += skipLowerEven

        dx = axisLength
        if self.negated:
            dx += 10

        x, y = loc
        if   facing == 'north':
            return x + dy, y + dx
        elif facing == 'south':
            return x + dy, y - dx
        elif facing == 'west':
            return x + dx, y + dy
        else:
            return x - dx, y + dy



class In(Component):
    def __init__(self, loc, **kwargs):
        self.inputs = []
        self.outputs = [loc]
        self.name = kwargs.get('label',None)
        self.inst = "In_%d_%d" % loc
        self.type = 'In'

class Out(Component):
    def __init__(self, loc, **kwargs):
        self.inputs = [loc]
        self.outputs = []
        self.name = kwargs.get('label',None)
        self.inst = "Out_%d_%d" % loc
        self.type = 'Out'

class And(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, ninputs, 1, loc, **kwargs)
        self.type = "And"
        self.inst = self.type + "_%d_%d" % loc

class NAnd(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, ninputs, 1, loc, negated=True, **kwargs)
        self.type = "NAnd"
        self.inst = self.type + "_%d_%d" % loc

class Or(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, ninputs, 1, loc, **kwargs)
        self.type = "Or"
        self.inst = self.type + "_%d_%d" % loc

class Nor(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, ninputs, 1, loc, negated=True, **kwargs)
        self.type = "NOr"
        self.inst = self.type + "_%d_%d" % loc

class Xor(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        kwargs['size']  = kwargs.get('size', 60)
        Gate.__init__(self, ninputs, 1, loc, **kwargs)
        self.type = "Xor"
        self.inst = self.type + "_%d_%d" % loc

class Not(Gate):
    def __init__(self, loc, **kwargs):
        kwargs['size']  = kwargs.get('size', 20)
        Gate.__init__(self, 1, 1, loc, negated=True, **kwargs)
        self.type = "Not"
        self.inst = self.type + "_%d_%d" % loc


circuit = Circuit()


dom = xml.dom.minidom.parse(name)

circ=dom.getElementsByTagName('circuit')
for node in circ:
    wires = node.getElementsByTagName('wire')
    for w in wires:
        f = eval(w.getAttribute('from'))
        t = eval(w.getAttribute('to'))
        circuit.addWire( f, t )

    #<comp lib="0" loc="(680,120)" name="Pin">
    #  <a name="facing" val="west"/>
    #  <a name="tristate" val="false"/>
    #  <a name="label" val="SUB"/>
    #  <a name="labelloc" val="north"/>
    #  <a name="labelfont" val="SansSerif bold 14"/>
    #</comp>
    comps = node.getElementsByTagName('comp')
    for c in comps:
        n = c.getAttribute('name')
        l = eval(c.getAttribute('loc'))
        d = {}
        anodes = c.getElementsByTagName('a')
        for a in anodes:
             key = a.getAttribute('name')
             val = a.getAttribute('val')
             if val.isdigit(): val = int(val)
             d[key] = val
        #print n, l, d
        c = None
        if n == 'Pin':
            if 'output' in d:
                c = Out(l, **d)
                circuit.addOutput(c)
            else:
                c = In(l, **d)
                circuit.addInput(c)
        else:
            if n == 'AND Gate':
                c = And(l, **d)
            elif n == 'NAND Gate':
                c = NAnd(l, **d)
            elif n == 'OR Gate':
                c = Or(l, **d)
            elif n == 'NOR Gate':
                c = Nor(l, **d)
            elif n == 'XOR Gate':
                c = Xor(l, **d)
            elif n == 'NOT Gate':
                c = Not(l, **d)
            else:
                if n != 'Text':
                    print n, 'not implemented'
                    sys.exit(0)

            if c: circuit.addComponent(c)

        #Clock
        #J-K Flip-Flop
        #S-R Flip-Flop

        
circuit.wire()

ins = []
for c in circuit.inputs:
    ins.append(c.name)

ins.sort()
for c in circuit.inputs:
    n = ins.index(c.name)
    c.inst = 'SWITCH[%d]' % n
    print "# Mapping %s to %s" % (c.name, c.inst)

outs = []
for c in circuit.outputs:
    outs.append(c.name)

outs.sort()
for c in circuit.outputs:
    n = outs.index(c.name)
    c.inst = 'LED[%d]' % n
    print "# Mapping %s to %s" % (c.name, c.inst)

print 'from magma.shield.LogicStart import *'
print

for c in circuit.components:
    print c, '=', c.getConstructor()

print
for c in circuit.components:
    if len(c.inputs):
        o = str(c)
        i = []
        for iport in c.inputs:
            i.append( str( circuit.ports[iport].outputs[0][0] ) )
        i = '(' + ",".join(i) + ')'
        print '%s%s' % (o, i)

print
for c in circuit.outputs:
    for iport in c.inputs:
        i = str(c)
        o = str( circuit.ports[iport].outputs[0][0] )
        print 'wire(%s,%s)' % (o, i)


