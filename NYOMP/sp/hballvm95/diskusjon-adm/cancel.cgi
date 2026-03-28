#!/local/bin/perl

$TOPPDIR        = "/local/www/sp/hballvm95";
$TOPP           = "/sp/hballvm95";
$DISKUSJONDIR	= "$TOPPDIR/diskusjon-adm";
$DISKUSJONURL	= "$TOPP/diskusjon-adm";

%input = &getinput;
$urlgruppe = &urlescape($input{'gruppe'});

&error("Ingen diskusjonsgruppe angitt") 
    if (length $input{'id'} && !length $input{'gruppe'});
if (! length $input{'id'}) {
    # no article id given, respond with fill-in form
    &header("Redaksjonens Master Cancel");
    print <<EOT;

For å slette et gammelt innlegg må du oppgi diskusjonsgruppe og
identifikasjonsnummer for den artikkelen du vil slette (dette finner
du i URL\'en til innlegget du vil slette)

<form method="POST" action="$DISKUSJONURL/cancel.cgi">

<font size="+2">
Velg diskusjonsgruppe du vil slette innlegg fra:</font>
<blockquote>
EOT
    opendir(DIR, $DISKUSJONDIR)
	|| &error("Kunne ikke åpne directory\'et $DISKUSJONDIR");
    foreach (sort readdir(DIR)) {
        next if /^\./;
	next unless -d $_;
	$urlgr = &urlescape($_);

	$checked = ($_ eq $input{'gruppe'}) ? " checked" : "";
	( $noquotes = $_ ) =~ s/"/&quot;/g;
	print qq!<input type="radio" name="gruppe" value="$noquotes" $checked> !;
	print qq!<a href="$TOPP/diskusjon.cgi/$urlgr">$_</a><br>\n!;
    }
    closedir(DIR);
    
    print <<EOT;
</blockquote>
<font size="+2">Innlegg-id:</font>

<input name="id" value="$input{'id'}" size="10"><p>

<input type="submit" value=" Slett innlegg ">

</form>
EOT

&footer;
exit 0;


} else {
    $filename = sprintf("$DISKUSJONDIR/$input{'gruppe'}/art%05d.txt",
			$input{'id'});

    if ( rename($filename, "$filename.backup") ) {
	&header("Har slettet innlegg");
	print "Innlegg nr. $input{'id'} er nå slettet fra ";
	print qq!<a href="$TOPP/diskusjon.cgi/$urlgruppe">!;
	print qq!diskusjonsgruppen $input{'gruppe'}</a>.<p>!;
    } else {
	&header("Ingen sletting utført");
	print "...fordi angitt artikkel (id=$input{'id'}) ikke finnes.<p>\n";
	print qq!Tilbake til <a href="$TOPP/diskusjon.cgi/$urlgruppe">!;
	print qq!diskusjonsgruppen "$input{'gruppe'}"</a> eller !;
	print qq!tilbake til <a href="$ENV{'SCRIPT_NAME'}?gruppe=$urlgruppe">!;
	print "skjema for sletting av inlegg</a>.<p>\n";
    }

    &footer;
    exit 0;
}


sub urlescape {
    local($url) = $_[0];
    # some chars are illegal in URLs. Code these as %<hexcode>

    $url =~ s!(["% &?/])!sprintf("%%%02X",unpack("c",$1))!ge;
    return $url;
}


sub header {
    local($txt) = $_[0];

    return if $HEADER++;
    print <<EOT;
Content-type: text/html

<html>
<head>
 <title>
  $txt
 </title>
</head>
<body background="/sp/hballvm95/img/vmlogo-bg.jpg">

<a href="/sp/hballvm95/">
<img alt="[Hjem]" src="/sp/hballvm95/img/vmikon.gif"
     border="0" align="right"></a>
<h1>$txt</h1>

EOT
}


sub footer {
    print <<EOT;

<p>
<address>
<hr size="1" noshade align="left" width="20%">
<center>
  <font size="-1">
  Disse sidene er laget for <a href="/"><img alt="SN Horisont" 
      border="0" src="/img/horisont.gif" align="absmiddle"></a>
  av <a href="/sn/">Schibsted Nett AS</a>. 
<a href="c.htm">Copyright &#169;</a> 1995.

</address>

</body>
</html>
EOT
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

