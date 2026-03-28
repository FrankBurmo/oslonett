#!/local/bin/perl

$DISKUSJONDIR	= "/local/www/dnlf/diskusjon/generelt";

%input = &getinput;

if (! length $input{'id'} ) {
    # no article id given, respond with fill-in form
    &header("Slett innlegg");
    print <<EOT;

For å slette et gammelt innlegg må du oppgi identifikasjonsnummer for
den artikkelen du vil slette (dette finner du i URL\'en til innlegget
du vil slette)

<form method="POST" action="$ENV{'SCRIPT_NAME'}">

<font size="+2">Innlegg-id:</font>

<input name="id" value="$input{'id'}" size="10"><p>

<input type="submit" value=" Slett innlegg ">

</form>
EOT

&footer;
exit 0;


} else {
    $filename = sprintf("$DISKUSJONDIR/art%05d.txt",
			$input{'id'});

    if ( rename($filename, "$filename.backup") ) {
	&header("Har slettet innlegg");
	print "Innlegg nr. $input{'id'} er nå slettet fra ";
    } else {
	&header("Ingen sletting utført...");
	print "...fordi angitt artikkel (id=$input{'id'}) ikke finnes.<p>\n";
	print "Tilbake til ";
    }
    print qq!<a href="/diskusjon/forum.cgi/generelt">!;
    print qq!diskusjonsgruppen</a>.<p>\n!;

    &footer;
    exit 0;
}


sub header {
    local($txt) = $_[0];

    return if $HEADER++;

    print <<EOT;
Content-type: text/html

<html>
<head>
  <title>$txt</title>
</head>
<body bgcolor="#ffffaa">
<h1>$txt</h1>
EOT
}


sub footer {
    print "\n</body>\n</html>\n";
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

