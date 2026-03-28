#!/local/bin/perl5

# Definisjon av felles konstanter og subrutiner for diskusjonsgruppe-system
#
# For å legge opp diskusjongsruppe for ny bruker er det nok å forandre
# konstantene $TOPPDIR, $TOPP, $NOTIFYRCPT samt prosedyrene "header" og
# "footer".
#
# I directory'et $TOPPDIR legger man opp "diskusjon.cgi" og lager et nytt
# sub-directory "diskusjon-adm". I dette directory'et legger man opp
# script'ene cancel.cgi (master cancel) og newgroup.cgi. Det nye 
# subdirectory'et må adgangsbeskyttes i web-serveren slik at ikke uatoriserte
# brukere kan kansellere andres innlegg eller lage nye grupper.


$TOPPDIR	= "/local/www/newsdesk";
$TOPP		= "/newsdesk";
$NOTIFYRCPT	= 'kgn@oslonett.no'; # Mottaker av beskjeder om nye innlegg.


$DISKUSJONDIR	= "$TOPPDIR/diskusjon-adm";
$TELLERFIL	= "$DISKUSJONDIR/teller.txt";
$MININDENT	= "      ";
@PWCHAR		= ("a" .. "z", "A".."Z", "0".."9", "_");
@MND		= ("januar", "februar", "mars", "april", "mai", "juni", "juli",
                   "august", "september", "oktober", "november", "desember");



sub header {
    local($txt) = $_[0];

    return if $HEADER++;
    print <<EOT;
Content-type: text/html

<html>
<head>
<title>$txt</title>
</head>
<body bgcolor="#ffffff" text="#000000">

<h1>Newsdesk</h1>

<h1>$txt</h1>

EOT
}


sub footer {
    print <<EOT;

<p><hr noshade>
<center>
<a href="$TOPP/">Tilbake til Newsdesk's forside</a>
</center>
</body>
</html>
EOT
}





sub escape {
    local($i);
    foreach $i ($[ .. $#_) {
        $_[$i] =~ s/\&/&amp;/g;
        $_[$i] =~ s/\&amp;(\w{1,6}|#\d{1,3});/&$1;/g;
        $_[$i] =~ s/æ/&aelig;/g;
        $_[$i] =~ s/ø/&oslash;/g;
        $_[$i] =~ s/å/&aring;/g;
        $_[$i] =~ s/Æ/&AElig;/g;
        $_[$i] =~ s/Ø/&Oslash;/g;
        $_[$i] =~ s/Å/&Aring;/g;
        # This is a good place to make sure no 
	# user can exploit server side includes!
        $_[$i] =~ s/<\!/<!-- /g;
    }
}



sub dato {
    local(@t);
    @t = localtime(time);
    return sprintf("%d. %s %d %02d:%02d:%02d",
		   $t[3], $MND[$t[4]], $t[5], @t[2,1,0]);
}



sub urlescape {
    local($url) = $_[0];
    # some chars are illegal in URLs. Code these as %<hexcode>

    $url =~ s!(["% &?/])!sprintf("%%%02X",unpack("c",$1))!ge;
    return $url;
}




sub error {
    local($msg) = $_[0];

    &header("Feilmelding");

    print "Programmet ble avbrutt med følgende feilmelding:\n\n<blockquote>\n";
    print qq!<hr size="2" noshade>\n<font size="+1"><b>$msg</b></font>\n!;
    print qq!<hr size="2" noshade>\n</blockquote>\n!;
    &footer;
    exit 0;
}



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

        # En/flere forekomster av whitespace i $value oversettes til SPC

        $value =~ s/\n/<br>/g;
        $input{$name} =  $value; # assosier verdi med feltnavn...
    }
    return %input;
}

1;				# return 1 since this is a library file
















