/*
Copyright (C) 2011-2012 CRS4.

This file is part of Seal.

Seal is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seal is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seal.  If not, see <http://www.gnu.org/licenses/>.

Imported from bwa (http://bio-bwa.sourceforge.net).  Modified
by: Simone Leo <simone.leo@crs4.it>, Luca Pireddu
<luca.pireddu@crs4.it>, Gianluigi Zanetti <gianluigi.zanetti@crs4.it>.

*/

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "bwt.h"
#include "utils.h"
#include <sys/mman.h>
#include <fcntl.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>


#ifdef BWT_ENABLE_MMAP

/** magic number for our modified rsax and sax files */
const uint32_t BWA_MMAP_SA_MAGIC = ('B' | 'W' << 8 | 'A' << 16 | 'T' << 24);

void* bwt_mmap_file(const char *fn, size_t size) {
	int fd = open(fn, O_RDONLY);
	xassert(fd > -1, "Cannot open file");
	
	struct stat buf;
	int s = fstat(fd, &buf);
	xassert(s > -1, "cannot stat file");

	off_t st_size = buf.st_size;
	if (size > 0) {
		xassert(st_size >= size, "bad file size");
		st_size = size;
	}

	// mmap flags:
	// MAP_PRIVATE: copy-on-write mapping. Writes not propagated to file. Our mapping is read-only,
	//              so this setting seems natural.
	// MAP_POPULATE: prefault page tables for mapping.  Use read-ahead. Only supported for MAP_PRIVATE
	// MAP_HUGETLB: use huge pages.  Manual says it's only supported since kernel ver. 2.6.32 
	//              and requires special system configuration.
	// MAP_NORESERVE: don't reserve swap space
	int map_flags = MAP_PRIVATE | MAP_POPULATE | MAP_NORESERVE;
	void* m = mmap(0, st_size, PROT_READ, map_flags, fd, 0);
	xassert(m != MAP_FAILED, "cannot mmap");
	madvise(m, st_size, MADV_WILLNEED);
	return m;
}

uint8_t *bwt_restore_reference_mmap_helper(const char *fn, size_t map_size) {
	return (uint8_t*) bwt_mmap_file(fn, map_size);
}

bwt_t *bwt_restore_bwt_mmap(const char *fn)
{
	void* m = bwt_mmap_file(fn, 0);

	int fd = open(fn, O_RDONLY);
	xassert(fd > -1, "Cannot open file");
	
	struct stat buf;
	int s = fstat(fd, &buf);
	xassert(s > -1, "cannot stat file");

	bwt_t *bwt;
	bwt = (bwt_t*)calloc(1, sizeof(bwt_t));
	bwt->bwt_size = (buf.st_size - sizeof(bwtint_t)*5) >> 2;
	bwt->primary = ((bwtint_t*)m)[0];
	bwt->bwt = (uint32_t*)&((bwtint_t*)m)[5];
	size_t i;
	for(i = 1; i < 5; ++i) {
	  bwt->L2[i] = ((bwtint_t*)m)[i];
	}
	bwt->seq_len = bwt->L2[4];
	bwt_gen_cnt_table(bwt);
	return bwt;
}

void bwt_restore_sa_mmap(const char *fn, bwt_t *bwt)
{
	void* m = bwt_mmap_file(fn, 0);

	int magic = ((bwtint_t*)m)[0];
	xassert(magic == BWA_MMAP_SA_MAGIC, "incompatible file identifier in .sax or .rsax");

	bwtint_t primary = ((bwtint_t*)m)[1];
	xassert(primary == bwt->primary, 
		"SA-BWT inconsistency: primary is not the same.");
	bwt->sa_intv = ((bwtint_t*)m)[6];
	primary = ((bwtint_t*)m)[7];
	xassert(primary == bwt->seq_len, 
		"SA-BWT inconsistency: seq_len is not the same.");
	bwt->n_sa = (bwt->seq_len + bwt->sa_intv) / bwt->sa_intv;

	bwt->sa = &((bwtint_t*)m)[8];
}

void bwt_destroy_mmap(bwt_t *bwt)
{
	if (bwt == 0) return;
	//free(bwt->sa); 
	//free(bwt->bwt);
	free(bwt);
}

#endif
