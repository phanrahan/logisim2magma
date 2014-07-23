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

        self.visited = False
    
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

    def prune(self):
        for c in self.components:
            if isinstance(c, Gate):
                c.inputs = [i for i in c.inputs if i in self.ports]
            #c.outputs = [i for i in c.outputs if i in self.ports]

            if hasattr(c, 'CE'):
                c.CE = c.CE if self.connected(c.CE) else None
            if hasattr(c, 'R'):
                c.R = c.R if self.connected(c.R) else None
            if hasattr(c, 'S'):
                c.S = c.S if self.connected(c.S) else None

        #self.inputs = [i for i in c.inputs if i in self.ports]
        #self.outputs = [i for i in c.outputs if i in self.ports]

    def wire(self):
        for c in self.inputs:
            o = c.outputs[0]
            self.ports[o].addOutput((c,o))

        for c in self.outputs:
            i = c.inputs[0]
            self.ports[i].addInput((c,i))

        for c in self.components:
             for o in c.outputs:
                 if o in self.ports:
                     self.ports[o].addOutput((c,o))
             for i in c.inputs:
                 if i in self.ports:
                     self.ports[i].addInput((c,i))

    def tsort(self):
        for c in self.components:
            if isinstance(c, Memory) or isinstance(c, FF):
                for oport in c.outputs:
                    if oport in self.ports:
                        n = self.ports[oport]
                        n.visited = True

        stack = [i for i in self.inputs]
        path = []

        while stack != []:
            o = stack.pop()
            for oport in o.outputs:
                if oport in self.ports:
                    n = self.ports[oport]
                    n.visited = True
                    for icomp, iport in n.inputs:
                        if icomp not in path:
                            fire = True
                            for iport in icomp.inputs:
                                m = self.ports[oport]
                                if not m.visited:
                                    fire = False
                            if fire:
                                 stack.append(icomp)
                                 path.append(icomp)

        return path

    def getOutput(self, port):
        net = self.ports[port]
        ocomp, oport = net.outputs[0]
        if isinstance(ocomp, Splitter) and len(ocomp.inputs) == 1:
            i = ocomp.outputs.index(oport)
            iport = ocomp.inputs[0]
            net = self.ports[iport]
            #print net.inputs, net.outputs
            icomp, iport = net.outputs[0]
            return str(icomp) + ('[%d]' % i)
        else:
            if len(ocomp.outputs) == 1:
                return str(ocomp)
            else:
                o = ocomp.outputs.index(oport)
                return str(ocomp) + '[%d]' % o
   
class Component:
    def __init__(self, x, y, w, h, **kwargs):

        # only need this for the edge function
        self.origin = (x,y)
        self.size = (w, h)

        # only need this for the orient function
        self.facing = kwargs.get('facing', 'east')

        self.kwinputs = {}
        self.inputs = []
        self.kwoutputs = {}
        self.outputs = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def getConstructor(self):
        return self.type + '()'

    def getEdgeLoc(self, edge, i):
        i = 10 * i
        x, y = self.origin
        w, h = self.size
        if   edge == 'north':
            return x+i, y
        elif edge == 'south':
            return x+i, y+h
        elif edge == 'west':
            return x, y+i
        elif edge == 'east':
            return x+w, y+i

    def getFaceLoc(self, x, y, dx, dy):
        face = self.facing
        if   face == 'east':
            return x + dx, y + dy
        elif face == 'north':
            return x + dy, y - dx
        elif face == 'west':
            return x - dx, y - dy
        elif face == 'south':
            return x - dy, y + dx

    def orientBox(self, org, x, y, w, h):
        face = self.facing
        if   face == 'east':
            return x + dx, y + dy
        elif face == 'north':
            return x + dy, y - dx
        elif face == 'west':
            return x - dx, y - dy
        elif face == 'south':
            return x - dy, y + dx

    def orientLoc(self, loc, org):
        ox, oy = org
        x, y = loc

        dx = x - ox
        dy = y - oy

        x = ox
        y = oy

        newloc = self.getFaceLoc(x, y, dx, dy)
        #print '# Mapping', loc, 'to', newloc, 'rotate', org, self.facing

        return newloc

    def orient(self, org):
        for i in range(len(self.inputs)):
            self.inputs[i] = self.orientLoc(self.inputs[i], org)

        for i in range(len(self.outputs)):
            self.outputs[i] = self.orientLoc(self.outputs[i], org)

        # kwinputs
        # kwoutputs

