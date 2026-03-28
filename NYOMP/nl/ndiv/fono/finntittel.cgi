#!/local/bin/perl
# Script for å søke i titteldatabasen. Med entydig input til script'et 
# returneres data om ett firma, ellers en liste over alle passende 
# firmaer.
#


require "lib/tittellib.pl";

@titles = &readdata;

%input = &getinput;
# returnerer data i (den globale) %input (key=feltnavn)

@matches = &dosearch;
&nomatch unless ( @matches );
$#matches ? &showlist(@matches) : &showfirm($matches[0]);

exit 0;


sub readdata {
# initialiserer globale variable:
    local(@titles);

    open(DATA, $datafile) || &error("Kunne ikke åpne datafilen");
    while (<DATA>) {
	push(@titles, $_);
    }
    close DATA;
    @titles;
}


sub dosearch {
    $input{'Tittel'} =~ s:/:\\/:g; 
    $ret =  eval($foobar= "/$input{'Tittel'}/"); # ønsker å trap'e evt. feil i regexp
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
    foreach $tit ( @titles ) { 
	chop($tit);
	@values = split($fieldsep, $tit);
	for $name ( @fields ) { 
	    $old{$name} = shift(@values);
	}

	for $name ( 'Tittel', 'Firma', 'Artist', 'Genre', 'Label') {
	    $input{$name} = '.*' unless $input{$name};
	}

	push(@matches, $tit) 
	    if ( 
		(!$input{'Tittelnr'} || $old{'Tittelnr'} == $input{'Tittelnr'}) &&
		$old{'Label'} =~ /$input{'Label'}/i &&
		$old{'Genre'} =~ /^$input{'Genre'}$/ &&
 		$old{'Artist'} =~ /^$input{'Artist'}/i &&
		$old{'Tittel'} =~ /^$input{'Tittel'}/i );
    }
    @matches;
}



