CC=			gcc
#CC=			clang --analyze
CFLAGS=		-g -Wall -O2 -m64
CFLAGS_LIB=	-fPIC -Wall -O3 -m64
WRAP_MALLOC=-DUSE_MALLOC_WRAPPERS
AR=			ar
CXXFLAGS_LIB=	$(CFLAGS_LIB)

BWA_LIBRARY_DIR ?= ..

# CRS4_DEBUG_RANDOMNESS eliminates randomness in N base replacement
# and hit selection: this allows to perform comparisons between the
# python wrapper and the original code.

DFLAGS=		-DHAVE_PTHREAD $(WRAP_MALLOC) #-DCRS4_DEBUG_RANDOMNESS #-D_FILE_OFFSET_BITS=64
DFLAGS_LIB=	-DHAVE_PTHREAD $(WRAP_MALLOC) -DBWT_ENABLE_MMAP -DBWT_EXPORT_LIBRARY_FUNCTIONS #-DCRS4_DEBUG_RANDOMNESS #-D_FILE_OFFSET_BITS=64

LOBJS=		utils.o kstring.o ksw.o bwt.o bntseq.o bwa.o bwamem.o bwamem_pair.o malloc_wrap.o
AOBJS=		QSufSort.o bwt_gen.o bwase.o bwaseqio.o bwtgap.o bwtaln.o bamlite.o \
			is.o bwtindex.o bwape.o kopen.o pemerge.o \
			bwtsw2_core.o bwtsw2_main.o bwtsw2_aux.o bwt_lite.o \
			bwtsw2_chain.o fastmap.o bwtsw2_pair.o
OBJS_LIB=	bwtaln.ol bwtgap.ol bwt.ol bwape.ol bwase.ol \
			bwt_mmap.ol bwaseqio.ol bntseq.ol kstring.ol \
			utils.ol bamlite.ol bwamisc.ol
PROG=		bwa
INCLUDES=	
LIBS=		-lm -lz -lpthread
LIBS_LIB=	-lz
SUBDIRS=	.
BWA_LIBRARY_NAME=$(BWA_LIBRARY_DIR)/libbwa

.SUFFIXES:.c .o .cc .ol

.c.o:
		$(CC) -c $(CFLAGS) $(DFLAGS) $(INCLUDES) $< -o $@
.c.ol:
		$(CC) -c $(CFLAGS_LIB) $(DFLAGS_LIB) $(INCLUDES) $< -o $@

all:$(PROG)

libbwa: ${BWA_LIBRARY_NAME}.so

${BWA_LIBRARY_NAME}.so:  ${OBJS_LIB}
	$(CC) -shared $^ ${LIBS_LIB} -o $@

bwa:libbwa.a $(AOBJS) main.o
		$(CC) $(CFLAGS) $(DFLAGS) $(AOBJS) main.o -o $@ -L. -lbwa $(LIBS)

bwamem-lite:libbwa.a example.o
		$(CC) $(CFLAGS) $(DFLAGS) example.o -o $@ -L. -lbwa $(LIBS)

libbwa.a:$(LOBJS)
		$(AR) -csru $@ $(LOBJS)

clean:
		rm -f gmon.out *.o a.out $(PROG) *~ *.a

cleanlib:
		rm -f *.ol *~


# FOR LIB
bwt.ol:bwt.h
bwtio.ol:bwt.h
bwtaln.ol:bwt.h bwtaln.h kseq.h
bntseq.ol:bntseq.h
bwtgap.ol:bwtgap.h bwtaln.h bwt.h

depend:
	( LC_ALL=C ; export LC_ALL; makedepend -Y -- $(CFLAGS) $(DFLAGS) -- *.c )

# DO NOT DELETE THIS LINE -- make depend depends on it.

QSufSort.o: QSufSort.h
bamlite.o: bamlite.h malloc_wrap.h
bntseq.o: bntseq.h utils.h kseq.h malloc_wrap.h
bwa.o: bntseq.h bwa.h bwt.h ksw.h utils.h malloc_wrap.h kseq.h
bwamem.o: kstring.h malloc_wrap.h bwamem.h bwt.h bntseq.h bwa.h ksw.h kvec.h
bwamem.o: ksort.h utils.h kbtree.h
bwamem_pair.o: kstring.h malloc_wrap.h bwamem.h bwt.h bntseq.h bwa.h kvec.h
bwamem_pair.o: utils.h ksw.h
bwape.o: bwtaln.h bwt.h kvec.h malloc_wrap.h bntseq.h utils.h bwase.h bwa.h
bwape.o: ksw.h khash.h
bwase.o: bwase.h bntseq.h bwt.h bwtaln.h utils.h kstring.h malloc_wrap.h
bwase.o: bwa.h ksw.h
bwaseqio.o: bwtaln.h bwt.h utils.h bamlite.h malloc_wrap.h kseq.h
bwt.o: utils.h bwt.h kvec.h malloc_wrap.h
bwt_gen.o: QSufSort.h malloc_wrap.h
bwt_lite.o: bwt_lite.h malloc_wrap.h
bwtaln.o: bwtaln.h bwt.h bwtgap.h utils.h bwa.h bntseq.h malloc_wrap.h
bwtgap.o: bwtgap.h bwt.h bwtaln.h malloc_wrap.h
bwtindex.o: bntseq.h bwt.h utils.h malloc_wrap.h
bwtsw2_aux.o: bntseq.h bwt_lite.h utils.h bwtsw2.h bwt.h kstring.h
bwtsw2_aux.o: malloc_wrap.h bwa.h ksw.h kseq.h ksort.h
bwtsw2_chain.o: bwtsw2.h bntseq.h bwt_lite.h bwt.h malloc_wrap.h ksort.h
bwtsw2_core.o: bwt_lite.h bwtsw2.h bntseq.h bwt.h kvec.h malloc_wrap.h
bwtsw2_core.o: khash.h ksort.h
bwtsw2_main.o: bwt.h bwtsw2.h bntseq.h bwt_lite.h utils.h bwa.h
bwtsw2_pair.o: utils.h bwt.h bntseq.h bwtsw2.h bwt_lite.h kstring.h
bwtsw2_pair.o: malloc_wrap.h ksw.h
example.o: bwamem.h bwt.h bntseq.h bwa.h kseq.h malloc_wrap.h
fastmap.o: bwa.h bntseq.h bwt.h bwamem.h kvec.h malloc_wrap.h utils.h kseq.h
is.o: malloc_wrap.h
kopen.o: malloc_wrap.h
kstring.o: kstring.h malloc_wrap.h
ksw.o: ksw.h malloc_wrap.h
main.o: utils.h
malloc_wrap.o: malloc_wrap.h
pemerge.o: ksw.h kseq.h malloc_wrap.h kstring.h bwa.h bntseq.h bwt.h utils.h
utils.o: utils.h ksort.h malloc_wrap.h kseq.h
