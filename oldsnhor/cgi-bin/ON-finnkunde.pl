#!/local/bin/perl
# Script for å søke i kundedatabasen. Med entydig input til script'et 
# returneres data om ett firma, ellers en liste over alle passende 
# firmaer.
#
# KGN, 16.6.95.
&error("Kun en provosert testfeil!");
&init;     # definerer globale variable
&getinput; # returnerer data i (den globale) %input (key=feltnavn)
@matches = &dosearch;
&nomatch unless ( @matches );
$#matches ? &showlist(@matches) : &showfirm($matches[0]);

exit 0;


sub error {

    &printhtmlhead("Feilmelding");
    print <<EOT;
CGI-scriptet ble avbrutt med følgende feilmelding:
<blockquote>
<hr>
@_
</hr>
<p>

Vil du ha ytterligere informasjon, ta kontakt med <a
href="mailto:kgn@oslonett.no">kgn@oslonett.no</a>
</body>
</html>
EOT
    exit 1;
}


sub init {
# initialiserer globale variable:
#
# $fieldsep     feltseparator i datafilen
# $sepcode      erstatning for opprinnelig forekomster av $fieldsep
# $ignore       (god kommentar XXXXX)
# $datafile     filnavn til datafil
# @firms        inneholder alle poster fra datafilen, 
#               feltene adkskilt med $fieldsep

    $ENV{'PATH'} = '/local/bin:/usr/bin';

    $endrescript = 'http://www.oslonett.no/on/www/kunder/ON-endrekunde.pl';
    $finnscript = 'http://www.oslonett.no/on/www/kunder/ON-finnkunde.pl';
    $nykundeform = '/local/www/on/www/kunder/nykunde.html';
    $datafile = '/local/www/ON-kundedata.txt';
    $tmpdir = '/local/www/tmp';

    $ignore = '[vilkårlig]';
    $fieldsep = '"';

    @fields = ("Kundenr", "Dato", "Firma", "Kontakt", "Adresse", "Postnr",
	       "Poststed", "Telefon", "Telefax", "Email", "Bekreftet",
	       "Annonsetype", "Spesialpris", "Diverse", "Kontakt1",
	       "Kontakt2");
    @simplefields = ("Firma", "Kontakt", "Adresse", "Postnr", "Poststed", 
		     "Telefon", "Telefax", "Email", "Spesialpris" );
    @radiobuttons = ("Bekreftet");
    @textareas = ("Diverse");

    open(DATA, $datafile) || &error("Kunne ikke åpne datafilen");
    while (<DATA>) {
	push(@firms, $_);
    }
    close DATA;
}




sub getinput {
# Leser inn data (med method GET eller POST) og plasserer dem i 
# (den globale) array'en %input, der nøkkel til assosiativ array er feltnavnet

    local($i, $name, $value, $data, @data);

    if ($ENV{'REQUEST_METHOD'} eq "GET") {
        $data = $ENV{'QUERY_STRING'};
    } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
        read(STDIN, $data, $ENV{'CONTENT_LENGTH'});
    }

    # Del opp input-data i felter ved alle forekomster av '&'.
    @data = split(/&/, $data);

    for $i (0 .. $#data) {

        # Pluss oversettes til SPC
        $data[$i] =~ tr/+/ /;

        # Alt til venstre for første "=" er feltnavn, resten er felt-verdi
        ($name, $value) = split(/=/, $data[$i], 2);

        # Erstatt forekomster av %<hexkode> med tilsvarende tegn
        $name =~ s/%(..)/pack("c",hex($1))/ge;
        $value =~ s/%(..)/pack("c",hex($1))/ge;

        # En/flere forekomster av SPC, CR og LF i $value oversettes til SPC
        $value =~ s/[ \r\n]+/ /g;

        # Feltseparatoren er ulovlig i $value, koder denne som $sepcode
        $value =~ s/$fieldsep/$sepcode/g;

        $input{$name} = $value;
    }
}



sub dosearch {
    $Boolop = $input{'soek'} eq "og" ? "&&" : "||";

    foreach ( 'Firma' , 'Annonsetype', 'Kontakt1', 'Kontakt2' ) {
	$input{$_} = '.*' if (! $input{$_} || $input{$_} eq $ignore);
    }


    foreach ( @firms ) { 
	chop;
	($Kundenr, $Firma, $Annonsetype, $Kontakt1, $Kontakt2) = 
	    (split("\""))[0,2,11,14,15];
	push(@matches, $_) 
	    if ( 
		(!$input{'Kundenr'} || $Kundenr == $input{'Kundenr'}) &&
		$Firma =~ /$input{'Firma'}/i &&
		$Annonsetype =~ /^$input{'Annonsetype'}$/ &&
 		$Kontakt1 =~ /^$input{'Kontakt1'}$/ &&
		$Kontakt2 =~ /^$input{'Kontakt2'}$/ );
    }
    @matches;
}



