TESTS = east.py west.py north.py south.py \
	and.py nand.py xor.py xnor.py \
	Multiplexer.py Demultiplexer.py \
	FullAdder.py Add.py Sub.py \
	DFF.py \
	Register.py 


.PHONY: test gold clean

test: $(TESTS)

gold:
	for f in $(TESTS); do \
	        cp $$f $$f.gold; \
	done

clean: 
	make -C build clean

%.py: %.circ
	python ../logisim.py $*.circ > build/$*.py

