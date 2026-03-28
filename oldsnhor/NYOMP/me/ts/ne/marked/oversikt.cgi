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
    print <<EOT;
<font size="+1">
For å se alle registrerte eiendommer kan du velge en av link'ene
nedenfor:
<ul>
<li> <a href="$ENV{SCRIPT_NAME}?status=leie">Leie</a>
<li> <a href="$ENV{SCRIPT_NAME}?status=selges">Selges</a>
<li> <a href="$ENV{SCRIPT_NAME}?status=søkes">Søkes</a>
</ul>

Dersom du vil begrense listen geografisk eller etter lokaltype, kan
du bruke <a href="$ENV{SCRIPT_NAME}?form=1">søkegrensesnittet til
markedsoversikten</a>. Via søkesiden kan du også søke etter
registrerte eiendommer med angitt adresse og etter alle eiendommer
registrert på en bestemt megler/eier.

EOT
    &printfooter;
    exit 0;
}

open(BASE, $BASE) || &error("Kan ikke åpne link-databasen $BASE");
while (<BASE>) {
    $link{$1} = $2 if /([^%]+)%(.+)/;
}
close BASE;
@linkkeys = keys %link;

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
	print qq!<br><font size="+2"><b>$tmp{omr}</b></font><br>!;
	print "<br><em><b>$tmp{type}</b></em></th>\n";
	$lastomr = $tmp{omr};
	$lasttype = $tmp{type};
    } elsif ($tmp{type} ne $lasttype) {
	print qq!<tr><th colspan="5" align="center">!;
	print qq!<br><em><b>$tmp{type}</b></em></th>!;
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
	if ($key eq 'megler' || $key eq 'adr') {
	  MEGLER:
	    foreach $k (@linkkeys) {
		next unless length $link{$k};
		last MEGLER
		    if $tmp{$key} =~ s!($k)!<a href="$link{$k}">$1</a>!i;
	    }
	}
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
	    $count{"$_: $tmp{$_}"}++ if $search{$_} =~ /meny/i;
	}
    }
    close FILE;

    print <<EOT;

<form action="$ENV{SCRIPT_NAME}" method="POST">
<table><dl>
EOT
    foreach $c (@cols) {
	next if $search{$c} =~ /^ikke/i;
	print qq!<tr><td><dt><font size="+1">$overskr{$c}: </font></td>\n!;
	print "<td> <dd>";
	if ($search{$c} =~ /^fritekst/i) {
	    print qq!<input name="$c" size="$INPUTLENGTH"><br>\n!;
	} elsif ($search{$c} =~ /^meny/i) {
	    $multi = "multiple size = $1" if $search{$c} =~ /multi=(\d+)/;
	    print qq!<select $multi name="$c">\n!;
	    foreach (sort keys %count) {
		next unless s/^$c:\s*//;
		print qq!<option value="$_"> $_\n!;
	    }
	    print "</select><br>\n";
	}
	print "</td>\n",
    }
    print <<EOT;
<tr><dt><td align="center" colspan="2">
<input type="submit" value=" Søk ">
<input type="reset" value=" Nytt skjema ">
</td>
</dl></table>
</form>
EOT

    &printfooter;
    exit 0;
}