class Power(Component):
    def __init__(self, loc, **kwargs):
        x, y = loc
        Component.__init__(self, x, y-10, w=20, h=20, **kwargs)

        self.outputs.append(loc)

        self.type = 'Power'
        self.inst = "1"
        self.name = kwargs.get('label',self.inst)

class Ground(Component):
    def __init__(self, loc, **kwargs):
        x, y = loc
        Component.__init__(self, x, y-10, w=20, h=20, **kwargs)

        self.outputs.append(loc)

        self.type = 'Ground'
        self.inst = "0"
        self.name = kwargs.get('label',self.inst)

class In(Component):
    def __init__(self, loc, **kwargs):
        x, y = loc
        Component.__init__(self, x-20, y-10, w=20, h=20, **kwargs)

        self.outputs.append(loc)

        self.type = 'In'
        self.inst = "In_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)


class Out(Component):
    def __init__(self, loc, **kwargs):
        x, y = loc
        Component.__init__(self, x, y-10, w=20, h=20, **kwargs)

        self.inputs.append(loc)

        self.type = 'Out'
        self.inst = "Out_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Clock(Component):
    def __init__(self, loc, **kwargs):
        x, y = loc
        Component.__init__(self, x, y-10, w=20, h=20, **kwargs)

        self.outputs.append(loc)

        self.type = 'Clock'
        self.inst = "Clock_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)


class Gate(Component):
    def __init__(self, loc, ninputs, noutputs, w=50, h=50, negated=False, 
                   **kwargs):

        size = kwargs.get('size', None)
        if size:
           w = h = size

        self.negated = negated
        if self.negated:
            w += 10

        x = loc[0] - w
        y = loc[1] - (h/20)*10

        Component.__init__(self, x, y, w, h, **kwargs)

        if noutputs > 0:
            self.outputs.append(loc)

        for i in range(ninputs):
            iloc = self.getInputLoc(i, ninputs, loc, self.facing, w)
            self.inputs.append(iloc)

        self.orient(loc)

        #print 'Gate', x, y, w, h
        #print self.inputs
        #print self.outputs

    def getConstructor(self):
        args = '()' if len(self.inputs) < 2 else '(%d)' % len(self.inputs)
        return self.type + args

    def getInputLoc(self, index, ninputs, loc, facing, size):

        if ninputs % 2 == 0: ninputs += 1

        #axisLength = size + bonusWidth + (negateOutput ? 10 : 0)
        #axisLength = size

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


        x, y = loc

        dx = -size

        if ninputs & 1 == 1: 
            dy = skipStart * (ninputs - 1) + skipDist * index
        else:
            dy = skipStart * ninputs + skipDist * index
            if index >= ninputs / 2:
                dy += skipLowerEven

        return x+dx, y+dy


class And(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, **kwargs)

        self.type = "And"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class NAnd(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, negated=True, **kwargs)

        self.type = "NAnd"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Or(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, **kwargs)

        self.type = "Or"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Nor(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, negated=True, **kwargs)

        self.type = "NOr"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Xor(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, w=60, **kwargs)

        self.type = "Xor"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class XNor(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, ninputs, 1, loc, w=60, negated=True, **kwargs)

        self.type = "XNor"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Buffer(Gate):
    def __init__(self, loc, **kwargs):
        Gate.__init__(self, loc, 1, 1, w=20, h=20, **kwargs)

        self.type = "Buffer"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Not(Gate):
    def __init__(self, loc, **kwargs):
        Gate.__init__(self, loc, 1, 1, w=20, h=20, negated=True, **kwargs)

        self.type = "Not"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Plexer(Component):
    def __init__(self, loc, **kwargs):
        self.select = kwargs.get("select", 1)
        self.width = 1 << self.select

        if self.select == 1:
            w = 30
            h = 40
        else:
            w = 40
            h = (self.width + 2) * 10

        x = loc[0] - w
        y = loc[1] - h/2

        Component.__init__(self, x, y, w, h, **kwargs)

        if self.select == 1:
            I0 = self.getEdgeLoc('west', 1)
            I1 = self.getEdgeLoc('west', 3)
            S = self.getEdgeLoc('south', 1)

            self.inputs = [I0, I1, S]

        else:
            I = self.width * [0]
            for i in range(self.width):
                 I[i] = self.getEdgeLoc('west', i+1)
            self.S = self.getEdgeLoc('south', 2)

            self.inputs = I + [S]

        self.OE = self.getEdgeLoc('south', 3)

        self.outputs = [loc]

