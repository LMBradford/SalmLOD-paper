#NOTES##############################################################################################
#No conda on Compute Canada
##Software loaded as modules in SLURM file instead

# Submit as one big job.
# the Kraken2 bacteria database is copied to SLURM_TMPDIR (rule cp_bacdb)
# the host database is also copied
# Update the host database in config file and on line 66 to match samples


#CONFIG FILE ###########################################################################################################################################################

#Define the config yaml file in the command line

#VARIABLE SETUP ########################################################################################################################################################

#Import packages for file name management
import glob #use wildcards to take in file names and maintain the name info throughout the workflow

import os #needed for pointing to location of kr2bac in rules kr2pair and kr2unpair

envvars:
  "SLURM_TMPDIR"
#Will be used in rule cp_db

#Detect wildcards from input files names
#Names must be fixed up with renamefastq.py
#Update data in config file to reflect name and filename info for project
#Project ID (ex. FS for feedspike) and sample name are used for all output file names
filename = config['pathtoinput'] + config['projID'] + "-" + config['seqtype'] + "_{name}_R1.fastq.gz"

NAME, = glob_wildcards(filename)

print(NAME)

PROJID = config['projID']

#Wildcards from config dictionaries
#Dynamically picks up list of databases and kr2 confidence levels from config
DB = list(config['dbs'].keys())
CONF=config['confidence']


#CATCH-ALL RULE ###################################################################################################################################################

rule all:
  #List all the final output files expected here.
  input:
    expand("Kr2results/" + config['projID'] + "_{name}_{db}_c{conf}_kr.txt.gz", name=NAME, db=DB, conf=CONF),
    expand("Salmonella/SSRchecks/" + config['projID'] + "_{name}_{db}_c{conf}_salmSSRhits.txt", name=NAME, db=DB, conf=CONF),
  
#REMOVE HOST READS###############################################################################################################
#Compare trimmed fastq files to database of host genome
#Remove reads matching host
#Use "cleaned" output files for database annotation

# Compare reads to host genome kr2 databases
# For chicken caeca samples, host is Gallus gallus
# For feed samples, host is Kraken 2 plant database
# Update host-genome db in config file

#Copy kr2bac database files to SLURM temporary directory
rule cp_hostdb:
  input:
    config['hostdb']
  output: directory(os.path.join(os.environ["SLURM_TMPDIR"], "kr2plant")) #change host db name if needed
  shell:
    "cp -R {input} {output}"


rule hostcheck_paired:
  input:
    paired_R1 = "Trim/" + config['projID'] + "_{name}_R1.P.fq.gz",
    paired_R2 = "Trim/" + config['projID'] + "_{name}_R2.P.fq.gz",
    hostdb = rules.cp_hostdb.output
  output:
    text = "Hostcheck/" + config['projID'] + "_{name}_paired.hostcheck_kr.txt"
  params:
    confidence = config['confidence']
  shell: "kraken2 -db {input.hostdb} \
  --paired {input.paired_R1} {input.paired_R2} \
  --use-names \
  --output {output.text} \
  --confidence {params.confidence}"

rule hostcheck_unpaired:
  input:
    unpaired = "Trim/" + config['projID'] + "_{name}_unpaired.fq.gz",
    hostdb = rules.cp_hostdb.output
  output:
    text = "Hostcheck/" + config['projID'] + "_{name}_unpaired.hostcheck_kr.txt"
  params: 
    confidence = config['confidence']
  shell: "kraken2 -db {input.hostdb} {input.unpaired} \
  --use-names \
  --output {output.text} \
  --confidence {params.confidence}"

#Concatenate reports from paired and unpaired
rule hostcheck_getIDs:
  input:
    paired = "Hostcheck/" + config['projID'] + "_{name}_paired.hostcheck_kr.txt",
    unpaired = "Hostcheck/" + config['projID'] + "_{name}_unpaired.hostcheck_kr.txt"
  output:
    "Hostcheck/" + config['projID'] + "_{name}_hostIDs.txt"
  shell:
    """
    cat {input.paired} {input.unpaired} | awk -F '\t' '$1 == "C" {{ print $2 }}' - > {output}
    """

rule remove_hostreads_pair:
  input:
    fwdp = "Trim/" + config['projID'] + "_{name}_R1.P.fq.gz",
    revp = "Trim/" + config['projID'] + "_{name}_R2.P.fq.gz",
    hostIDs = rules.hostcheck_getIDs.output
  output:
    fwd_clean = "Hostfree/" + config['projID'] + "_{name}_hostfree_R1.P.fq.gz",
    rev_clean = "Hostfree/" + config['projID'] + "_{name}_hostfree_R2.P.fq.gz"
  shell: "filterbyname.sh in1={input.fwdp} in2={input.revp} \
  names={input.hostIDs} include=f \
  out1={output.fwd_clean} out2={output.rev_clean} \
  -Xmx25g"

