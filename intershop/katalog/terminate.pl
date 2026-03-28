#!/local/bin/perl5

$file=$ARGV[1];
print $file;
open(FILE, "<$file") || die "Får ikke modifisert $file";

while (<FILE>) {
    s/^(.*)$/$1\$\$/;
    print $_;
}

close(FILE);

exit(0);
