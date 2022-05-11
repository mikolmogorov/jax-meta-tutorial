Metagenomic assembly using metaFlye
===================================

This tutorial is a part of the Long read sequencing workshop, held at
The Jackson Laboratory for Genomic Medicine in May 2022. Presented
by Mikhail Kolmogorov.

Prerequsites
------------

The tutorial requires a Linux or Mac machine with at least 16 Gb of RAM and 5 Gb disk space.
You can use either a laptop/desctop or remote computational server. If you are using 
a server, you will need to copy assembly results back to the local machine
to visualize them using Bandage and Quast.

If you don't have it already, download and install bioconda as described [here](https://bioconda.github.io/user/install.html).

Instal the required tools in a separate environemnt

```
conda create -n jax-meta-tutorial flye=2.9 quast bandage checkm-genome biopython wget
conda activate jax-meta-tutorial
```


Assembling mock bacterial community from ONT data
-------------------------------------------------

In this part, we will be using Oxford Nanopore sequencing of a mock bacterial
community, originally published by [Nicholls et al.](https://academic.oup.com/gigascience/article/8/5/giz043/5486468).
We will be using the version with even bacterial distribution. The community also contains
two yeast genomes, but we will ignore them for the sake of simplicity.

For the convenience, I am providing a downsampled version of the dataset
(total read size ~1Gb) that was also re-basecalled with the recent
basecaller (Guppy 5).

To download reads, use:

```
wget XXX_zendo/Nicholls_ont_guppy5_1gb.fastq.gz
```

Then, run metaFlye as follows:

```
flye --nano-hq Nicholls_ont_guppy5_1gb.fastq.gz -o flye_ont -t 30 --meta
```

This step may take considerable time, depending on the available resorces.
Feel free to adjust `-t` parameter accoding to the number of CPUs on your machine.
Using 30 threads, it takes about 30 minutes to run the assembly.

Once assembly is done, time to visualize it! Open `flye/assembly_graph.gfa`
using `Bandage`. If you were using a remote server for computation, you'll need
to download the graph file to local machine first.

This is how your assembly might look like, visualized by Bandage:

![Bandageont](ont_graph.png)

Notice multiple circular chromosomes, that likely correspond to
complete bacterial genomes. There are also two pairs of bacterial
genomes that have shared long repeats that were unresolved.
Because of that, these genomes are "glued" on the graph, instead of forming
separate circular contigs.

Can we verify that the assemblies indeed represent
the correct genomes? Yes, because we are lucky to have reference
genomes for this particular community.

Download and extract reference genomes as follows:

```
wget ZENODO_Nicholls_ont_refs.tar.gz
tar -xvf Nicholls_ont_refs.tar.gz
```

Now, use metaQUAST to analyze the assembly:

```
metaquast.py flye_ont/assembly.fasta -R Nicholls_ont_refs -o quast_ont
```

The best way to look at Quast results is though their interactive web browser report.
You can open `quast_ont/report.html` to do that. Alternatively, you can examine
the text report as follows. First of all, let's look at genome completion rates:

```
cat quast_ont/summary/TXT/Genome_fraction.txt 
```

Which outputs:
```
Assemblies           assembly
155_P.aeruginosa     99.998  
220_E.coli           100.000 
227_S.enterica       99.930  
445_S.aureus         99.726  
464_E.faecalis       100.000 
516_B.subtilis       99.797  
525_L.monocytogenes  99.963  
528_L.fermentum      100.000 
```

All bacteria have 99%+ sequence recovered, nice!

Next, let's check base-level accuracy. You can see the number
of indels and missmatches for each bacteria here:

```
cat quast_ont/summary/TXT/num_indels_per_100_kbp.txt
cat quast_ont/summary/TXT/num_mismatches_per_100_kbp.txt
```

For example, for `L.monocytogenes`, the total number of
mismatches + indels is about 10 per 100kb, which translates
into ~QV40. Not bad!

Finally, how complete our assmeblies are? And what to do if we are analysing
a real metagenome and don't have references? In this case, CheckM
could be helpful.

First, download the reference database, and set it up:

```
wget https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz
mkdir checkm_data && tar -xvf checkm_data_2015_01_16.tar.gz -C checkm_data
checkm data setRoot `pwd`/checkm_data
```

CheckM was designed to work with metagenomic bins (MAGs), however
in our situation our contigs are already as good as MAGs (if not better).
Therefore, we will create "fake" bins with only a single contig within each bin.
To make it convenient, I've prepared a converter script for you.
The command below converts all contigs longer than 100kb into bins.

```
wget https://raw.githubusercontent.com/fenderglass/jax-meta-tutorial/main/create_meta_bins.py
python create_meta_bins.py flye_ont/assembly.fasta 100000 checkm_bins
```

Now, we are ready to run CheckM:

```
checkm lineage_wf -x fasta checkm_bins checkm_out -t 10 --pplacer_threads 10 -f checkm_out/qa_table.txt
cat checkm/qa_table.txt
```

You might see the following summary:

```
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Bin Id                Marker lineage           # genomes   # markers   # marker sets    0     1     2   3   4   5+   Completeness   Contamination   Strain heterogeneity  
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  contig_183         g__Bacillus (UID865)            36         1200          269         8    1190   2   0   0   0       99.64            0.25               0.00          
  contig_34      o__Lactobacillales (UID544)        293         475           267         2    472    1   0   0   0       99.53            0.19               0.00          
  contig_51    f__Enterobacteriaceae (UID5139)      119         1169          340         8    1160   1   0   0   0       99.31            0.04               0.00          
  contig_32      o__Pseudomonadales (UID4488)       185         813           308         5    803    5   0   0   0       99.00            0.61               0.00          
  contig_19    f__Enterobacteriaceae (UID5124)      134         1173          336         10   1154   9   0   0   0       98.96            0.20              77.78          
  contig_156     o__Lactobacillales (UID355)        490         334           183         4    329    1   0   0   0       98.63            0.55              100.00         
  contig_72       g__Staphylococcus (UID301)         45         940           178         9    930    1   0   0   0       98.50            0.08               0.00          
  contig_99          c__Bacilli (UID354)            515         329           183        103   226    0   0   0   0       74.32            0.00               0.00          
  contig_97          c__Bacilli (UID354)            515         329           183        259    70    0   0   0   0       15.30            0.00               0.00          
  contig_98              root (UID1)                5656         56            24         55    1     0   0   0   0        4.17            0.00               0.00          
  contig_300             root (UID1)                5656         56            24         56    0     0   0   0   0        0.00            0.00               0.00          
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

You can see that 7 contigs represent bacterial genomes with 98%+ completeness. And looks like one bacteria was
split into two large contigs (contig_99 and contig_97). Must be that one tangle!

Assembling mock bacterial community from PacBio HiFi data
---------------------------------------------------------

The previous mock community consisted of different bacterial species
and mostly different genera. In a real metagenome, we commonly see many
closely-related species or strains. To model this, PacBio
recently released [HiFi sequencing](https://www.ncbi.nlm.nih.gov/sra/SRR13128014) 
of mock bacterial community with 5 E.coli strains, among other species. Let's give it a try!

As before, I've prepared a downsampled version here:

```
wget XXX_SRR13128014_hifi_1gb.fastq.gz
```

Assembly using metaFlye's hifi mode:

```
flye --pacbio-hifi SRR13128014_hifi_1gb.fastq.gz -o flye_hifi -t 30 --meta
```

If you visualize the assembly with Bandage as before, you'll notice that some
tangled components, in addition to nicely assembled circular chromosomes.

![Bandagehifi](hifi_graph.png)


Similarly, you can run QUAST analysis with the following references:
```
wget YYY_SRR13128014_refs.tar.gz
```
