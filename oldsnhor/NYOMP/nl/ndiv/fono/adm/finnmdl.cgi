#!/local/bin/perl
# Script for å søke i kundedatabasen. Med entydig input til script'et 
# returneres data om ett firma, ellers en liste over alle passende 
# firmaer.
#


require "../lib/medllib.pl";

@firms = &readdata;

%input = &getinput;
# returnerer data i (den globale) %input (key=feltnavn)

@matches = &dosearch;
&nomatch unless ( @matches );
$#matches ? &showlist(@matches) : &showfirm($matches[0]);

exit 0;




sub readdata {
# initialiserer globale variable:
    local(@firms);

    open(DATA, $datafile) || &error("Kunne ikke åpne datafilen");
    while (<DATA>) {
	push(@firms, $_);
    }
    close DATA;
    @firms;
}





sub dosearch {
    $input{'Firma'} =~ s:/:\\/:g; 
    $ret =  eval($foobar = "/$input{'Firma'}/"); # ønsker å trap'e evt. feil i regexp

    if ( ! defined($ret) ) {
	&printheader("Feil i søkeuttrykket");
	print <<EOT;
Du har sendt med følgende søkeuttrykk for firmanavn:
<b>$input{'Firma'}</b> <br>($foobar)
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
    foreach $firm ( @firms ) { 
	chop($firm);
	@values = split($fieldsep, $firm);
	for $name ( @fields ) { 
	    $old{$name} = shift(@values);
	}

	for $name ( 'Firma', 'Diverse') {
	    $input{$name} = '.*' unless $input{$name};
	}

	push(@matches, $firm) 
	    if ( 
		(!$input{'Medlemsnr'} || $old{'Medlemsnr'} == $input{'Medlemsnr'}) &&
		$old{'Firma'} =~ /$input{'Firma'}/i &&
		$old{'Diverse'} =~ /^$input{'Diverse'}$/ );

    }
    @matches;
}



sub showlist {
    local(@firms) = @_;
    local($line, @list, @name, @no, $totalcount);

    foreach $firm ( @firms ) {
	%old = &decode($firm);


	$old{'Firma'} =~ s/^\s+//;	

	if ($input{'format'} ne 'html') {
	    $latexfirm = $old{'Firma'};
	    $latexfirm =~ s/([\{\\\}])/\\verb@$1@/g;
	    $latexfirm =~ s/([\%\$\^\#\_\~\&])/\\$1\{\}/g;

	    $line = sprintf("%s& %s", $latexfirm, $old{'Medlemsnr'});

	    $line .= sprintf("& %s", $old{Kontakt})
		if $input{'felt.kontakt'};
	    $line .= sprintf("& %s, %s %s", $old{'Adresse'}, 
			     $old{'Postnr'}, $old{'Poststed'}) 
		if $input{'felt.adr'};



	
	    $line .= sprintf("& %s", $old{'Kontakt1'})
		if $input{'felt.kontakt1'};
	    $line .= sprintf("& %s", $old{'Kontakt2'})
		if $input{'felt.kontakt2'};
	    $line .= "\\\\\n";
	} else {
	    $line = sprintf("<a href=%s?Medlemsnr=%d>%-50s%4d  ",
			    $privfinnscript, $old{'Medlemsnr'},
			    $old{'Firma'}."</a>", $old{'Medlemsnr'});
	    $line .= sprintf(" %-25s", $old{'Kontakt'})
		if $input{'felt.kontakt'};
	    $line .= sprintf(" %-10s", $old{'Telefon'}) if $input{'felt.tel'};
	    $line .= sprintf(" %-50s", $old{'Adresse'}.", ".$old{'Postnr'}
			     ." ". $old{'Poststed'})
		if $input{'felt.adr'};
	    $line .= sprintf(" %-18s", $old{'Annonsetype'})
		if $input{'felt.type'};
	    if ($input{'felt.pris'}) {
		if ($old{'Annonsetype'} ne "Stillingsannonse"
		    || $input{'Annonsetype'} eq "Stillingsannonse") {
		    $line .= sprintf(" %8s ", $price{$old{'Annonsetype'}});
		    if ($price{$old{'Annonsetype'}}) {
			$line .= ($old{'Bekreftet'} eq "Ja") ? "Ja   " : "Nei  ";
		    } else {
			$line .= "     ";
		    }
		    $sumprice += $price{$old{'Annonsetype'}};
		} else {
		    $line .= " " x 15;
		}
	    }

	    $line .= sprintf(" %-20s", $old{'Kontakt1'})
		if $input{'felt.kontakt1'};
	    $line .= sprintf(" %-15s", $old{'Kontakt2'})
		if $input{'felt.kontakt2'};
	    $line .= "\n";
	}
	push(@list, $line);

# Kan nå manipulere $firm uten at utskriften endres.
# Ønsker riktig sortering av ÆØÅ.
	$old{'Firma'} =~ tr/a-zæøåÆØÅ/A-Z[\\][\\]/;
	push(@name, $old{'Firma'}); # trenger @name og @no for å gjøre
	push(@no, $old{'Medlemsnr'}); # alfabetisk eller numerisk sortering hhv.
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
    $overskr = "Firmanavn                                   Medlemsnr  ";
    $overskr .= "Kontaktperson            " if $input{'felt.kontakt'};
    $overskr .= "Adresse                                            "
        if $input{'felt.adr'};

    $overskr .= "Pris/Bekreftet " if $input{'felt.pris'};


if ($input{'format'} eq 'html') {
    &printheader("Liste over FONO medlemmer");
    print "<pre>\n$overskr\n\n@list\n</pre>\n";

    print "Tilsammen $totalcount medlemmer i listen ovenfor.<p>\n\n";
    
    print "Listen inkluderer også medlemmer som er markert som «tidligere medlem».<p>\n\n" if ($input{'visgamle'} eq "ja");


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

	$overskr .= "}\nFirmanavn& Medlemsnr";
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
\\section*{Liste over kunder}
\\small
$overskr
\\hline
@list
\\end{tabular}

Tilsammen $totalcount kunder i listen ovenfor. 

EOT
    
    print LATEX "Listen inkluderer også kunder som er markert som «tidligere kunde».\n\n" if ($input{'visgamle'} eq "ja");
    print LATEX "Listen inkluderer også kunder som er ikke er bekreftet.\n\n" if ($input{'visikkebekreftet'} eq "ja");

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
\\section*{Kundedata for $old{'Firma'}}

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

    &showlatexfirm(%old) if (defined($input{'format'}) &&
			     $input{'format'} ne 'html');


    &printheader("Oppdatering av data i FONOs medlemsregister");

    print <<EOT;

<form method="POST" action="$endrescript">
<input type=hidden name="Medlemsnr" value="$old{'Medlemsnr'}">
<input type=hidden name="RegDato" value="$old{'RegDato'}">
EOT

    open(FORM, $nykundeform) || 
	&error("Finner ikke FORM for ny registrering ($nykundeform)");

    while ( <FORM> ) {
	next if 1 .. /<form/i;	# kast alle linjer før <form...
	for $field ( @simplefields ) {
	    s/(name=\"$field\")/$1 value=\"$old{$field}\"/ig;
	}

	for $field ( @textareas ) {
	    s/(<textarea name=\"$field\".+>\n)/$1$old{$field}/ig;
	}

	for $field ( @radiobuttons ) {
	    s/(name=\"$field\"\s+value=\"$old{$field}\")/$1 checked/ig;
	}

	( $select ) = /select\s+name=\"(\w+)\"/ig;
	$lastselect = $select if $select;

	s/action=".+"/action="$endrescript"/ig;
	s/(Firmainformasjon)/$1, kundenummer: $old{'Medlemsnr'}/;
	s/<input\s+type="submit"[^>]*>/<input type="submit" name="Knapp" value="Oppdater medlemsdatabasen"> <input type="submit" name="Knapp" value="Slett dette medlemmet">/ig;
	s/<option\s+selected>/<option>/;
	s/<option>\s*($old{$lastselect})/<option selected>$1/gi;

	print;
    }
    close(FORM);

    exit 0;
}


sub nomatch {

    while ( ($key, $val) = each %input ) {
#	next if ( $val eq '.*' || $skip{$key} );
	push(@lines, "<li> $key = $val\n");
    }

    &printheader("Søket ga ingen treff");
    print <<EOT;
De angitte søkeparametrene passer ikke med noen av postene i kundedatabasen.

Søkeparametrene var:
<ul>
@lines
</ul>
EOT
    &printfooter;
    exit 0;
}


