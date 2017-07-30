import sys
import xml.dom.minidom
from logisim.component import *
from logisim.circuit import Circuit

if len(sys.argv) > 1:
     name = sys.argv[1]
else:
     print 'usage: python logisym.py file.circ'
     sys.exit(-1)

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
                c = NOr(l, **d)
            elif n == 'XOR Gate':
                c = XOr(l, **d)
            elif n == 'XNOR Gate':
                c = XNOr(l, **d)
            elif n == 'NOT Gate':
                c = Not(l, **d)
            elif n == 'Buffer':
                c = Buffer(l, **d)

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


circuit.wire()

ins = []
for c in circuit.inputs:
    if isinstance(c, In):
        ins.append(c.name)

outs = []
for c in circuit.outputs:
    if isinstance(c, Out):
        outs.append(c.name)


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
              

def megawing():
    print '''import sys
from magma import compile, wire
from loam.shields.megawing import MegaWing

megawing = MegaWing()
megawing.SWITCH(%d)
megawing.LED(%d)

main = megawing.main()
''' % (len(circuit.inputs), len(circuit.outputs))

    ins.sort()
    for c in circuit.inputs:
        if isinstance(c, In):
            n = ins.index(c.name)
            ioname = 'main.SWITCH[%d]' % n
            #print "# Mapping %s to %s" % (c.name, name)
            c.name = ioname

    outs.sort()
    for c in circuit.outputs:
        if isinstance(c, Out):
            n = outs.index(c.name)
            ioname = 'main.LED[%d]' % n
            #print "# Mapping %s to %s" % (c.name, name)
            c.name = ioname


def icestick():
    print '''import sys
from magma import array, compile, wire
from loam.boards.icestick import IceStick
from mantle import And, NAnd, Or, NOr, XOr, NXOr, Not, Add, Sub, Buf, Mux, DFF, TFF, SRFF, JKFF, Register, Counter

icestick = IceStick()
for i in range(%d):
    icestick.J1[i].input().on()
for i in range(%d):
    icestick.J3[i].output().on()

main = icestick.main()
''' % (len(circuit.inputs), len(circuit.outputs))

    ins.sort()
    for c in circuit.inputs:
        if isinstance(c, In):
            n = ins.index(c.name)
            ioname = 'main.J1[%d]' % n
            #print "# Mapping %s to %s" % (c.name, name)
            c.name = ioname

    outs.sort()
    for c in circuit.outputs:
        if isinstance(c, Out):
            n = outs.index(c.name)
            ioname = 'main.J3[%d]' % n
            #print "# Mapping %s to %s" % (c.name, name)
            c.name = ioname

icestick()

for c in circuit.components:
    if isinstance(c, Clock):
        continue
    print c, '=', c.getConstructor(circuit)

def getArgs(c):
    i = [circuit.getOutput(port) for port in c.inputs if circuit.connected(port)]

    args = ','.join(i)

    if hasattr(c, 'CE') and circuit.connected(c.CE):
        args += ', ce=%s' % circuit.getOutput( c.CE )
    if hasattr(c, 'R') and circuit.connected(c.R):
        args += ', r=%s' % circuit.getOutput( c.R )
    if hasattr(c, 'S') and circuit.connected(c.S):
        args += ', s=%s' % circuit.getOutput( c.S )

    return args

for c in circuit.splitters:
    if len(c.inputs) > 1:
        o = str(c)
        i = getArgs(c)
        print '%s = array(%s)' % (o, i)

print
for c in reversed(circuit.tsort()):
    if isinstance(c, Splitter):
        continue

    if len(c.inputs):
        if isinstance(c, Out):
            assert len(c.inputs) == 1
            port = c.inputs[0]
            assert circuit.connected(port)
            i = circuit.getOutput(port)
            print 'wire(%s, %s)' % (str(i), str(c))
            continue

        o = str(c)
        i = getArgs(c)
        print '%s(%s)' % (o, i)

print
print 'compile("%s", main)' % (name.split('.')[0])
