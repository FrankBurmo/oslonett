#!/local/bin/perl

$outfile="./tmp.html";

&dodir('.');

sub dodir {

    $ch_from=$ARGV[0];		# Get first parameter - string to change FROM
    $ch_to=$ARGV[$#ARGV];	# Change to this one...


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
	    $name = "$dir/$_";
	    if (substr($name,-5) eq ".html") {
		print $name,"\n";
		&processChange($name);
	    }

	}
    }
    else {
	$subcount=$nlink-2;
	for (@filenames) {
	    next if $_ eq '.';
	    next if $_ eq '..';
	    $name = "$dir/$_";
	    if (substr($name,-5) eq ".html") {
		print $name,"\n";
		&processChange($name);
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

    open(INFILE, "<$name");
    open(OUTFILE, ">$outfile") || die "Not able to open $outfile ...\n";;

    while (<INFILE>) {
	$_=~ s/$ch_from/$ch_to/;
	print OUTFILE;
    }
    close (OUTFILE);
    close (INFILE);

    `mv $outfile $name`;
    `chmod g+rxw $name`;
    `chmod a+rx $name`;

}


