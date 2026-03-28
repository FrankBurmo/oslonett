#!/local/bin/perl
# Script for å søke i titteldatabasen. Med entydig input til script'et 
# returneres data om ett firma, ellers en liste over alle passende 
# firmaer.
#


require "lib/tittellib.pl";

@stikks = &readdata;



%input = &getinput;
# returnerer data i (den globale) %input (key=feltnavn)

@matches = &dosearch;
&nomatch unless ( @matches );
$#matches ? &showlist(@matches) : &showfirm($matches[0]);

exit 0;


sub readdata {
# initialiserer globale variable:
    local(@stikks);

    open(DATA, $stikkdatafile) || &error("Kunne ikke åpne datafilen");
    while (<DATA>) {
	push(@stikks, $_);
    }
    close DATA;
    @stikks;
}


sub dosearch {
    $ret =  eval("/$input{'Tittel'}/"); # ønsker å trap'e evt. feil i regexp
    if ( ! defined($ret) ) {
	&printheader("Feil i søkeuttrykket");
	print <<EOT;
Du har sendt med følgende søkeuttrykk for tittelnavn:
<b>$input{'Tittel'}</b> 
<p>

Dette er ikke et lovlig
<a href="http://pubweb.nexor.co.uk/public/perl/man/html/perlre.html">
regulært uttrykk i perl</a>. Gå tilbake til skjemaet og rett opp feilen.
<p>

Eventuelle spørsmål kan rettes til <a href="mailto:$mailadr">$mailadr</a>.
EOT
        &printfooter;
        exit 1;
    }
    foreach $stikk ( @stikks ) { 
	chop($stikk);
	@values = split("%", $stikk);
	for $name ( @stikkfields ) { 
	    $old{$name} = shift(@values);
	}

	for $name ( 'Tittel',  'Artist', 'Genre', 'Label', 'Stikkord') {
	    $input{$name} = '.*' unless $input{$name};
	}

	push(@matches, $stikk) 
	    if ( 
		(!$input{'Stikknr'} || ($old{'Stikknr'} == $input{'Stikknr'})) &&
 		$old{'Artist'} =~ /$input{'Artist'}/i &&
		$old{'Label'} =~ /$input{'Label'}/i &&
		$old{'Genre'} =~ /$input{'Genre'}/i &&
 		$old{'Stikkord'} =~ /$input{'Stikkord'}/i &&
		$old{'Tittel'} =~ /$input{'Tittel'}/i );
    }
    @matches;
}



