#!/local/bin/perl -w
#
# Definerer felles variable og rutiner for forskningsdagenes CGI-scripts
#
# KGN, sist endret 8.9.95


umask 002;

$mailadr	= "webmaster\@oslonett.no";
$timeout	= 10;
$LOCK_EX	= 2;
$LOCK_UN	= 8;

$basedir	= "/local/www/div/oi/fd95/respons";
$intdir		= "/local/www/div/oi/fd95/respons/intern";

$gifurl		= "http://$ENV{'SERVER_NAME'}/forskdag95/gifs";
$baseurl	= "http://$ENV{'SERVER_NAME'}/forskdag95/respons";
$utscript	= "$baseurl/ut.cgi";
$redutscript	= "$baseurl/intern/redut.cgi";
@mnd		= ("januar", "februar", "mars", "april", "mai", "juni",
		   "juli", "august", "september", "oktober", "november",
		   "desember");

system("chmod -R go+rX,g+w $basedir > /dev/null >&1");


sub getinput {
# Leser inn data (med method GET eller POST) og plasserer dem i en
# assosiativ array, der nøklene i array'en er feltnavnene

    local($i, $name, $value, $data, @data);

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
	$value = &htmlescape($value);
	$name =~ tr/A-ZÆØÅ/a-zæøå/;
        $input{$name} =  $value; # assosier verdi med feltnavn...
	push(@names, $name);	# ...og ta vare på feltrekkefølgen
    }
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
<body bgcolor="#e0e0e0" text="42315a" alink="ff8410" vlink="ff8410" link="295239">
<center>
<img src="$gifurl/fd95-logo-inv.gif" alt="Forskningsdagene '95" >
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
# forsøket på å flock'e ble gitt opp.

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



sub dato {
    local(@t) = (localtime(time));
    sprintf("%d.%d.%d %02d:%02d:%02d", $t[3], $t[4]+1, @t[5,2,1,0]);
}



sub uniquenumber {
    local($counterfile) = $_[0];
    local($counter);

    $SIG{'ALRM'} = 'handletimeout';	# Må ikke blokkere uendelig hvis
    alarm($timeout);			# filen ved en feil er låst permanent

    open(COUNTER, "+<$counterfile") || open(COUNTER, ">$counterfile") 
	|| &error("Kunne ikke åpne tellerfilen ($counterfile)");
    flock(COUNTER, $LOCK_EX);
    $SIG{'ALRM'} = 'IGNORE';		# Kan nå lese og oppdatere trygt
    $counter = <COUNTER> || 0;	# Leser inn sist brukte registreringsnummer
    seek(COUNTER, 0, 0);
    print COUNTER ++$counter, "\n";

    flock(COUNTER, $LOCK_UN);		# Frigir datafilen igjen
    close(COUNTER);
    $counter;				# Returner ny tellerverdi
}


1;		# Returnerer 1 siden det er en lib-fil
