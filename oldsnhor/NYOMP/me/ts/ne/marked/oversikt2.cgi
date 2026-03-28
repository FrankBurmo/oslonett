#!/local/bin/perl5

require "lib.pl";
$SEPARATOR = "\t";
$FILENAME = 'markedsbase.txt';
$INPUTLENGTH = 40;
@SPECFIELDS = ('beskrivelse','forkortelse','searchable','null','alignment');
@SPEC = (
	 'Status	status	meny	ikke-null	<h2>',
	 'Beliggenhet	omr	meny multi=6	null	<h2>',
	 'Lokaltype	type	meny multi=6	null	<h3>',
	 'Adresse	adr	fritekst	null	v',
	 'Kvadratmeter	kvm	ikke søkbar	null	h',
	 'Side	side	ikke søkbar	null	h',
	 'Megler/eier	megler	fritekst	null	v',
	 'Telefon	tel	ikke søkbar	null	v',
	 );


%input = &getinput;

foreach $i ($[ .. $#SPEC) {
    @field{@SPECFIELDS} = split(/$SEPARATOR/, $SPEC[$i]);
    push(@cols, $field{forkortelse});
    $overskr{$field{forkortelse}} = $field{beskrivelse};
    $null{$field{forkortelse}} = $field{null};
    $search{$field{forkortelse}} = $field{searchable};
    push(@searchable, $field{forkortelse})
	unless $field{searchable} =~ /^ikke/;
    $align{$field{forkortelse}} = $field{alignment};
}
open(FILE, $FILENAME) || &error("Kan ikke åpne markedsdatabasen $FILENAME");

&showform if $input{form};

$input{status} =~ tr/A-ZÆØÅ/a-zæøå/;
unless ($input{status} =~ /^(leie|søkes|selges)$/) {
    &printheader("Markedsoversikten");
    print qq!<font size="+1">\n!;
    print "Du må angi en av kategoriene nedenfor:\n";
    print "<ul>\n";
    print qq!<li> <a href="$ENV{SCRIPT_NAME}?status=leie">Leie</a>\n!;
    print qq!<li> <a href="$ENV{SCRIPT_NAME}?status=selges">Selges</a>\n!;
    print qq!<li> <a href="$ENV{SCRIPT_NAME}?status=søkes">Søkes</a>\n!;
    print "</ul>\n";
    &printfooter;
    exit 0;
}

open(BASE, $BASE) || &error("Kan ikke åpne link-databasen $BASE");
while (<BASE>) {
    $link{$1} = $2 if /([^%]+)%(.+)/;
}
close BASE;

&printheader("Markedsoversikten: $input{status}");

$input{status} =~ tr/a-zæøå/A-ZÆØÅ/;

print qq!<table border="0">\n!;
LINE:
while (<FILE>) {
    @tmp{@cols} = split(/$SEPARATOR/);
    foreach $key (@searchable) {
	next LINE if length $input{$key} && $tmp{$key} !~ /$input{$key}/i;
    }

    if ($tmp{omr} ne $lastomr) {
	print qq!<tr><th colspan="5" align="center">!;
	print qq!<font size="+2"><b>$tmp{omr}</b></font><br>!;
	print "<em><b>$tmp{type}</b></em></th>\n";
	$lastomr = $tmp{omr};
	$lasttype = $tmp{type};
    } elsif ($tmp{type} ne $lasttype) {
	print qq!<tr><th colspan="5" align="center">!;
	print qq!<em><b>$tmp{type}</b></em></th>!;
	$lasttype = $tmp{type};
    }
    unless ($overskr++) {
	# Skriv ut overskriftene kun én gang...
	print "<tr><td><em>";
	print join("</em></td><td><em>",
		   @overskr{adr,kvm,side,megler,tel});
	print "</em></td>\n";
    }
    print "<tr>";
    foreach $key ('adr', 'kvm', 'side', 'megler', 'tel') {
	if ($align{$key} =~ /^h/i) {
	    print qq!<td align="right">!;
	} else {
	    print "<td>";
	}
	while (($k,$v) = each %link) {
	    last if $tmp{$key} =~ s!($k)!<a href="$v">$1</a>!;
	}
#	$tmp{$key} = $link{$tmp{$key}} if length $link{$tmp{$key}};
	print "$tmp{$key}</td>\n";
    }
}
print "</table>\n";
close FILE;


&printfooter;

exit 0;


sub showform {
    &printheader("Markedsoversikten: søk");
    while (<FILE>) {
	@tmp{@cols} = split(/$SEPARATOR/);
	foreach (@searchable) {
	    $count{"$_: $tmp{$_}"}++ if $search{$_} =~ /meny|checkbox/i;
	}
    }
    close FILE;

    print qq!<form action="$ENV{SCRIPT_NAME}" method="POST">\n!;
    print qq!<table border="0"><dl>\n!;
    foreach $c (@cols) {
	next if $search{$c} =~ /^ikke/i;
	print qq!<tr><td><dt><font size="+1">$overskr{$c}: </font></td>\n!;
	print "<dd> <td>";
	if ($search{$c} =~ /^fritekst/i) {
	    print qq!<input name="$c" size="$INPUTLENGTH"><br>\n!;
	} elsif ($search{$c} =~ /^checkbox/i) {
	    print qq!<table border="0">\n!;
	    $counter = 0;
	    foreach (sort keys %count) {
		next unless s/^$c:\s*//;
		print "<tr>\n" unless $counter++ % 2;
		print qq!<td><input type="checkbox" name="$c" value="$_"> !;
		print "$_</td>\n";
	    }
	    print "</table>\n";
	} elsif ($search{$c} =~ /^meny/i) {
	    $multi = "multiple size = $1" if $search{$c} =~ /multi=(\d+)/;
	    print qq!<select $multi name="$c">\n!;
	    print qq!<option value=""> Vilkårlig\n! if $null{$c} =~ /^null/;
	    foreach (sort keys %count) {
		next unless s/^$c:\s*//;
		print qq!<option value="$_"> $_\n!;
	    }
	    print "</select><br>\n";
	}
	print "</td>\n",
    }
    print <<EOT;
<tr><dt><td><input type="submit" value=" Søk "></td>
</dl></table>
</form>
EOT

    &printfooter;
    exit 0;
}

