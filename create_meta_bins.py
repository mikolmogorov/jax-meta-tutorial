#!/usr/bin/env python3

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import sys
import os


if len(sys.argv) != 4:
    print("Usage: create_bins.py input_fasta min_len out_dir")
    sys.exit(1)

filename = sys.argv[1]
min_len = int(sys.argv[2])
out_dir = sys.argv[3]

if not os.path.isdir(out_dir):
    os.mkdir(out_dir)

for seq in SeqIO.parse(filename, "fasta"):
    if len(seq.seq) > min_len:
        out_file = open(os.path.join(out_dir, "{0}.fasta".format(seq.id)), "w")

        SeqIO.write(seq, out_file, "fasta")
