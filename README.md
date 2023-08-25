This repo holds the code used in Bradford et al.'s *Limit of detection of Salmonella ser. Enteritidis using culture-based versus culture-independent diagnostic approaches*.

# Shotgun Sequencing Analysis
Analysis of shotgun sequencing datasets is based on the pipeline established in Bradford et al.'s An Optimized Pipeline for Detection of Salmonella Sequences in Shotgun Metagenomics Datasets (BioRxiv: https://doi.org/10.1101/2023.07.27.550528). It is run through a series of custom snakemake workflows and designed to be submitted via SLURM commands on the Digital Alliance of Canada (formerly Compute Canada) HPC system. While it would be possible to run the whole workflow in a single snakemake file, it is instead divided into a few steps to make more responsible use of Compute Canada resources.

Directory setup:
In addition to the directories in this repo, add:

slurm/logs #Log files from SLURM submissions.
Library #Raw fastq files
Summary #Run summarizing scripts here

Other directories will be created during the snakemake workflows.



## Preparation steps
Rename fastq.gz files to a convention that works with snakemake's expected inputs: 
<project code>_<sequence type>_<sampleID>_R<1/2>.fastq.gz. The renamefastq.py script does this for name formats provided by the McGill sequencing centre.

## Config File
All steps of this workflow use the same config file.

The config file must be updated for each project to give the correct input file location, project ID (ex. FS for feedspike), sequence type (ex. ShotSeq), and "host" database location. This allows the snakefiles to be generalized.

## Step 1: Trim
`sbatch SLURM_step1.sh`
Submits a job based on snakefile_step1.py

Trim and quality filter reads with Trimmomatic. Concatentate files of unpaired forward and reverse reads so that they are not left out of detection analysis.

This is memory-light but time-intensive. The default slurm submission asks for 2 GB memory, 16 cores, and 3 hours of clock-time. Adjust the number of cores according to the number of input files so that everything can run in parallel. For >~16 sets of input files, consider increasing the GB.


## Step 2: Remove host reads, annotate remaining reads with Kraken2, extract putative Salmonella reads and check them against SSRs

For Feedspike project:
`sbatch SLURM_step2.sh`
Submits a job based on snakefile_step2.py

Note that the host database is copied into SLURM_TMPDIR. This is much more efficent, but means that the database used by subsequent steps is considered "new" by snakemake each time, so host removal steps are repeated if any part of the analysis has to be repeated. This loses some of the functionality of snakemake.

The main steps here are memory-intensive, especially rules kr2pair and kr2unpair, which have to load in the kraken2 bacteria database (~50 GB). The SLURM submission settings use 210 GB, 4 cores, and 16 hours of clock-time. Four rules can run in parallel, so at least 50 GB X 4 = 200 GB memory is needed. The amount of time needed varies based on input fastq file size and the job will fail if it runs out of time.

#### Substep: host read removal
Compare trimmed fastq files against a Kraken2 database; for CaecaSpike, db is made from the Gallus gallus genome. For Feedspike, the kraken 2 plant database.
Paired and unpaired read outputs from Trimmomatic (step 1) are separately compared against the host database by Kraken 2 (confidence 0.25). An awk command pulls out the read IDs of any hits from the Kraken 2 output file and stores them in a text file ({name}_hostIDs.txt). This list of names is then used by BBMAP's filterbyname.sh, which takes in the trimmed fastq files an outputs fastq files minus the host reads.

#### Substep: read annotation with kraken 2
Compared trimmed, host-free reads against the Kraken 2 bacteria database (confidence 0.25). Paired and unpaired fastq file sets are processed separately. Outputs include both a Kraken 2 output file, with one read per line, and a Kraken2 report. Reports can be compared to each other for community composition analysis. The output files are concatenated and used in the next substep.

#### Substep: extract putative Salmonella reads from Kraken2 results
Lines in the Kraken 2 output files with Salmonella (but not plasmid or virus) in the name column (i.e., anything belonging to the Salmonella genus, whether it was IDed at any lower level or not) are pulled out using awk and printed to a file. The read IDs from that file are then cut and printed to another file (ending in salmhitIDs.txt).
Sequences for putative Salmonella hits (the salmhitIDs) are pulled from the raw fastq files into fasta files using bbmap's filterbyname.

