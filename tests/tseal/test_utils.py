
import os

MiniRefMemDir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mini_ref',  'bwamem_0.7.8'))
MiniRefMemPath = os.path.join(MiniRefMemDir, 'mini_ref.fasta')
MiniRefReadsPrq = os.path.join(MiniRefMemDir, '..', 'mini_ref_seqs.prq')

# we cache the list produced by get_mini_ref_seqs
_mini_ref_seqs_prq = None

def read_seqs(filename):
    """
    Read a PRQ file of sequences::

        ID	SEQ1	Q1	SEQ2	Q2
    """
    with open(filename) as f:
        # use a tuple since it's immutable
        seqs = tuple([ line.rstrip('\n').split('\t') for line in f ])
    return seqs

def get_mini_ref_seqs():
    global _mini_ref_seqs_prq
    if _mini_ref_seqs_prq is None:
        _mini_ref_seqs_prq = read_seqs(MiniRefReadsPrq)
    return _mini_ref_seqs_prq

def rapi_mini_ref_seqs_sam_no_header():
    return (
    "read_00	65	chr1	32461	60	60M	=	32581	121	AAAACTGACCCACACAGAAAAACTAATTGTGAGAACCAATATTATACTAAATTCATTTGA	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE	NM:i:0	AS:i:60	MD:Z:60	XS:i:0\n"
    "read_00	129	chr1	32581	60	60M	=	32461	-121	CAAAAGTTAACCCATATGGAATGCAATGGAGGAAATCAATGACATATCAGATCTAGAAAC	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE	NM:i:0	AS:i:60	MD:Z:60	XS:i:0\n"
    "del3_read_00	65	chr1	32458	60	11M3D49M	=	32581	124	TAGAAAACTGAACACAGAAAAACTAATTGTGAGAACCAATATTATACTAAATTCATTTGA	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE	NM:i:3	AS:i:51	MD:Z:11^CCC49	XS:i:0\n"
    "del3_read_00	129	chr1	32581	60	60M	=	32458	-124	CAAAAGTTAACCCATATGGAATGCAATGGAGGAAATCAATGACATATCAGATCTAGAAAC	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE	NM:i:0	AS:i:60	MD:Z:60	XS:i:0\n"
    "ins3_read_00	65	chr1	32464	60	13M3I44M	=	32581	118	ACTGACCCACACAGGGGAAAAACTAATTGTGAGAACCAATATTATACTAAATTCATTTGA	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE	NM:i:3	AS:i:48	MD:Z:57	XS:i:0\n"
    "ins3_read_00	129	chr1	32581	60	60M	=	32464	-118	CAAAAGTTAACCCATATGGAATGCAATGGAGGAAATCAATGACATATCAGATCTAGAAAC	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE	NM:i:0	AS:i:60	MD:Z:60	XS:i:0\n"
    "sub2_read_01	65	chr1	27121	60	60M	=	27241	121	GTGCAGATCCCATATGTCCAATAAAAAGGTAAGATCCAAACTCAGATGTCCTATGAGTAT	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE	NM:i:2	AS:i:50	MD:Z:15T16C27	XS:i:0\n"
    "sub2_read_01	129	chr1	27241	60	60M	=	27121	-121	TCACTAGTTATTTTTAAAATAGGATTGCATGTTGAAATGATAATCTTTTGGATATATTGG	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE	NM:i:0	AS:i:60	MD:Z:60	XS:i:0\n"
    "read_00_rev	113	chr1	32461	60	60M	=	32581	121	AAAACTGACCCACACAGAAAAACTAATTGTGAGAACCAATATTATACTAAATTCATTTGA	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEES	NM:i:0	AS:i:60	MD:Z:60	XS:i:0\n"
    "read_00_rev	177	chr1	32581	60	60M	=	32461	-121	CAAAAGTTAACCCATATGGAATGCAATGGAGGAAATCAATGACATATCAGATCTAGAAAC	EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEES	NM:i:0	AS:i:60	MD:Z:60	XS:i:0")

_complement = {
    'A':'T',
    'G':'C',
    'C':'G',
    'T':'A',
    'N':'N',
    'a':'t',
    'g':'c',
    'c':'g',
    't':'a',
    'n':'n'
}

def rev_complement(seq):
    return ''.join( _complement[base] for base in seq[::-1] )
