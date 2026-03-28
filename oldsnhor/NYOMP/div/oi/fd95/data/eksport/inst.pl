#!/local/bin/perl5

while (<ARGV>) {
    print "Institusjon: $1\n\n"
	if ( /institusjon.+value="(.+)"/i );
    print &format($1)
	if ( /Beskrivelse.+ with ``(.+)`/i );
    print "\n\n", &format($1), "\n\n"
	if ( /Deltagelse.+ with ``(.+)`/i );
}

print "\n\n\n";


sub format {
    local($text) = $_[0];

    $text =~ s/(.{50,70})\s+/$1\n/g;

    return $text;
}