class Mux(Plexer):
    def __init__(self, loc, **kwargs):
        Plexer.__init__(self, loc, **kwargs)

        self.type = "Mux"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

    def getConstructor(self):
        args = '(%d)' % self.width
        return self.type + args


class FF(Component):
    def __init__(self, loc, w=40, h=40, **kwargs):
        x = loc[0] - w
        y = loc[1] - 10
        Component.__init__(self, x, y, w, h, **kwargs)

        self.Q = self.getEdgeLoc('east', 1)
        self.Qp = self.getEdgeLoc('east', 3)

        CLK = self.getEdgeLoc('west', 2)

        CE = self.getEdgeLoc('south', 2)
        R = self.getEdgeLoc('sorth', 1)
        S = self.getEdgeLoc('south', 3)

        self.kwinputs = {"R":R, "S":S, "CE":CE, "CLK":CLK}

class DFF(FF):
    def __init__(self, loc, **kwargs):
        FF.__init__(self, loc, **kwargs)

        D = self.getEdgeLoc('west', 3)
        self.inputs = [D]
        self.outputs = [self.Q]

        self.type = "FF"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class TFF(FF):
    def __init__(self, loc, **kwargs):
        FF.__init__(self, loc, **kwargs)

        T = self.getEdgeLoc('west', 3)
        self.inputs = [T]
        self.outputs = [self.Q]

        self.type = "TFF"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class SRFF(FF):
    def __init__(self, loc, **kwargs):
        FF.__init__(self, loc, **kwargs)

        S = self.getEdgeLoc('west', 1)
        R = self.getEdgeLoc('west', 3)
        self.inputs = [S, R]
        self.outputs = [self.Q]
        #self.outputs = [self.Q, self.Qp]

        self.type = "SRFF"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class JKFF(FF):
    def __init__(self, loc, **kwargs):
        FF.__init__(self, loc, **kwargs)

        J = self.getEdgeLoc('west', 1)
        K = self.getEdgeLoc('west', 3)
        self.inputs = [J, K]
        self.outputs = [self.Q]
        #self.outputs = [self.Q, self.Qp]

        self.type = "JKFF"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)



class Box(Component):
    def __init__(self, loc, w=30, h=40, **kwargs):
        x = loc[0] - w
        y = loc[1] - 20
        Component.__init__(self, x, y, w, h, **kwargs)

    def getConstructor(self):
        args = '(%d)' % self.width
        return self.type + args

class Register(Box):
    def __init__(self, loc, **kwargs):
        Box.__init__(self, loc, **kwargs)

        self.width = kwargs.get('width', 8)

        Q = self.getEdgeLoc('east', 2)
        D = self.getEdgeLoc('west',2)

        self.CLK = self.getEdgeLoc('south', 1)
        self.R = self.getEdgeLoc('south', 2)

        self.inputs.append(D)
        self.outputs.append(Q)

        self.type = "Register"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Counter(Box):
    def __init__(self, loc, **kwargs):
        Box.__init__(self, loc, **kwargs)

        self.width = kwargs.get('width', 8)

        Q = self.getEdgeLoc('east', 2)
        COUNT = self.getEdgeLoc('west', 3)

        #D = self.getEdgeLoc('west',2)
        #LOAD = self.getEdgeLoc('west', 1)

        self.CLK = self.getEdgeLoc('south', 1)
        self.R = self.getEdgeLoc('south', 2)

        self.COUT = self.getEdgeLoc('east', 3)

        self.inputs.append(COUNT)
        self.outputs.append(Q)

        self.type = "Counter"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Memory(Component):
    def __init__(self, loc, w=140, h=80, **kwargs):
        x = loc[0] - w
        y = loc[1] - h/2
        Component.__init__(self, x, y, w, h, **kwargs)

        # addrwidth in [2048, 1024]
        self.addrwidth = kwargs.get("addrWidth", 8)
        # datawidth in [8, 9, 16, 18]
        self.datawidth = kwargs.get("dataWidth", 8)

        self.mem = kwargs.get('contents',0)
        n = len(self.mem)
        if n < (1 << self.addrwidth):
            self.mem += ((1 << self.addrwidth) - n) * [0]
            assert len(self.mem) == (1 << self.addrwidth)

        self.D = self.getEdgeLoc('east', 4)
        self.A = self.getEdgeLoc('west', 4)

        self.SEL = self.getEdgeLoc('south', 5)

    def getConstructor(self):
        mem = map(str, self.mem)
        mem = '[' + ",".join(mem) + ']'
        args = '(%s, %d)' % (mem, self.datawidth)
        return self.type + args

