#!/local/bin/perl
#

# initialiserer globale variable:
#
# @fields       definisjon av hvilke felter som skal lagres i datafilen 
#               NB! Alle scripts som bruker datafilen, samt HTML FORMS
#               som sender data til disse script'ene må bruke formatet 
#               angitt i @fields (samme rettskriving)
# %skip         hvilke felter vi ikke er interessert i å lagre i datafilen
# 		men som godt kan forekomme i input fra HTML FORM
# @required     hvilke felter som _må_ være utfylt for at registreringen
#		skal godtas og lagres i datafilen
#
# --- finnkunde-scriptet leser $nykundeform og legger inn kjent informasjon.
# --- Til dette trengs noen variable som angir typen de ulike input-feltene
# @simplefields	Angir hvilke enkle <input>-felter
# @radiobuttons Angir hvilke felter med tag <input type="radio"...>
# @textareas	Angir hvilke felter som har input lest inn i "textarea"
#
# $fieldsep     feltseparator i datafilen
# $sepcode      erstatning for opprinnelig forekomster av $fieldsep
#
# --- Nødvendige filnavn og URL'er defineres i denne filen
# $datafile     datafilen
# $counterfile  tellerfilen
# $errlogfile	feil-logg
# $nykundeform	html-fil som inneholder skjema for nyregistrering av kunder
# $pslogofile   fil som inneholder SchibstedNett/WWW-logo. inkluderes i ps-dokument
# $tmpdir	filområde for mellomlagring
# $endrescript	URL til script for å oppdatere kundedata
# $finnscript	URL til script med søkegrensesnitt til databasen
#
# $timeout      maksimalt # sekunder før vi gir opp å få tilgang til låst fil
# $mailadr      adressen man henvises til for informasjon/kommentarer
# $LOCK_EX      Parameterverdi til flock(): "exclusive lock"
# $LOCK_UN      Parameterverdi til flock(): "unlock"



%fieldname	= ("Medlemsnr", "Medlemsnummer",
		   "RegDato", "Registreringsdato",
		   "EndreDato", "Dato for siste endring",
		   "Firma", "Firma",
		   "Kontakt", "Kontaktperson",
		   "Adresse", "Adresse",
		   "Postnr", "Postnummer",
		   "Poststed", "Poststed",
		   "Telefon", "Telefon",
		   "Telefax", "Telefax",
		   "Email", "E-mail",
		   "URL", "URL",
		   "Diverse", "Diverse",);

@fields		= ("Medlemsnr", "RegDato", "EndreDato", "Firma", "Kontakt",
		   "Adresse", "Postnr", "Poststed", "Telefon", "Telefax",
		   "Email", "URL", "Diverse"); 

# (Rekkefølgen av elementene i @fields er vesentlig.
#  Kan derfor ikke bruke keys(%fieldname) for @fields.

@simplefields	= ("Firma", "Kontakt", "Adresse", "Postnr", "Poststed", 
		   "Telefon", "Telefax", "Email", "URL" );

@textareas	= ("Diverse");

@skip		= ("mailto", "reply-to", "subject", "cc", 
		   "sortering", "format");
@required	= ("Firma", "Adresse", "Postnr", "Poststed");

$fieldsep	= '"';		# Man mister alle forekomster av ", erstatter
$sepcode        = '\'';		# disse med ' som antas å være likeverdig.

$endrescript	= 'http://www.sn.no/fono/adm/editmdl.cgi';
$finnscript	= 'http://www.sn.no/fono/finnmdl.cgi';
$privfinnscript	= 'http://www.sn.no/fono/adm/finnmdl.cgi';

$basedir	= '/local/www/nl/ndiv/fono';
$counterfile 	= "$basedir/lib/FONO-medlemsteller.txt";
$errlogfile 	= "$basedir/lib/FONO-medlemsfeil.txt";
$datafile 	= "$basedir/lib/FONO-medlemsdata.txt";
$nykundeform 	= "$basedir/adm/nyttmdl.htm";
$pslogofile 	= "$basedir/lib/fono.ps";
$tmpdir 	= '/local/www/tmp';

$mailadr = 'steinar@a.sn.no';
$textareawidth = 60;
$tablesize = 55;
$timeout = 15;
$LOCK_EX = 2;
$LOCK_UN = 8;

# Gjør chmod i fall det ikke var gjort fra før
chmod 0664, $datafile, $counterfile, $errlogfile;
foreach (@skip) { $skip{$_} = 1; }

