#!/local/bin/perl5

$TOPP           = "/local/www/newsdesk";
$TOPPURL        = "/newsdesk";
$DISKUSJONDIR	= "$TOPP/diskusjon-adm";

%input = &getinput;
$urlgruppe = &urlescape($input{'gruppe'});

if (! length $input{'gruppenavn'}) {
    # no group name given, respond with fill-in form
    &header("Opprett ny diskusjons-gruppe");
    print <<EOT;

Herfra kan det lages nye grupper. Følgende diskusjonsgrupper finnes allerede:

<form method="POST" action="$ENV{'SCRIPT_NAME'}">

<ul>
EOT
    opendir(DIR, $DISKUSJONDIR)
	|| &error("Kunne ikke åpne directory\'et $DISKUSJONDIR");
    foreach (sort readdir(DIR)) {
        next if /^\./;
	next if /^bin$/;
	next unless -d $_;
	$urlgr = &urlescape($_);

	( $noquotes = $_ ) =~ s/\"/&quot;/g;
	print qq! <li> <a href="$TOPPURL/diskusjon.cgi/$urlgr">$_</a><br>\n!;
    }
    closedir(DIR);
    
    print <<EOT;
</ul>

<font size="+2">Navn på ny gruppe:</font>
<input name="gruppenavn" size="40"><p>

<center><input type="submit" value=" Lag ny gruppe "></center>

</form>
EOT

&footer;
exit 0;


} else {
    &error("Angitt gruppe finnes allerede")
	if -d "$DISKUSJONDIR/$input{'gruppenavn'}";
    mkdir("$DISKUSJONDIR/$input{'gruppenavn'}", 0775);

    &header("Har opprettet ny gruppe");
    $urlgr = &urlescape($input{'gruppenavn'});
    print <<EOT;

Den nye gruppen har URL'en <a
href="$TOPPURL/diskusjon.cgi/$urlgr">http://$ENV{'SERVER_NAME'}$TOPPURL/diskusjon.cgi/$urlgr</a>.<p>

<center>
<a href="$ENV{'SCRIPT_NAME'}">Opprette flere nye grupper</a>
</center>
EOT
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
<body bgcolor="#ffffff">

<a href="/">
   <img src="/img/sn_horisont_liten_inv.gif" 
        alt="[SN Horisont]" 
     valign=middle 
     border="0"></a>
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