rule remove_hostreads_unpair:
  input:
    unpaired = "Trim/" + config['projID'] + "_{name}_unpaired.fq.gz",
    hostIDs = rules.hostcheck_getIDs.output
  output:
    unpaired_clean = "Hostfree/" + config['projID'] + "_{name}_hostfree_unpaired.fq.gz"
  shell: "filterbyname.sh in={input.unpaired} \
  names={input.hostIDs} include=f \
  out={output.unpaired_clean} \
  -Xmx25g"

#DATABASE ANNOTATION######################################################################################################################################

#Copy kr2bac database files to SLURM temporary directory
rule cp_bacdb:
  input:
    config['dbs']['kr2bac']
  output: directory(os.path.join(os.environ["SLURM_TMPDIR"], "kr2bac"))
  shell:
    "cp -R {input} {output}"


#Confidence levels and paths to databases are stored as dictionaries in config file

rule kr2pair:
  input:
    paired_R1 = "Hostfree/" + config['projID'] + "_{name}_hostfree_R1.P.fq.gz",
    paired_R2 = "Hostfree/" + config['projID'] + "_{name}_hostfree_R2.P.fq.gz",
    bac_db = rules.cp_bacdb.output
  output:
    text = temp("Kr2reports/{name}_paired.{db}_c{conf}_kr.txt"),
    report = "Kr2reports/" + config['projID'] + "_{name}_paired.{db}_c{conf}.kr2rep"
  params: 
    confidence = config['confidence']
  shell: "kraken2 -db {input.bac_db} --paired {input.paired_R1} {input.paired_R2} \
  --use-names \
  --output {output.text} \
  --confidence {params.confidence} \
  --report {output.report} --report-zero-counts "


rule kr2unpair:
  input:
    unpaired = "Hostfree/" + config['projID'] + "_{name}_hostfree_unpaired.fq.gz",
    bac_db = rules.cp_bacdb.output
  output:
    text = temp("Kr2reports/{name}_unpaired.{db}_c{conf}_kr.txt"),
    report = "Kr2reports/" + config['projID'] + "_{name}_unpaired.{db}_c{conf}.kr2rep"      
  params: 
    confidence = config['confidence']
  shell: "kraken2 -db {input.bac_db} {input.unpaired} \
  --use-names \
  --output {output.text} \
  --confidence {params.confidence} \
  --report {output.report} --report-zero-counts "


#Concatenate paired and unpaired for each library+confidence combo

rule concat_pair_unpair:
  input:
    paired = "Kr2reports/{name}_paired.{db}_c{conf}_kr.txt",
    unpaired = "Kr2reports/{name}_unpaired.{db}_c{conf}_kr.txt"
  output:
    "Kr2results/" + config['projID'] + "_{name}_{db}_c{conf}_kr.txt.gz"
  shell:
    "cat {input.paired} {input.unpaired} | gzip > {output}"


#SALMONELLA READS AND HITS###################################################################################################################

#Get data for every read that was identified as being in the Salmonella genus
rule catch_salmhits:
  input:
    "Kr2results/" + config['projID'] + "_{name}_{db}_c{conf}_kr.txt.gz"
  output:
    "Salmonella/" + config['projID'] + "_{name}_{db}_c{conf}_salmhits.txt"
  shell:
    """
    zcat {input} | awk -F '\t' '($3 ~ "Salmonella") && ($3 !~ "plasmid") && ($3 !~ "virus")' - > {output}
    """


#Extract seqs IDed as Salmonella from original metagenome files
#Output in fasta format

rule ext_salmhitIDs:
  input:
    salmhits = rules.catch_salmhits.output
  output:
    IDS = "Salmonella/" + config['projID'] + "_{name}_{db}_c{conf}_salmhitIDs.txt"
  shell:
    "cat {input.salmhits} | cut -f 2 | sort -u > {output.IDS}"


rule ext_salmhits:
  input:
    salmhitIDs = rules.ext_salmhitIDs.output.IDS,
    fwd = config['pathtoinput'] + config['projID'] + "-" + config['seqtype'] + "_{name}_R1.fastq.gz",
    rev = config['pathtoinput'] + config['projID'] + "-" + config['seqtype'] + "_{name}_R2.fastq.gz"
  output:
    fasta = "Salmonella/" + config['projID'] + "_{name}_{db}_c{conf}_salmhits.fa",
  shell:
    "filterbyname.sh in1={input.fwd} in2={input.rev} \
    names={input.salmhitIDs} include=t \
    out={output.fasta} \
    -Xmx2g"


#CONFIRM SALMONELLA HITS##############################################################################################################

#Compare reads IDed as Salmonella against a database of 403 species-specific regions of Salmonella enterica (from Laing et al 2017)
rule blastn_salmSSR:
  input:
    fasta = rules.ext_salmhits.output.fasta
  output:
    "Salmonella/SSRchecks/" + config['projID'] + "_{name}_{db}_c{conf}_salmSSRhits.txt",
  params: 
    pathtodb = config['samSSR_db'],
    max_target_seqs = 1,
    max_hsps = 1
  shell:
    "blastn -db {params.pathtodb} -query {input.fasta} -out {output} -outfmt 6 \
    -max_target_seqs {params.max_target_seqs} -max_hsps {params.max_hsps}"