NOTE: I didn't do marker gene search in final project, can remove that step.

## Summarizing results
Simple python scripts for creating summary tables can be found in the scripts directory. Run these in the Summaries directory.
  
Run *summarize_SSRhits.py* to count the number of hits per sample.
  
Run *summarize_hostcheck.py* to count the number of host reads per sample.

Run *summarize_kr2rep.py* to get the number of unclassified reads per sample.
  
Run *summarize_kr2salm.py* to count the number of putative Salmonella hits from Kraken2 per sample.
  
Run *summarize_trimlogs.py* to get all the trimmomatic stats in one table.
  
Once all these scripts have been done, run *make_results_table.py* to read in info from all the other results files and make a single comprehensive summary table.

# 16S analysis
Analysis of 16S sequence data (both V4 and V3-V4 regions) was performed in Qiime2 v2022.11 using the following commands:

Import
`qiime tools import --type 'SampleData[PairedEndSequencesWithQuality]'  --input-path <metadata.tsv> --output-path <project>/paired-end-demux.qza --input-format PairedEndFastqManifestPhred33V2`

Trim primers
`qiime cutadapt trim-paired --i-demultiplexed-sequences paired-end-demux.qza --p-front-f ^<fwd primer> --p-front-r ^<rev primer> --p-match-read-wildcards --p-match-adapter-wildcards --o-trimmed-sequences paired-cut.qza --p-discard-untrimmed  --verbose --p-cores 16 > cutadapt-report.txt`

Primers:
| Name | Sequence (5'-3') | Target | Reference |
| --- | --- | --- | --- |
| 16S-F_515F | GTGCCAGCMGCCGCGGTAA | V4 | Caporaso, et al. ( 2011) |
| 16S-R_806R | GGACTACHVGGGTWTCTAAT | V4 | Caporaso, et al. ( 2011) |
| 16S-F_341F | CCTACGGGNGGCWGCAG | V3-V4 | Klindworth, et al. (2013) |
| 16S-R-785R | GACTACHVGGGTATCTAATCC | V3-V4 | Klindworth, et al. (2013) |


Denoising
`tsp qiime dada2 denoise-paired --i-demultiplexed-seqs paired-cut.qza --p-trunc-len-f <fwd-read-trunc> --p-trunc-len-r <rev-read-trunc> --p-min-overlap <overlap>  --p-n-threads 0 --o-representative-sequences rep-seqs.qza --o-table denoised-table.qza --o-denoising-stats denoising-stats.qza --verbose`

| Sequences | fwd trunc position | rev trunc position | overlap |
| --- | --- | --- | --- |
| V3-V4 | 260 | 190 | 12 |
| V4 | 0 (none) | 0 (none) | 4 |


Classification
Train classifier for V3-V4 region
`qiime feature-classifier extract-reads --i-sequences silva-138-99-seqs.qza --p-f-primer CCTACGGGNGGCWGCAG --p-r-primer GACTACHVGGGTATCTAATCC --o-reads silva-138-341f-785r-refseqs.qza`

`qiime feature-classifier fit-classifier-naive-bayes --i-reference-reads silva-138-341f-785r-refseqs.qza --i-reference-taxonomy silva-138-99-tax.qza --o-classifier silva-138-341f-785r-classifier.qza`

Classifier for V4: silva-138-99-515-806-nb-classifier.qza, pre-trained and provided on Qiime2 website

Classify
`qiime feature-classifier classify-sklearn --i-classifier <classifier> --i-reads rep-seqs_merged.qza --o-classification taxonomy.qza`

Remove mitochondria and chloroplasts (feed samples)
`qiime taxa filter-table --i-table denoised-table.qza --i-taxonomy taxonomy.qza --p-exclude mitochondria,chloroplast --o-filtered-table table-filtered.qza`

# Limit of Detection calculations
LOD50 and confidence intervals were calculated according to the log-log model by Wilrich and Wilrich (2009) using a, Excel tool provided online: https://www.wiwiss.fu-berlin.de/fachbereich/vwl/iso/ehemalige/wilrich/index.html

# Plots
Plots were created in R v4.2.3. Rmarkdown files and input files are in R/.