sub showlist {
    local(@titles) = @_;
    local($line, @list, @name, @no, $totalcount);

    foreach $tit ( @titles ) {
	%old = &decode($tit,$fieldsep,*fields);


	$old{'Tittel'} =~ s/^\s+//;	

	if ( ! ($input{'format'} =~ /html.*/)) {
	    $latexfirm = $old{'Tittel'};
	    $latexfirm =~ s/([\{\\\}])/\\verb@$1@/g;
	    $latexfirm =~ s/([\%\$\^\#\_\~\&])/\\$1\{\}/g;

	    $line = sprintf("%s& %s", $latexfirm, $old{'Tittelnr'});

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
          <blockquote><table border=0 cellspacing=2>\n";
          $line .= "<tr><td>Artist</td><td> : </td><td>$old{'Artist'}</td></tr>\n";
          $line .= "<tr><td>Label</td><td> : </td><td>$old{'Label'}</td></tr>\n";
          $line .= "<tr><td>Genre</td><td> : </td><td>$old{'Genre'}</td></tr>\n";
          $line .= "<tr><td>Kat.nr</td><td> : </td><td>$old{'Kat.nr'}</td></tr>\n";
          $line .= "<tr><td>Utg.år</td><td> : </td><td>$old{'År'}</td></tr>\n";
          $line .= "<tr><td>Pris</td><td> : </td><td>$old{'Pris'}</td></tr>
          </table>\n";

 
          $line .= "<p>$old{'Diverse'}\n" if $old{'Diverse'};
          $line .= "</blockquote>\n";

	    } else { 
        
	    $line = sprintf("<a href=%s?Tittelnr=%d>%-35s  ",
			    $finnscript, $old{'Tittelnr'},
			    substr($old{'Tittel'},0,31)."</a>");
	    $line .= sprintf(" %-25s", $old{'Artist'})
		if $input{'felt.artist'};

	    $line .= sprintf(" %-50s", $old{'Label'})
		if $input{'felt.label'};
	    $line .= sprintf(" %-18s", $old{'Genre'})
		if $input{'felt.genre'};


	    $line .= "\n";
	}
	push(@list, $line);

# Kan nå manipulere $tit uten at utskriften endres.
# Ønsker riktig sortering av ÆØÅ.
	$old{'Tittel'} =~ tr/a-zæøåÆØÅ/A-Z[\\][\\]/;
	push(@name, $old{'Tittel'}); # trenger @name og @no for å gjøre
	push(@no, $old{'Tittelnr'}); # alfabetisk eller numerisk sortering hhv.
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
    $overskr = "Tittelnavn                        ";
    $overskr .= "Artist                     " if $input{'felt.artist'};
    $overskr .= "Label  " if $input{'felt.label'};
    $overskr .= "  Genre                                            "
        if $input{'felt.genre'};


if ($input{'format'} eq 'html' || $input{'format'} eq 'htmlfull') {

    if  ($ENV{HTTP_REFERER} =~ /\.*finnmdl/) {
	&printheader("Liste over titler fra $input{'Label'}");}
    else {    &printheader("Liste over titler fra FONOs titteldatabase");}
    print "<font size=-1>(noen titler kan være kuttet for å få plass skjermen)</font>\n";

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

	$overskr .= "}\nTittelnavn& Tittelnr";
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

    for (@fields) {
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
    @old = split($fieldsep, $entry);
    foreach ( @fields ) {
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


    &printheader("Utskrift fra FONOs titteldatabase");
# Fix spacer
    $firma = $old{Label};
    $firma =~ s/\ /\+/g;
#    $firma =~ s#/#%2F#g;

    print<<EOT;
        <table cellspacing=5 border=5 cellpadding=2>
	<tr><th align=left>Tittel</th><th align=left>Artist</th>
            <th align=left>Label</th><th align=left>Genre</th>
            <th align=left>Kat.nr</th><th align=left>Utg.år</th>
            <th align=left>Pris</th></tr>
        <tr><td>$old{'Tittel'}</td><td>$old{'Artist'}</td>
            <td><a href="finnmdl.cgi?format=html&Firma=$firma">$old{'Label'}</a></td><td>$old{'Genre'}</td>
            <td>$old{'Kat.nr'}</td><td>$old{'År'}</td><td>$old{'Pris'}</td></tr>
        
        </table>
        <p>
      <center>
      <table border=0 cellspacing=5>
      <tr><td>
      <form method="POST" action="bestill.cgi">
        <input type="hidden" name="Label" value="$old{'Label'}">
        <input type="hidden" name="Tittel" value="$old{'Tittel'}">
        <input type="hidden" name="Artist" value="$old{'Artist'}">
        <input type="hidden" name="Kat.nr" value="$old{'Kat.nr'}">
        <input type="hidden" name="Pris" value="$old{'Pris'}">
       <input type="submit" value="Bestill mot postoppkrav">
     </form></td><td>
      <form method="POST" action="https://shop.sn.no/shop/fono/bestill.cgi">
        <input type="hidden" name="Label" value="$old{'Label'}">
        <input type="hidden" name="Tittel" value="$old{'Tittel'}">
        <input type="hidden" name="Artist" value="$old{'Artist'}">
        <input type="hidden" name="Kat.nr" value="$old{'Kat.nr'}">
        <input type="hidden" name="Pris" value="$old{'Pris'}">
        <input type="submit" value="Bestill med kredittkort">
     </form></td></tr></table>
     </center>
<p>
(Bestilling med kredittkort, krever at du bruker Netscape Web browser eller
 en annen browser som støtter sk. SSL, dvs. kryptert kommunikasjon.
EOT
 if ($ua eq "Mozilla" && $ver >= 1.1) {
     print " Det kan se ut som om din browser støtter dette!";
 } else {
     print " Det kan se ut som om din browser <i>ikke</i> støtter dette!";
 }

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
De angitte søkeparametrene passer ikke med noen av postene i titteldatabasen.

Søkeparametrene var:
<ul>
@lines
</ul>
EOT
    &printfooter;
    exit 0;
}


