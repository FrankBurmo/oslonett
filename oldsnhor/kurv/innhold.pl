#!/local/bin/perl5

$id = shift @ARGV;

exit 0 unless length $id;

open(KURV, "/local/www/kurv/kunder/kurv-$id.data") || exit 0;
while (<KURV>) {
    ($vareid) = /^(\S+)/;
    next unless length $vareid;
    print "$vareid\n";
}
