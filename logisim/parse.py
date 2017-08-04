import sys
import xml.dom.minidom
from .component import *
from .circuit import Circuit


def setinput(circuit, c, port):
    # print 'Splitter Input', port
    c.inputs.append(port)
    if port in circuit.ports:
        # circuit.addInput(c)
        circuit.ports[port].addInput((c, port))


def setoutput(circuit, c, port):
    # print 'Splitter Output', port
    c.outputs.append(port)
    if port in circuit.ports:
        # circuit.addOutput(c)
        circuit.ports[port].addOutput((c, port))


def parse(name):
    circuit = Circuit()

    dom = xml.dom.minidom.parse(name)

    circ = dom.getElementsByTagName('circuit')
    for node in circ:
        wires = node.getElementsByTagName('wire')
        for w in wires:
            f = eval(w.getAttribute('from'))
            t = eval(w.getAttribute('to'))
            circuit.addWire(f, t)

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
                    if val.isdigit():
                        val = int(val)
                d[key] = val
            # print n, l, d
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

    for c in circuit.splitters:
        fanin = False
        port = c.fanin
        if port in circuit.ports:
            out = circuit.ports[port].outputs
            # print port, 'is connected to a net with outputs', out
            if out:
                fanin = True

        # print 'fanouts', len(c.fanouts)
        fanout = False
        for port in c.fanouts:
            if port in circuit.ports:
                out = circuit.ports[port].outputs
                # print port, 'is connected to a net with outputs', out
                if out:
                    fanout = True

        if fanin and fanout:
            print "# Outputs on both sides of splitter", c
            continue

        if not fanin and not fanout:
            print "# No Outputs on both sides of splitter", c
            continue

        if fanin:
            # print 'Splitter Fan In', c
            setinput(circuit, c, c.fanin)
            for i in range(len(c.fanouts)):
                setoutput(circuit, c, c.fanouts[i])

        if fanout:
            # print 'Splitter Fan Out', c
            setoutput(circuit, c, c.fanin)
            for i in range(len(c.fanouts)):
                setinput(circuit, c, c.fanouts[i])

    return circuit
