print "v2.0 raw",
for i in range(256):
    if i % 16 == 0:
        print
    print "%02x" % i,