class ROM(Memory):
    def __init__(self, loc, **kwargs):
        Memory.__init__(self, loc, **kwargs)

        self.inputs = [self.A]
        self.outputs = [self.D]

        self.type = "ROMB"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class RAM(Memory):
    def __init__(self, loc, **kwargs):
        Memory.__init__(self, loc, **kwargs)

        self.inputs = [self.A]
        self.outputs = [self.D]

        self.CLK = self.getEdgeLoc('south', 6)
        self.WE = self.getEdgeLoc('south', 7)

        self.R = self.getEdgeLoc('south', 8)

        self.type = "RAMB"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Arith(Component):
    def __init__(self, loc, w=40, h=40, **kwargs):
        x = loc[0] - w
        y = loc[1] - h/2
        Component.__init__(self, x, y, w, h, **kwargs)

        self.width = kwargs.get("width", 8)

        A = self.getEdgeLoc('west', 1)
        B = self.getEdgeLoc('west', 3)

        C = self.getEdgeLoc('east', 2)

        self.CIN = self.getEdgeLoc('south', 2)
        self.COUT = self.getEdgeLoc('north', 2)

        self.inputs = [A, B]
        self.outputs = [C]

    def getConstructor(self):
        args = '(%d)' % self.width
        return self.type + args

class Add(Arith):
    def __init__(self, loc, **kwargs):
        Arith.__init__(self, loc, **kwargs)

        self.type = "Add"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class Sub(Arith):
    def __init__(self, loc, **kwargs):
        Arith.__init__(self, loc, **kwargs)

        self.type = "Sub"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)



class Splitter(Component):
    def __init__(self, loc, **kwargs):
        self.fanout = kwargs.get('fanout', 2)
        self.output = kwargs.get('incoming', 2)
        self.appear = kwargs.get('appear','left')
        self.bit0 = kwargs.get('bit0',0)

        w = 20
        h = 10*self.fanout
        if self.appear == 'right':
            x = loc[0]
            y = loc[1]
        else:
            x = loc[0]
            y = loc[1] - h

        Component.__init__(self, x, y, w, h, **kwargs)

        self.fanin = loc
        self.fanouts = []
        org = loc
        for i in range(self.fanout):
            if self.appear == 'right':
                loc = (x+20, y+10*i+10)
            else:
                loc = (x+20, y+10*i)
            loc = self.orientLoc(loc, org)
            self.fanouts.append(loc)

        if self.appear == 'left'  and self.bit0 != 0:
            self.fanouts.reverse()
        if self.appear == 'right' and self.bit0 == 0:
            self.fanouts.reverse()

        self.type = "Splitter"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

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
             if key == 'contents':
                 val = a.firstChild.data.split()
                 val = [int(v, 16) for v in val[3:]]
             else:
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
        elif n == 'Power':
            c = Power(l, **d)
            circuit.addInput(c)
        elif n == 'Ground':
            c = Ground(l, **d)
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
            elif n == 'XNOR Gate':
                c = XNor(l, **d)
            elif n == 'NOT Gate':
                c = Not(l, **d)

            elif n == 'Multiplexer':
                c = Mux(l, **d)

            elif n == 'Adder':
                c = Add(l, **d)
            elif n == 'Subtractor':
                c = Sub(l, **d)

            elif n == 'Clock':
                c = Clock(l, **d)

            elif n == 'D Flip-Flop':
                c = DFF(l, **d)
            elif n == 'T Flip-Flop':
                c = TFF(l, **d)
            elif n == 'S-R Flip-Flop':
                c = SRFF(l, **d)
            elif n == 'J-K Flip-Flop':
                c = JKFF(l, **d)

            elif n == 'Register':
                c = Register(l, **d)
            elif n == 'Counter':
                c = Counter(l, **d)

            elif n == 'ROM':
                c = ROM(l, **d)
            elif n == 'RAM':
                c = RAM(l, **d)


            elif n == 'Splitter':
                c = Splitter(l, **d)
 
            else:
                if n != 'Text':
                    print n, 'not implemented'
                    sys.exit(0)

            if c:
                circuit.addComponent(c)


