MAGMA = ~hanrahan/git//magma
DEVICE='xc3s250e'

TESTS = And.xdl ExclusiveOr.xdl \
	Multiplexer.xdl \
    Demultiplexer.xdl \
    Decoder.xdl \
    FullAdder.xdl

.PHONY: test gold clean

test: $(TESTS)

gold:
	for f in $(TESTS); do \
	        cp $$f $$f.gold; \
	done

clean: 
	rm -f *.bit *.pyc *.xdl *.pcf *.gold
	make -C build clean

%.py: %.circ
	python logisim.py $*.circ > $*.py

%.xdl: %.py
	rm -f $*.pcf $*.xdl
	${MAGMA}/bin/magma -o $@ -p $*.pcf $*
	if [ -e $@.gold ] ; then \
		diff $@ $@.gold ; \
	fi

%.bit: %.xdl
	cp $< build/fpga.xdl
	cp $*.pcf build/fpga.pcf
	make -C build
	cp build/test.bit $@