1;			# returnerer 1 siden dette er en bibliotek-fil



sub getinput {
# Leser inn data (med method GET eller POST) og plasserer dem i en
# assosiativ array, der nøklene i array'en er feltnavnene

    local($i, $name, $value, $data, @data, %input);

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

        # Hvis kun whitespace er sendt med ignoreres dette name-value paret
        next if $value !~ /\S/;

        # En/flere forekomster av SPC, CR og LF i $value oversettes til SPC
        $value =~ s/\s+/ /g;

        # Feltseparatoren er ulovlig i $value, koder denne som $sepcode
        $value =~ s/$fieldsep/$sepcode/g;

        $input{$name} = $value;
    }
    %input;			# returnerer den assosiative array'en
}



sub handletimeout {
# Før flock() kalles setter vi opp en alarm som kaller denne prosedyren
# etter $timeout sekunder. Prosedyren returnerer altså feilmelding hvis
# forsøket på å flock'e ble gitt opp.

    &printheader("Får ikke tilgang til databasen");
    print <<EOT;
<h2>Datafilen er låst av en annen prosess.</h2>

Forsøk igjen litt senere. <p>

Om problemet skulle være vedvarende, ta kontakt med 
<a href="mailto:$mailadr">$mailadr</a>.
EOT
    &printfooter;
    &logerror("Datafil flock'et - gir opp etter $timeout sekunder");
    exit 2;
}



sub printfooter {
# Skriver ut en standard HTML footer-tekst
    print <<EOT;
<p>
<address>
<hr noshade size=1 width=30% align=left>
   <a href="http://www.sn.no/fono/">
   <img src="/fono/img/icon.gif"
        alt="[FONO-Hjemmeside]"
     valign=middle align=left
     border="0"></a>

   <a href="http://www.sn.no">
   <img src="http://www.sn.no/img/horisont.gif"
        alt="[SN Horisont]"
     valign=middle align=right
     border="0"></a>
</address>

</body>
</html>
<!-- Alle programmer og skript (C) Schibsted Nett, 1996 -->
<!-- Kontakt oss for nærmere info hvis likn. løsninger ønskes -->
EOT
}



sub printheader {
# Skriver ut en standard HTML header, dokumenttittel hentes fra 1. parameter
    local($title) = @_[0];

    print <<EOT;
Content-type: text/html

<html><head>
<title>$title</title>
 <link rev=made href="mailto:webmaster@sn.no">
</head>
<body background="/fono/img/back.gif" bgcolor="#ffffff">
<table><tr><td valign=top width=25%>
<a href=/fono/><img alt="" align=left SRC=/fono/img/logo.gif border=0></a><br><pre>               </pre><td valign=top> <h1>Foreningen Norske Plateselskaper<br><a href="/fono/img/menu.map"><IMG SRC="/fono/img/ssm_menu.gif" border=0 ismap alt=""></a></h1>
</table>
<br clear=all>

<h2>$title</h2>

EOT
}



sub logerror {
# Logger meldingen(e) angitt i parameter(ene) til $errlogfile.
# Gjør ingen file-locking, gir opp hvis ikke filen lar seg åpne.

    open(LOG,">>$errlogfile") || return;
    printf LOG "%s: %s\n", &dato, join(" ", @_);
    close(LOG);
}
    

sub error {
# Returner HTML-kode med feilmeldingen gitt i første parameter
    &printheader("Feilmelding");
    print <<EOT;
CGI-scriptet ble avbrutt med føglende feilmelding:
<blockquote>
<hr noshade size=1>
<p>
<strong>
@_
</strong>
<p>
</hr noshade size=1>
</blockquote>
EOT
    exit 1;
}
    


sub dato {
# Returnerer tekst med dato og tid på formen "yymmdd hh:mm:ss", der
# tidspunktet er oppstartingstiden for det kjørende script'et

    ($s,$m,$h,$mday,$mon,$year,@rest) = localtime($^T);
    sprintf("%02d%02d%02d %02d:%02d:%02d",
            $year,$mon+1,$mday, $h,$m,$s);
}



sub decode {
# Tar en linje med en datapost som input. Bryter denne opp ved hver 
# $fieldsep og returnerer en assosiativ array med keys = elementene
# i @fields og values = verdiene fra parameteren.
    local($entry) = @_[0];
    local(@values, $name, %old);

    @values = split($fieldsep, $entry);
    for $name ( @fields ) {
	$old{$name} = shift(@values);
    }
    %old;
}