circuit.prune()
circuit.wire()

ins = []
for c in circuit.inputs:
    if isinstance(c, In):
        ins.append(c.name)

ins.sort()
for c in circuit.inputs:
    if isinstance(c, In):
        n = ins.index(c.name)
        name = 'SWITCH[%d]' % n
        print "# Mapping %s to %s" % (c.name, name)
        c.name = name

outs = []
for c in circuit.outputs:
    if isinstance(c, Out):
        outs.append(c.name)

outs.sort()
for c in circuit.outputs:
    if isinstance(c, Out):
        n = outs.index(c.name)
        name = 'LED[%d]' % n
        print "# Mapping %s to %s" % (c.name, name)
        c.name = name


def setinput(c, port):
     #print 'Splitter Input', port
     c.inputs.append(port)
     if port in circuit.ports:
         #circuit.addInput(c)
         circuit.ports[port].addInput((c,port))

def setoutput(c, port):
     #print 'Splitter Output', port
     c.outputs.append(port)
     if port in circuit.ports:
         #circuit.addOutput(c)
         circuit.ports[port].addOutput((c,port))

for c in circuit.splitters:
    fanin = False
    port = c.fanin
    if port in circuit.ports:
        out = circuit.ports[port].outputs
        #print port, 'is connected to a net with outputs', out
        if out:
            fanin = True

    #print 'fanouts', len(c.fanouts)
    fanout = False
    for port in c.fanouts:
        if port in circuit.ports:
            out =  circuit.ports[port].outputs
            #print port, 'is connected to a net with outputs', out
            if out:
                fanout = True

    if fanin and fanout:
        print "# Outputs on both sides of splitter", c
        continue

    if not fanin and not fanout:
        print "# No Outputs on both sides of splitter", c
        continue

    if fanin:
        #print 'Splitter Fan In', c
        setinput(c, c.fanin)
        for i in range(len(c.fanouts)):
            setoutput(c, c.fanouts[i])

    if fanout:
        #print 'Splitter Fan Out', c
        setoutput(c, c.fanin)
        for i in range(len(c.fanouts)):
            setinput(c, c.fanouts[i])
              

print 'from magma.shield.LogicStart import *'
print

for c in circuit.components:
    if isinstance(c, Clock):
        continue
    print c, '=', c.getConstructor()

def getArgs(c):
    i = [circuit.getOutput(port) for port in c.inputs]

    args = ','.join(i)

    if hasattr(c, 'CE') and c.CE:
        args += ', ce=%s' % circuit.getOutput( c.CE )
    if hasattr(c, 'R') and c.R:
        args += ', r=%s' % circuit.getOutput( c.R )
    if hasattr(c, 'S') and c.S:
        args += ', s=%s' % circuit.getOutput( c.S )

    return args

for c in circuit.splitters:
    if len(c.inputs) > 1:
        o = str(c)
        i = getArgs(c)
        print '%s = [%s]' % (o, i)

print
for c in reversed(circuit.tsort()):
    if isinstance(c, Splitter):
        continue
    if len(c.inputs):
        o = str(c)
        i = getArgs(c)
        print '%s(%s)' % (o, i)

