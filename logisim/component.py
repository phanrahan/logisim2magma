class Component:
    def __init__(self, x, y, w, h, **kwargs):

        # only need this for the edge function
        self.origin = (x, y)
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

    def getConstructor(self, circuit):
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

        negate = ninputs * [0]
        for i in range(ninputs):
            negate[i] = kwargs.get('negate' + str(i), negate[i] )
        self.negate = negate

        self.negated = negated
        if self.negated:
            w += 10

        x = loc[0] - w
        y = loc[1] - (h/20)*10

        Component.__init__(self, x, y, w, h, **kwargs)

        if noutputs > 0:
            self.outputs.append(loc)

        for i in range(ninputs):
            iloc = self.getInputLoc(i, negate[i], ninputs, loc, self.facing, w)
            self.inputs.append(iloc)

        self.orient(loc)

        #print 'Gate', x, y, w, h
        #print self.inputs
        #print self.outputs

    def getNumInputs(self, circuit):
        n = 0
        for port in self.inputs:
             if circuit.connected(port):
                 n += 1
        return n
       
    def getConstructor(self, circuit, op=None):
        args = []
        n = 0

        negatedinput = False
        for i in range(len(self.inputs)):
            if circuit.connected(self.inputs[i]):
                arg = 'I{}'.format(n)
                if self.negate[n]:
                    arg = '~' + arg
                    negatedinput = True
                args.append(arg)
                n += 1

        if negatedinput:
            expr = op.join(args)
            if self.negated:
                expr = '~(' + expr + ')'
            name = 'LUT%d(' + expr + ')'
            return name % n
        else:
            args = '()' if n < 2 else '(%d)' % n
            return self.type + args

    def getInputLoc(self, index, negate, ninputs, loc, facing, size):

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
        if negate:
           dx -= 10

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

    def getConstructor(self, circuit):
        return Gate.getConstructor(self, circuit, '&' )

class NAnd(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, negated=True, **kwargs)

        self.type = "NAnd"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

    def getConstructor(self, circuit):
        return Gate.getConstructor(self, circuit, '&' )

class Or(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, **kwargs)

        self.type = "Or"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

    def getConstructor(self, circuit):
        return Gate.getConstructor(self, circuit, '|' )


class NOr(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, negated=True, **kwargs)

        self.type = "NOr"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

    def getConstructor(self, circuit):
        return Gate.getConstructor(self, circuit, '|' )


class XOr(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, w=60, **kwargs)

        self.type = "XOr"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

    def getConstructor(self, circuit):
        return Gate.getConstructor(self, circuit, '^' )


class XNOr(Gate):
    def __init__(self, loc, ninputs=5, **kwargs):
        Gate.__init__(self, loc, ninputs, 1, w=60, negated=True, **kwargs)

        self.type = "NXOr"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

    def getConstructor(self, circuit):
        return Gate.getConstructor(self, circuit, '^' )


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

    def getConstructor(self, circuit):
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

        self.type = "DFF"
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

    def getConstructor(self, circuit):
        args = '(%d)' % self.width
        return self.type + args

class Register(Box):
    def __init__(self, loc, **kwargs):
        Box.__init__(self, loc, **kwargs)

        self.width = kwargs.get('width', 8)

        Q = self.getEdgeLoc('east', 2)

        D = self.getEdgeLoc('west',2)
        self.CLK = self.getEdgeLoc('west', 3)

        self.CE = self.getEdgeLoc('south', 1)
        # asynchronous reset`
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

        self.CS = self.getEdgeLoc('south', 5)

    def getConstructor(self, circuit):
        mem = map(str, self.mem)
        mem = '[' + ",".join(mem) + ']'
        args = '(%s, %d)' % (mem, self.datawidth)
        return self.type + args

class ROM(Memory):
    def __init__(self, loc, **kwargs):
        Memory.__init__(self, loc, **kwargs)

        self.inputs = [self.A]
        self.outputs = [self.D]

        self.type = "ROM"
        self.inst = self.type + "_%d_%d" % loc
        self.name = kwargs.get('label',self.inst)

class RAM(Memory):
    def __init__(self, loc, **kwargs):
        Memory.__init__(self, loc, **kwargs)

        self.DI = self.getEdgeLoc('west', 6)
        self.inputs = [self.A, self.DI]

        self.outputs = [self.D]

        self.WE = self.getEdgeLoc('south', 4)
        self.CLK = self.getEdgeLoc('south', 6)
        self.OE = self.getEdgeLoc('south', 7)
        self.R = self.getEdgeLoc('south', 8) # asynchronous

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

    def getConstructor(self, circuit):
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
