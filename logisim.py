import sys
from logisim.parse import parse
from logisim.component import Clock, In, Out, Splitter, Gate
import icestick

if len(sys.argv) > 1:
    name = sys.argv[1]
else:
    print 'usage: python logisym.py file.circ'
    sys.exit(-1)

circuit = parse(name)

ins = []
for c in circuit.inputs:
    if isinstance(c, In):
        ins.append(c.name)

outs = []
for c in circuit.outputs:
    if isinstance(c, Out):
        outs.append(c.name)

ins.sort()
ninputs = len(circuit.inputs)
if ninputs == 1:
    c = circuit.inputs[0]
    ioname = 'main.J1_0'
    c.name = ioname
elif ninputs > 1:
    for c in circuit.inputs:
        if isinstance(c, In):
            n = ins.index(c.name)
            ioname = 'main.J1[%d]' % n
            # print "# Mapping %s to %s" % (c.name, name)
            c.name = ioname

outs.sort()
noutputs = len(circuit.outputs)
if noutputs == 1:
    c = circuit.outputs[0]
    ioname = 'main.J3_0'
    c.name = ioname
elif noutputs > 1:
    for c in circuit.outputs:
        if isinstance(c, Out):
            n = outs.index(c.name)
            ioname = 'main.J3[%d]' % n
            # print "# Mapping %s to %s" % (c.name, name)
            c.name = ioname

icestick.icestick(circuit)

for c in circuit.components:
    if isinstance(c, Clock):
        continue
    print c, '=', c.getConstructor(circuit)


def getArgs(c):
    i = [circuit.getOutput(port)
         for port in c.inputs if circuit.connected(port)]

    args = ','.join(i)

    if hasattr(c, 'CE') and circuit.connected(c.CE):
        args += ', ce=%s' % circuit.getOutput(c.CE)
    if hasattr(c, 'R') and circuit.connected(c.R):
        args += ', r=%s' % circuit.getOutput(c.R)
    if hasattr(c, 'S') and circuit.connected(c.S):
        args += ', s=%s' % circuit.getOutput(c.S)

    return args

print
components = list(circuit.tsort())
for c in components:
    if isinstance(c, Out):
        continue

    if isinstance(c, Splitter):
        o = str(c)
        i = getArgs(c)
        if len(c.inputs) > 1:
            print '%s = array(%s)' % (o, i)
        else:
            print '%s = %s' % (o, i)
    else:
        args = []
        for port in c.inputs:
            if circuit.connected(port):
                args.append(circuit.getOutput(port))
        inst = str(c)
        print '{}_O = {}({})'.format(inst, inst, ",".join(args))

print
for c in components:
    if isinstance(c, Out):
        assert len(c.inputs)
        port = c.inputs[0]
        assert circuit.connected(port)
        i = circuit.getOutput(port)
        print 'wire(%s, %s)' % (str(i), str(c))

print
print 'compile("%s", main)' % (name.split('.')[0])
