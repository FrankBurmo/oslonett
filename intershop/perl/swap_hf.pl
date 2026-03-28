#!/local/bin/perl


#
# Bytter ut header/footer områder i en fil. Disse er merket med 
# <!-- TEST_BEGIN -->
# og
# <!-- TEST_END --> 
# hvor TEST kan være hva som helst. IKKE angi _BEGIN eller _END i kommandlinljen.
# Alt i mellom disse to tagene byttes ut med innholdet
# av den spesifiserte filen:
#
# swap_hf RS nyheader.txt index.html
#
# vil lete i indes.html efter RS_BEGIN og RS_END, og erstatte det mellomværende 
# med nyheader.txt
#
# Resultatet havner i index.html
#
#
# (c) kentv 10-95
#

$path=$ENV{'PWD'};

if ($#ARGV < 2) {
    print "\nswap_hf: area_descriptor    header-footer file    files... \n";
    die;
}


# Which part of the text do we want to change?
$area_begin=join("",$ARGV[0],"_BEGIN");
$area_end=join("",$ARGV[0],"_END");


# This is the input-file (footer or header)
$in_file=$ARGV[1];

# and this is the file to be changed
$out_file=$ARGV[2];

# and this is the temporary file
$tmp_file=join("",$path,"/swap.tmp");

open(OUTFILE, ">$tmp_file") || die "Not able to open $tmp_file...\n";
open(SWAPFILE, "<$in_file") || die "Not able to open $in_file...\n";
open(INFILE, "<$out_file") || die "Not able to open $out_file...\n";

# Copy the top of the text _before_ the swap
while (<INFILE>) {    	     
    print OUTFILE $_;
    last if /$area_begin/;
}

# Copy in from specified file
while (<SWAPFILE>) {
    print OUTFILE $_;
}				

# Skip the part of the old file that we don't want
while (<INFILE>) {
    last if /$area_end/;
}

# Need a newline character
print OUTFILE "\n";

# Copy the delimiter and
print OUTFILE $_;

# the rest of the file 
while (<INFILE>) {
    print OUTFILE $_;
}

# Clean up...
close (INFILE);
close (OUTFILE);
close (SWAPFILE);

`mv $tmp_file $out_file`;
`chmod g+rxw $out_file`;
`chmod a+rx $out_file`;




