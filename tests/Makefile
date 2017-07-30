TESTS = east.py west.py north.py south.py splitter.py \
    and.py nand.py xor.py xnor.py \
	Multiplexer.py Demultiplexer.py \
    Mux2.py \
    FullAdder.py Add.py Sub.py \
    RSLatchNOr.py RSLatchNAnd.py \
    DFF.py TFF.py SRFF.py JKFF.py Register.py \
    Counter.py \
    ROM.py 

.PHONY: test gold clean

test: $(TESTS)

gold:
	for f in $(TESTS); do \
	        cp $$f $$f.gold; \
	done

clean: 
	rm -f *.py 
	make -C build clean

%.py: %.circ
	python ../logisim.py $*.circ > build/$*.py

