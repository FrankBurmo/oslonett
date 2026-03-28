#!/local/bin/perl

# Program for å generere liste eller enkeltutskrift for arrangementer
# under Forskingsdagene '95.
#
# KGN, 13.7.95. Sist endret: 13.7.95

%fieldname = ("Arrangement", "Arrangementets tittel",
              "Beskrivelse", "Kort beskrivelse av arrangementet",
              "Sted", "Sted",
              "Dato", "Dato",
              "Klokkeslett", "Klokkeslett",
              "Institusjon", "Arrangør-institusjon",
              "Kontakt", "Kontaktperson for påmelding",
              "Pris", "Pris",
              "Maalgruppe", "Målgruppe(r)",
              "Fylke", "Fylke",
              "Beliggenhet", "Beliggenhet" );          

@fields = ("Nummer", "Arrangement", "Beskrivelse", "Dato", "Institusjon",
	   "Fylke", "Beliggenhet", "Maskin");

require "adm/fd-lib.pl";

print "Content-type: text/html\n\n";

%input = &getinput;
delete($input{'Fylke'}) if ($input{'Fylke'} =~ /alle fylker/i);
$input{'Makstreff'} = 10000 unless $input{'Makstreff'};
&regexp_escape(@input{'Arrangement', 'Institusjon', 'Beliggenhet'});
&case_insensitivize(@input{'Arrangement', 'Institusjon', 'Beliggenhet'});
@matches = &dosearch;

&showlist(@matches);

exit 0;


sub dosearch {
    local(@matches);

    open(FILE, $arrindeks)
	|| &error("Kunne ikke åpne indeksfilen ($arrindeks)");
    while (<FILE>) {
	@entry{@fields} = split($fieldsep, $_);

	# Hvis et arrangement foregår på flere dager, lag egne entries
	# for hver dag...
	@dates = split($datosep, $entry{'Dato'});
	foreach (@dates) {
	    $entry{'Dato'} = $_;
	    push(@matches, join($fieldsep, @entry{@fields}))
		if ((!$input{'Arrangement'}
		     || ($entry{'Arrangement'} =~ /$input{'Arrangement'}/i
			 || $entry{'Beskrivelse'} =~ /$input{'Arrangement'}/i))
		    && (!$input{'Institusjon'}
			|| $entry{'Institusjon'} =~ /$input{'Institusjon'}/i)
		    && ($input{'Fylke'} !~ /\S/
			|| $entry{'Fylke'} eq $input{'Fylke'})
		    && (!$input{'Beliggenhet'}
			|| $entry{'Beliggenhet'} =~ /$input{'Beliggenhet'}/i)
		    && (!$input{'Dato'}
			|| (&matchdate($entry{'Dato'}, $input{'Dato'}))));
	}
    }
    close(FILE);

    @matches;
}


sub matchdate {
    local($a, $b) = @_[0,1];
    local(@a, @b, %mark);

    @a = split($datosep, $a);
    @b = split($datosep, $b);

    grep($mark{$_}++, @a);

    join($datosep, grep($mark{$_}, @b));
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
	    ($dato, $mnd) = $entry{'Dato'} =~ /(\d+)\.(\d+)/;
	    
	    printf(" <dt> <font size=+2>%d. %s, %s:</font>\n <dd>\n",
		  $dato, $mnd[$mnd-1], $entry{'Fylke'})
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
    local (%par) = @_;
    local ($key, @lines);

    foreach $key (sort keys %par) {
        next unless $fieldname{$key};
        push(@lines, " <dt> <b>$fieldname{$key}</b>\n <dd> $par{$key}\n");
    }
    return unless @lines;

    print "<blockquote>\n<hr noshade size=\"2\">\n";
    printf("Søkepara%s var som følger:\n",
           (@lines == 1) ? "meteren" : "metrene");
    print "<dl>\n@lines\n</dl>\n<hr noshade size=\"2\">\n</blockquote>\n";
}
