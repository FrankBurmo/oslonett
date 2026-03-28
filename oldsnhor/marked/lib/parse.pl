
# Module to parse DATA files

package main;

sub parse
{
    my($f) = @_;
    my $entry = {};
    open(F, $f) or die "Can't open $f: $1";
    while (<F>) {
	chomp;
	last if /^\s*$/;
	my($k, $v) = split(/:\s+/, $_, 2);
	$k = lc $k;
	$entry->{$k} = $v;
    }
    $entry->{text} = "";
    while (<F>) {
	$entry->{text} .= $_;
    }
    close(F);
    return $entry;
}


1;
