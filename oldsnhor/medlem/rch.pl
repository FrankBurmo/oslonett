#!/local/bin/perl

$ch_to=$ARGV[0];	

$outfile="/home/stovner/a/kentv/tmp.html";
undef($/);

open(CHFILE, "<$ch_to") || die "Not able to open $ch_to...\n";

$sub=<CHFILE>;


&dodir('.');


sub dodir {

    local($dir,$nlink) = @_;
    local($dev,$ino,$mode,$subcount);

    ($dev,$ino,$mode,$nlink) = stat('.') unless $nlink;


    opendir(DIR,'.') || die "Can't open $dir";
    local(@filenames) = readdir(DIR);
    closedir(DIR);

    if ($nlink == 2) {
	for (@filenames) {
	    next if $_ eq '.';
	    next if $_ eq '..';
	    $name2 = $_;
	    $name = "$dir/$_";
	    if (substr($name,-5) eq ".html") {
		print $name,"\n";
		&processChange($name2);
	    }

	}
    }
    else {
	$subcount=$nlink-2;
	for (@filenames) {
	    next if $_ eq '.';
	    next if $_ eq '..';
	    $name2 = $_;
	    $name = "$dir/$_";
	    if (substr($name,-5) eq ".html") {
		print $name,"\n";	    
		&processChange($name2);
		next;
	    }


	    next if $subcount == 0; # Seen all subdirs?

	    # Get link count and check for directories

	    ($dev,$ino,$mode,$nlink) = lstat($_);
	    next unless -d $_;

	    #It really is a directory, so do it recursively.

	    chdir $_ || die "Can't cd to $name";
	    &dodir($name,$nlink);
	    chdir '..';
	    -$subcount;
	}
    }
}


sub processChange {

    $name=$_[0];


    open(OUTFILE, ">$outfile") || die "Not able to open $outfile ...\n";
    print "NOT ABLE TO OPEN INFILE!\n" unless open (INFILE, "<$name");

    $fil ="";
    $fil = <INFILE>; 
    $fil =~ s#</BODY>.*</HTML>#$sub#i;

    print OUTFILE $fil;

    close (OUTFILE);
    close (INFILE);
    system "mv $outfile $name" || die "Could not create $this_file";
    
    system "chmod g+rxw $name";
    system "chmod a+rx $name";

}




