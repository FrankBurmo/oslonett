#!/local/bin/perl5

$KVITTERING	= 'http://www.sn.no/sp/hballvm95/trekke-kvitt.html';
$LOGGFIL	= '/local/www/sp/hballvm95/diskusjon-adm/trekke-logg.txt';

%input = &getinput;

unshift(@datanames, 'Dato');
chop($input{'Dato'} = `/usr/bin/date`);
push(@datanames, 'Remote host');
$input{'Remote host'} = $ENV{REMOTE_HOST} || $ENV{REMOTE_ADDR};
if (length $input{REMOTE_USER}) {
    push(@datanames, 'Remote user');
    $input{'Remote user'} = $ENV{REMOTE_USER};
}

open(LOG, ">>$LOGGFIL") || &logfailed;
print LOG "\n";
foreach (@datanames) {
    printf LOG "%-25s %s\n", $_.':',$input{$_};
}
close LOG || &logfailed;

print "Location: $KVITTERING\n\n";
exit 0;


sub getinput {
# Return %input array, associating input names with input values
# Also builds global array @datanames, giving original order of input
# field names.
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

        $value =~ s/\s+/ /g;
        push(@datanames, $name);
        $input{$name} = $value;
    }
    %input;                     # returnerer den assosiative array'en
}



sub logfailed {
    print "Content-type: text/html\n\n";
    print <<EOT;
<html>
<head>
<title>
Kunne ikke lagre navnet og adressen din
</title>
</head>

<body background="/sp/hballvm95/img/vmlogo-bg.jpg">

<a href="/sp/hballvm95/">
<img alt="[Hjem]" src="/sp/hballvm95/img/vmikon.gif"
     border="0" align="right"></a>

<h1>Kunne ikke lagre navnet og adressen din</h1>

<font size="+1">
På grunn av en teknisk feil, kunne programmet ikke lagre de innsendte
opplysningene fra deg.<p>

Ta gjerne kontakt med <a href="mailto:webmaster\@sn.no">webmaster\@sn.no</a>.
</font>

<address>
<hr size="1" noshade align="center" width="20%">
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
    exit 0;
}
