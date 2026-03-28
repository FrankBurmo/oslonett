#!/local/bin/perl
#
# Definerer felles variable og rutiner for forskningsdagenes CGI-scripts
#
# KGN, 11.7.95


umask 002;
$mailadr	= "kgn\@oslonett.no";
$fieldsep	= "\`";
$sepcode	= "\'";
$datosep	= ", ";
$timeout	= 10;
$LOCK_EX	= 2;
$LOCK_UN	= 8;
$masterpw	= "lF/XBpowxwRMM";
# $masterpw er manuelt generert: $masterpw = crypt($klartekst, $salt),
#  der $salt er tilfeldig valgt kombinasjon av to tegn i [a-zA-Z0-9./].

@arrfields	= ("Nummer", "Arrangement", "Beskrivelse", "Dato",
		   "Institusjon", "Fylke", "Beliggenhet", "Maskin");
@instfields	= ("Nummer", "Institusjon", "Kategori", "Maskin");

@samechar	= ("Àà", "Áá", "Ââ", "Ãã", "Ää", "Åå", "Ææ", "Çç", "Èè", "Éé",
		   "Êê", "Ëë", "Ìì", "Íí", "Îî", "Ïï", "Ðð", "Ññ", "Òò", "Óó",
		   "Ôô", "Õõ", "Öö", "Øø", "Ùù", "Úú", "Ûû", "Üü", "Ýý", "Þþ" 
		   );

# directories skal ikke avsluttes med '/'.
$basedir	= "/local/www/div/oi/fd95";

$instdir	= "$basedir/data/inst";
$instindeks	= "$instdir/inst-indeks.txt";
$instteller	= "$instdir/inst-teller.txt";

$arrdir		= "$basedir/data/arr";
$arrindeks	= "$arrdir/arr-indeks.txt";
$arrteller	= "$arrdir/arr-teller.txt";

$baseurl	= "http://$ENV{'SERVER_NAME'}/div/oi/fd95";
$insturl	= "$baseurl/data/inst";
$arrurl		= "$baseurl/data/arr";

@mnd		= ("januar", "februar", "mars", "april", "mai", "juni",
		   "juli", "august", "september", "oktober", "november",
		   "desember");

system("chmod -R go+rX,g+w $basedir > /dev/null >& /dev/null");


sub getinput {
# Leser inn data (med method GET eller POST) og plasserer dem i en
# assosiativ array, der nøklene i array'en er feltnavnene

    local($i, $name, $value, $data, @data, %input);

    if ($ENV{'REQUEST_METHOD'} eq "GET") {
        $data = $ENV{'QUERY_STRING'};
    } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
        read(STDIN, $data, $ENV{'CONTENT_LENGTH'});
    } else {
	return;
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

        # Hvis kun whitespace er sendt med ignoreres dette name-value paret
        next if $value !~ /\S/;

        # En/flere forekomster av whitespace i $value oversettes til SPC
        $value =~ s/\s+/ /g;

	# Forekomster av $fieldsep er ulovlige og erstattes derfor av $sepcode
	$value =~ s/$fieldsep/$sepcode/g;

	# Unngå forekomster av " i $value - dette avslutter feltene i
	# *.updateinfo for tidlig.
	$value =~ s/\"/\'/g;

	$value = &htmlescape($value);

        $input{$name} .= ($input{$name}?$datosep:"") . $value;
    }
    $input{'Maskin'} = $ENV{'REMOTE_HOST'};
    %input;                     # returnerer den assosiative array'en
}



sub htmlescape {
    local($text) = $_[0];

    $text =~ s/&/&amp;/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    return $text;
}


sub error {

    local($msg) = $_[0];

    print &header("Feilmelding");
    print <<EOT;
Programmet ble avbrutt med følgende feilmelding:
<blockquote>
  <center>
  <hr noshade size=2>
  <b><font size="+1">$msg</font></b>
  <hr noshade size=2>
  </center>
</blockquote>

Dersom du har spørsmål eller kommentarer kan du ta kontakt med <a
href="mailto:$mailadr">$mailadr</a>.
EOT
    print &footer;
    exit 1;
}


sub header {
    local($title) = $_[0];

    return qq@<html>
<head>
 <title>$title</title>
</head>
<body bgcolor="ffffff" text="42315a" alink="ff8410" vlink="ff8410" link="295239">
<center>
<img src="$baseurl/gifs/fd95-logo-inv.gif" alt="Forskningsdagene '95" >
</center>
<h1>$title</h1>
@;

}



sub footer {
 
    return qq!
<p>
<hr size="1" noshade>

<address>
  Tilrettelagt for <a href="/div/oi/fd95/">Forskningsdagene '95</a> av <a href="/">Oslonett AS</a>.
</address>

</body>
</html>
!;
}




sub handletimeout {
# Før flock() kalles setter vi opp en alarm som kaller denne prosedyren
# etter $timeout sekunder. Prosedyren returnerer altså feilmelding hvis
# forsøket på å flocke ble gitt opp.

    print &header("Får ikke tilgang til databasen");
    print <<EOT;
<h2>Datafilen eller tellerfilen er låst av en annen prosess. 
Forsøk igjen litt senere.</h2>

Om problemet skulle være vedvarende, ta kontakt med 
<a href="mailto:$mailadr">$mailadr</a>.
EOT

    print &footer;
    exit 2;
}


sub regexp_escape {
    local($i);

    foreach $i ( $[ .. $#_ ) {
	if (defined($_[$i])) {
	    $_[$i] =~ s/([.*+?&()\[\\\]])/\\$1/g;
	    $_[$i] =~ s/\s*\|+\s*/|/g;
	}
    }
}


sub case_insensitivize {
# Treat national characters specially: in each argument, substitute
# 'Ø' or 'ø' with '[øØ]' etc. Chars to translate are listed in @samechar.
    local($i);

    foreach $i ( $[ .. $#_ ) {
	if (defined($_[$i])) {
	    $_[$i] =~ s/($specialcase)/$bothcases{$1}/g;
	}
    }
}


foreach $entry (@samechar) {
    $specialcase .= $entry;
    foreach $char ( split(//, $entry)) {
	$bothcases{$char} = "\[$entry\]";
    }
}
$specialcase = "\[$specialcase\]";

1;		# Returnerer 1 siden det er en lib-fil