sub showlist {
    local(@firms) = @_;
    local($no, $date, $firm, @rest, $line, @list, @name, @no, $totalcount);

while ( ($key, $val) = each %input ) {
push(@lines, "<li> $key = $val\n");
}

    foreach ( @firms ) {
	($no, $firm, $pakke, $k1, $k2) = (split('"'))[0,2,11,14,15];
	$firm =~ s/^\s+//;	

	if ($input{'format'} eq 'ps') {
	    $latexfirm = $firm;
	    $latexfirm =~ s/([\%\$\^\#\_\~\&])/\\$1\{\}/;
	    $line = sprintf("%s& %d& %s& %s& %s\\\\\n",
			    $latexfirm, $no, $pakke, $k1, $k2);
	} else {
	    $line = sprintf("<a href=%s?Kundenr=%d>%-40s%4d   %-20s %-20s %-15s\n",
			    $finnscript, $no, $firm."</a>", $no, $pakke, $k1, $k2);
	}
	push(@list, $line);

# Kan nå manipulere $firm uten at utskriften endres.
	$firm =~ tr/æøåÆØÅ/[\][\]/; # Ønsker riktig behandling av ÆØÅ.
	push(@name, $firm);	# trenger @name og @no for å gjøre
	push(@no, $no);		# alfabetisk eller numerisk sortering hhv.
    }

    sub byname { 
	$name[$a] cmp $name[$b]; 
    }

    sub bynumber { 
	$no[$a] <=> $no[$b]; 
    }

    if ( $input{'sortering'} eq "numerisk" ) {
	@list = @list[sort bynumber $[..$#name];
    } else {
	@list = @list[sort byname $[..$#name];
    }

    $totalcount = @list;
    $"="";
    if ($input{'format'} ne 'ps') {
	&printhtmlhead("Liste over kunder");
        print <<EOT;

<pre>
Firmanavn                         Kundenr  Annonsepakke         Kontakt1             Kontakt2

@list
</pre>

Tilsammen $totalcount kunder i listen ovenfor.

</body>
</html>
EOT

    } else {
	chdir($tmpdir) || &error("Failed to cd to $tmpdir");
	open(STDERR, "/dev/null");
	open(LATEX, ">tmp.$$.tex") || &error("Failed to create tmp-file");

	print LATEX <<EOT;
\\documentstyle[A4,isolatin,psfig]{article}
\\begin{document}
\\psfig{figure=/local/www/on/www/kunder/www-i.ps,width=6cm}
\\section*{Liste over kunder}
\\small
\\begin{tabular}{lrlll}
Firmanavn& Kundenr& Annonsepakke& Kontakt 1& Kontakt 2\\\\
\\hline
@list
\\end{tabular}

Tilsammen $totalcount kunder i listen ovenfor.

\\end{document}
EOT
        close(LATEX);
        system("latex tmp.$$.tex > /dev/null");
	$| = 1;			# Husk å flush'e stdout før dvips gir output
	print "Content-type: application/postscript\n\n";
	system("dvips -f < tmp.$$.dvi; rm tmp.$$.*");
    }
    exit 0;
}



sub showfirm {

    $entry = @_[0];
    @old = split('"', $entry);
    foreach ( @fields ) {
	$old{$_} = shift(@old);
    }


    print "Content-type: text/html\n\n";

    open(FORM, $nykundeform) || 
	&error("Finner ikke FORM for ny registrering ($nykundeform)");

    while ( <FORM> ) {
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

	s/(<form .+>\n)/$1<input type=hidden name="Kundenr" value="$Kundenr">/;
	s/action=".+"/action="$endrescript"/ig;
	s/(Firmainformasjon)/$1, kundenummer: $old{'Kundenr'}/;
	s/<input\s+type="submit"[^>]*>/<input type="submit" value="Oppdater kundedatabasen">/ig;
	s/<option\s+selected>/<option>/;
	s/<option>\s*($old{$lastselect})/<option selected>$1/gi;

	print;
    }
    close(FORM);

    exit 0;
}


sub nomatch {

    while ( ($key, $val) = each %input ) {
	push(@lines, "<li> $key = $val\n");
    }

    &printhtmlhead("Liste over kunder");
    print <<EOT;
De angitte søkeparametrene passer ikke med noen av postene i kundedatabasen.

@lines

</body>
</html>
EOT

    exit 0;
}


sub printhtmlhead {
    $title = @_[0];

    print <<EOT;
Content-type: text/html

<html>
<head>
 <title>$title</title>
 <link rev=made href="mailto:webmaster@oslonett.no">
</head>
<body background="/gifs/on/onbg.gif">
<img alt="" src="/gifs/on/www-i.gif">

<h1>$title</h1>

EOT

}