sub showlist {
    local(@stikks) = @_;
    local($line, @list, @name, @no, $totalcount);

    foreach $stikk ( @stikks ) {
	%old = &decode($stikk,'%',*stikkfields);


	$old{'Tittel'} =~ s/^\s+//;	

	if ( ! ($input{'format'} =~ /html.*/)) {
	    $latexfirm = $old{'Tittel'};
	    $latexfirm =~ s/([\{\\\}])/\\verb@$1@/g;
	    $latexfirm =~ s/([\%\$\^\#\_\~\&])/\\$1\{\}/g;

	    $line = sprintf("%s& %s", $latexfirm, $old{'Stikknr'});

	    $line .= sprintf("& %s", $old{Artist})
		if $input{'felt.artist'};
	    $line .= sprintf("& %s, %s %s", $old{'Label'})
		if $input{'felt.label'};

	
	    $line .= sprintf("& %s", $old{'Genre'})
		if $input{'felt.genre'};

	    $line .= "\\\\\n";
	} elsif ($input{'format'} eq 'htmlfull') { 
# lag en full utskrift for hvert tittel, her m] navn byttes
          $line = "<font size=+1><b>$old{'Tittel'}</b></font>\n
          <blockquote>\n";
          $line .= "v. $old{'Kontakt'}<br>\n" if $old{'Kontakt'};
          $line .= "$old{'Adresse'}<br>
          $old{'Postnr'} $old{'Poststed'}<br>\n";
          $line .= "Tlf: $old{'Telefon'}" if $old{'Telefon'};
          $line .= ", fax: $old{'Telefax'}\n" if $old{'Telefax'};

          if ($old{'Email'}) { $line .= "<p>Email: <a href=\"mailto:$old{'Email'}\">$old{'Email'}</a>\n";
			       } else { $line .= "<p>\n";}

          $line .= "URL: <a href=\"$old{'URL'}\">$old{'URL'}</a>\n" if $old{'URL'};
 
          $line .= "<p>$old{'Diverse'}\n" if $old{'Diverse'};
          $line .= "</blockquote>\n";

	    } else { 

# Normal html kortformat liste
        
	    $line = sprintf("<a href=%s?Stikknr=%d>%-35s  ",
			    $finnstikkscript, $old{'Stikknr'},
			    substr ($old{'Tittel'},0,31)."</a>");
	    $line .= sprintf(" %-25s", $old{'Artist'})
		if $input{'felt.artist'};

	    $line .= sprintf(" %-30s", $old{'Label'})
		if $input{'felt.label'};
	    $line .= sprintf(" %-15s", $old{'Genre'})
		if $input{'felt.genre'};
	    $line .= sprintf(" %-15s", $old{'Kat.nr'})
		if $input{'felt.katnr'};
	    $line .= sprintf(" %-6s", $old{'Tid'})
		if $input{'felt.tid'};
	    $line .= "\n";
	}
	push(@list, $line);

# Kan nå manipulere $stikk uten at utskriften endres.
# Ønsker riktig sortering av ÆØÅ.
	$old{'Tittel'} =~ tr/a-zæøåÆØÅ/A-Z[\\][\\]/;
	push(@name, $old{'Tittel'}); # trenger @name og @no for å gjøre
	push(@no, $old{'Stikknr'}); # alfabetisk eller numerisk sortering hhv.
    }

    sub byname { 
	$name[$a] cmp $name[$b]; 
    }

    sub bynumber { 
	$no[$a] <=> $no[$b]; 
    }

    if ( $input{'sortering'} eq "numerisk" ) {
	@list = @list[sort bynumber $[..$#name];
    } elsif ( $input{'sortering'} eq "dato" ) {
	@list = reverse @list[ sort bynumber $[..$#name ];
    } else {
	@list = @list[sort byname $[..$#name];
    }

    $totalcount = @list;

    $"='';
    $dato = &dato;
    $overskr = "Kuttnavn                          ";
    $overskr .= "Artist                    "    if $input{'felt.artist'};
    $overskr .= "Label                          " if $input{'felt.label'};
    $overskr .= "Genre          "                if $input{'felt.genre'};
    $overskr .= "Kat.nr         "                if $input{'felt.katnr'};
    $overskr .= "Avsp.tid"                        if $input{'felt.tid'};



if ($input{'format'} eq 'html' || $input{'format'} eq 'htmlfull') {

    if  ($ENV{HTTP_REFERER} =~ /\.*finnmdl/) {
	&printheader("Liste over stikkord fra $input{'Label'}");}
    else {    &printheader("Liste over oppføringer fra FONOs stikkorddatabase");}

    print "<pre>\n$overskr\n\n" if $input{'format'} eq 'html';
    print "@list\n";
    print "</pre>\n" if $input{'format'} eq 'html';

    print "Tilsammen $totalcount titler i listen ovenfor.<p>\n\n";
    

    print "Automatisk generert $dato.\n\n";

    &printfooter;
    } else {
	chdir($tmpdir) || &error("Failed to cd to $tmpdir");
	open(STDERR, "/dev/null");
	open(LATEX, ">tmp.$$.tex") || &error("Failed to create tmp-file");

	$overskr = "\\begin{tabular}{lr";

	$overskr .= "l" if $input{'felt.kontakt'};
	$overskr .= "l" if $input{'felt.adr'};
	$overskr .= "l" if $input{'felt.type'};
	$overskr .= "rc" if $input{'felt.pris'};
	$overskr .= "l" if $input{'felt.kontakt1'};
	$overskr .= "l" if $input{'felt.kontakt2'};

	$overskr .= "}\nTittelnavn& Stikknr";
	$overskr .= "& Kontaktperson" if $input{'felt.kontakt'};
	$overskr .= "& Adresse" if $input{'felt.adr'};
	$overskr .= "& Annonsetype" if $input{'felt.type'};
	$overskr .= "& Kvartalpris& Bekreftet?" if $input{'felt.pris'};
	$overskr .= "& Initiell kontakt" if $input{'felt.kontakt1'};
	$overskr .= "& Operativ kontakt" if $input{'felt.kontakt2'};
	$overskr .= "\\\\";

	$pagebreak = "\\end{tabular}\n\\newpage\n$overskr\n\\hline\n";
	$linecount = $tablesize - 7;
	while (defined($list[$linecount])) {
	    splice(@list,$linecount,0,$pagebreak);
	    $linecount += $tablesize;
	}

	$dato = &dato;
	print LATEX <<EOT;
\\documentstyle[A4,isolatin,psfig]{article}
\\parindent=0cm
\\begin{document}
\\psfig{figure=$pslogofile,width=6cm}
\\section*{Liste over tittelr}
\\small
$overskr
\\hline
@list
\\end{tabular}

Tilsammen $totalcount tittelr i listen ovenfor. 

EOT
    
    print LATEX "Listen inkluderer også tittelr som er markert som «tidligere tittel».\n\n" if ($input{'visgamle'} eq "ja");
    print LATEX "Listen inkluderer også tittelr som er ikke er bekreftet.\n\n" if ($input{'visikkebekreftet'} eq "ja");

    print LATEX "Faste leieinntekter, pr. kvartal (spesialavtaler ikke medregnet): NOK $sumprice\n\n" if $input{'felt.pris'} && $sumprice;
    
    print LATEX "Listen ble generert automatisk $dato.\n\\end{document}\n";

close(LATEX);

	$| = 1;	   # Husk å flush'e stdout etter at Content-type er angitt
	if ( $input{'format'} =~ /^ps.+/ ) {
	    system("latex tmp.$$.tex > /dev/null");

	    print "Content-type: application/";
	    print (($input{'format'} eq 'psskjerm')
		? 'postscript' : 'octet-stream');
	    print "\n\n";
	    system("dvips -f < tmp.$$.dvi");
	} else {
	    print"Content-type: application/octet-stream\n\n";
	    system("cat tmp.$$.tex");
	}
	system("rm tmp.*");
    }
exit 0;
}



sub showlatexfirm {
    local(%old) = @_;
    local($dato);

    chdir($tmpdir) || &error("Failed to cd to $tmpdir");
    open(STDERR, ">/dev/null");
    open(LATEX, ">tmp.$$.tex") || &error("Failed to create tmp-file");

    for (@stikkfields) {
	$old{$_} =~ s/([\{\\\}])/\\verb@$1@/g;
	$old{$_} =~ s/([\%\$\^\#\_\~\&])/\\$1\{\}/g;
	push(@items, "\\item[$fieldname{$_}:] $old{$_}\n");
    }
    $dato = &dato;
    print LATEX <<EOT;
\\documentstyle[A4,isolatin,psfig]{article}
\\parskip=0cm
\\parindent=0cm
\\pagestyle{empty}
\\begin{document}
\\psfig{figure=$pslogofile,width=6cm}
\\section*{Titteldata for $old{'Tittel'}}

\\begin{description}
@items
\\end{description}

Dokumentet ble generert automatisk $dato
\\end{document}
EOT
    close(LATEX);

    $| = 1;	   # Husk å flush'e stdout etter at Content-type er angitt
    print "Content-type: application/";
    print ( ($input{'format'} eq 'psskjerm')
	   ? "postscript\n\n" : "octet-stream\n\n");

    if ( $input{'format'} =~ /^ps.+/ ) {
	system("latex tmp.$$.tex > /dev/null");
	system("dvips -f < tmp.$$.dvi; ");
    } else {
	system("cat tmp.$$.tex");
    }
    system("rm tmp.$$.*");
    exit 0;
}
    


sub showfirm {
    $entry = @_[0];
    @old = split("%", $entry);
    foreach ( @stikkfields ) {
	$old{$_} = shift(@old);
    }
    $linje = $old{'Diverse'};
    $pos = $textareawidth;
    while ( substr($linje, $pos, 1) ) {
	while ( substr($linje, $pos, 1) =~ /\S/ ) { $pos--; }
	substr($linje,$pos,1) = "\n";
	$pos += $textareawidth;
    }
    $old{'Diverse'} = $linje;


    &printheader("Utskrift fra FONOs stikkorddatabase");
    $lab = $old{Label};
    $lab =~ s/\ /\+/g;    
    print<<EOT;
    Denne tittelen ligger lagret med stikkord: <b>$old{Stikkord}</b><p>
        <table cellspacing=5 border=5 cellpadding=2>
	<tr><th align=left>Kuttittel</th><th align=left>Artist</th>
            <th align=left>Label</th><th align=left>Genre</th>
            <th align=left>Kat.nr</th><th align=left>Tid</th>
        <tr><td>$old{'Tittel'}</td><td>$old{'Artist'}</td>
            <td><a href="finnmdl.cgi?Firma=$lab&format=html">$old{'Label'}</a></td><td>$old{'Genre'}</td>
            <td>$old{'Kat.nr'}</td><td>$old{'Tid'}</td></tr>
        
        </table>
        <p>

EOT

    &printfooter;

    exit 0;
}


sub nomatch {

    while ( ($key, $val) = each %input ) {
#	next if ( $val eq '.*' || $skip{$key} );
	push(@lines, "<li> $key = $val\n");
    }

    &printheader("Søket ga ingen treff");
    print <<EOT;
De angitte søkeparametrene passer ikke med noen av postene i stikkorddatabasen.

Søkeparametrene var:
<ul>
@lines
</ul>
EOT
    &printfooter;
    exit 0;
}


