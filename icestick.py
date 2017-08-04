from logisim.component import DFF, TFF, SRFF, JKFF, Register, Counter, Memory

def icestick(circuit):
    ninputs = len(circuit.inputs)
    noutputs = len(circuit.outputs)
    clocks = False
    for c in circuit.components:
        if   isinstance(c, DFF):
            clocks = True
        elif isinstance(c, TFF):
            clocks = True
        elif isinstance(c, SRFF):
            clocks = True
        elif isinstance(c, JKFF):
            clocks = True
        elif isinstance(c, Register):
            clocks = True
        elif isinstance(c, Counter):
            clocks = True
        elif isinstance(c, Memory):
            clocks = True

    print '''from magma import array, compile, wire
from loam.boards.icestick import IceStick
from mantle import I0, I1, I2, I3, LUT1, LUT2, LUT3, LUT4, And, NAnd, Or, NOr, XOr, NXOr, Not, Add, Sub, Buf, Mux, DFF, TFF, SRFF, JKFF, Register, Counter, ROM

icestick = IceStick()'''

    if clocks:
        print "icestick.Clock.on()"

    if ninputs == 1:
        print "icestick.J1[0].input().rename('J1_0').on()"
    elif ninputs > 1:
        print '''\
for i in range({}):
   icestick.J1[i].input().on()'''.format(ninputs)

    if noutputs == 1:
       print "icestick.J3[0].output().rename('J3_0').on()"
    elif noutputs > 1:
        print '''\
for i in range({}):
   icestick.J3[i].output().on()'''.format(noutputs)

    print '''
main = icestick.main()
'''

