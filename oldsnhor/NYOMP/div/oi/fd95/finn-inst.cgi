#!/local/bin/perl
#
# Program for å generere liste eller enkeltutskrift for deltager-
# institusjoner under Forskingsdagene '95.
#
# KGN, 14.7.95. Sist endret: 14.7.95

print "Content-type: text/html\n\n";

require "/local/www/div/oi/fd95/adm/fd-lib.pl";

@fields = ("Nummer", "Institusjon", "Kategori", "Maskin");
%fieldname = ("Nummer", "Registeringsnummer",
	      "Kategori", "Kategori",
	      "Institusjon", "Institusjon");


%input = &getinput;
&regexp_escape($input{'Institusjon'}) if $input{'Institujon'};

&viskategorier unless join("",@input{keys %fieldname});

@matches = &dosearch(%input);

if (!@matches) {
    print &header("Søket ga ingen treff i databasen");

    foreach $key (sort keys %input) {
        next unless $fieldname{$key};
        push(@lines, " <dt> <b>$fieldname{$key}</b>\n <dd> $input{$key}\n");
    }
    if (@lines) {
	print "<blockquote>\n<hr noshade size=\"2\">\n";
	printf("Søkepara%s var som følger:\n",
	       (@lines == 1) ? "meteren" : "metrene");
	print "<dl>\n@lines\n</dl>\n<hr noshade size=\"2\">\n</blockquote>\n";
    }
    exit 0;

} else {
    print &header("Søkeresultat: liste over institusjoner");
    print "<ul>\n";

    sub byinst { $datakey[$a] cmp $datakey[$b]; }

    foreach (@matches) { 
	@entry{@fields} = split($fieldsep);
	push(@datakey, $entry{'Institusjon'});
    }

    foreach (@matches[sort byinst $[ .. $#matches]) {
	@entry{@fields} = split($fieldsep);
	printf(" <li> <a href=\"$insturl/inst%04d.html\">%s</a> (Kategori: %s)\n",
	       @entry{'Nummer', 'Institusjon', 'Kategori'});
    }
    print "</ul>\n", &footer;
}

exit 0;



sub viskategorier {
    open(FILE, $instindeks)
	|| &error("Kunne ikke åpne indeksfilen ($instindeks)");
    while (<FILE>) {
	@entry{@fields} = split($fieldsep, $_);
	$teller{$entry{'Kategori'}}++;
    }
    close(FILE);

    print &header("Oversikt over deltagerinstitusjoner");

    print <<EOT;

Institusjonene som deltar i FD\'95 er gruppert i kategorier. Listen
nedenfor viser hvilke kategorier som er i bruk i databasen. Tallet i
parentes angir hvor mange institusjoner som er registrert under hver
kategori.
<p>

Klikk på en av kategoriene nedenfor for å se hvilke institusjoner som
er med i denne kategorien.

<ul>
EOT
    for $kategori (sort keys %teller) {
	$kode = $kategori;
	$kode =~ s/([ \+\?\%])/sprintf("%%%02x",unpack("c",$1))/ge;
	$kode =~ s/($specialcase)/sprintf("%%%02X",unpack("c",$1)>0?unpack("c", $1) : unpack("c", $1) + 256)/ge;
	print qq@ <li> <a href="finn-inst.cgi?Kategori=$kode">$kategori</a> ($teller{$kategori})\n@;
    }
    print "</ul>\n";

    print <<EOT;

Det er også mulig å vise en alfabetisk <a
href="finn-inst.cgi?Institusjon=.*">liste over samtlige
deltakerinstitusjoner</a>. Denne listen kan imidlertid bli lang og
vanskelig å finne fram i. Bruk heller søkegrensesnittet nedenfor
dersom du leter etter en spesiell institusjon.
<p>
<hr noshade size=2>
<p>

<form method="POST" actoin"finn-inst.cgi">
<center>
<table border="6" cellpadding="5" cellspacing="5">
<tr>
  <td align="middle">
    <h2>Søk etter institusjoner</h2>
  </td>
<p>

<tr>
  <td>
    Institusjonens navn: <input name="Institusjon" size="50">
    <input type="submit" value="Start søk">
    <p>
    Her kan du skrive inn fullt navn eller del av navn til den eller
    de institusjonene du leter etter. Vil du søke etter flere institusjoner
    på en gang, setter du tegnet | mellom søkeuttrykkene.
  </td>
<p>

</table>
</center>
</form>

EOT

    print &footer;
    exit 0;
}


sub dosearch {
    local(%input) = @_;
    local(@matches);

    open(FILE, $instindeks)
	|| &error("Kunne ikke åpne indeksfilen ($instindeks)");
    while (<FILE>) {
	@entry{@fields} = split($fieldsep, $_);

	push(@matches, join($fieldsep, @entry{@fields}))
	    if ( (!$input{'Nummer'}
		  || ($entry{'Nummer'} eq $input{'Nummer'}))
		&& (!$input{'Institusjon'}
		    || ($entry{'Institusjon'} =~ /$input{'Institusjon'}/i))
		&& (!$input{'Kategori'}
		    || ($entry{'Kategori'} eq $input{'Kategori'})));
    }
    close(FILE);

    @matches;
}



    
sub showlist {
    local(@arrangementer) = @_;


    if (!@arrangementer) {
	print &header("Søket ga ingen treff i databasen");
	&printparams(%input);
    } else {
	print &header("Søkeresultat: liste over arrangementer");

	foreach (@arrangementer) {
	    @entry{@fields} = split($fieldsep, $_);
	    $entry{'Fylke'} =~ tr/a-zæøåÆØÅ/A-Z[\\][\\]/;
	    $entry{'Arrangement'} =~ tr/a-zæøåÆØÅ/A-Z[\\][\\]/;
	    push(@datakeys, sprintf("%-6s%-20s%-54s",
				    @entry{'Dato', 'Fylke', 'Arrangement'}));
	}

	# Gjør så en sortering, først på dato, deretter på fylke og så 
	# på arrangør-institusjon
	@arrangementer = @arrangementer[sort arrliste $[ .. $#datakeys];

	if ($#arrangementer >= $input{'Makstreff'}) {
	    printf "Søket ga %d treff, viser kun de $input{'Makstreff'} første:<p>\n", scalar(@arrangementer);
	    @arrangementer = @arrangementer[ $[ .. $input{'Makstreff'}-1 ];
	} else {
	    printf "Søket ga %d treff:<p>\n", scalar(@arrangementer);
	}

	sub arrliste { $datakeys[$a] cmp $datakeys[$b]; }

	# Kan så skrive ut alle arrangementene:
	print "<dl>\n";
	for (@arrangementer) {
	    @entry{@fields} = split($fieldsep, $_);
	    printf(" <dt> <font size=+2>%s, %s:</font>\n <dd>\n",
		  $entry{'Dato'}, $entry{'Fylke'})
		if ($forrige ne $entry{'Dato'} . $entry{'Fylke'});
	    printf("  <li> %s: <a href=\"$arrurl/arr%04d.html\">%s</a>\n",
		   @entry{'Institusjon', 'Nummer', 'Arrangement'});
	    $forrige = $entry{'Dato'} . $entry{'Fylke'};
	}
	print "</dl>\n";
    }
    print &footer;
}



sub printparams {
    local(%par) = @_;

    foreach $key (sort keys %par) {
	next unless $fieldname{$key};
	push(@lines, " <dt> <b>$fieldname{$key}</b>\n <dd> $par{$key}\n");
    }
    return unless @lines;

    print "<blockquote>\n<hr noshade size=2>\n";
    printf("Søkepara%s var som følger:\n",
	   (@lines == 1) ? "meteren" : "metrene");
    print "<dl>\n@lines\n</dl>\n<hr noshade size=2>\n</blockquote>\n";
}

