#!/local/bin/perl


# gencat.cgi
#
# Dag Wigum, 10.12.95
#
# Genererer en htmlfil med aksjekurser
#



# Neste linje virker kun for method="GET". Bør gi feilmelding hvis dette
# ikke er tilfelle eller bruke read(STDIN, $kat, $ENV{'CONTENT_LENGTH'}
# hvis method="POST".


read(STDIN, $var, $ENV{'CONTENT_LENGTH'});

open(STDERR, "/dev/null");

     @I = split(/\=/,$var);

     $kat = $I[1];



dbmopen(%AKSJER,"aksje",0664) || print "Content-type: text/html\n\nFoo";
dbmopen(%KAT,"kategori",0664) || print "Content-type: text/html\n\nFo";



# Lag title-tag...

$title = "Dagens aksjekurs";

# Lag body-tag...
$body_tag = "<body BGCOLOR=\"#ffffee\" TEXT=\"#000000\"
           LINK=\"#0000ff\" VLINK=\"#aa0000\" ALINK=\"#aa0000\">";


&header;
&katalog;
&footer;

sub header {

    print "Content-type: text/html\n\n";

    print "
<html>
<head>
<title>
$title
</title>
</head>

$body_tag

<h1>$kat</h1>

Kursene er sist oppdatert kl xx.xx, den xx/xx-xx.<p>

Delphi Economics garanterer ikke i noen forstand for informasjonens
korrekthet og tar ikke ansvar for posisjoner tatt på bakgrunn av denne
informasjonen.<p>

<i>Kilde: Oslo Børs, NRK Tekst-TV</i><p>



<table border=1 width=450>
<tr>
<th>Name</th><th>VPnr</th><th>Last</th><th>Volume</th><th>Bid</th><th>Ask</th>
</tr>
";

    return;
}

sub katalog{

    while (defined($KAT{$i.$kat})) {

  @NAMES = split(/\+/,$KAT{$i.$kat});

  foreach $_ (@NAMES) {
    @FIRM = split(/,/);

    @TMP = split(/,/,$AKSJER{$FIRM[0]});
    @KJOP = split(/:/,$TMP[1]);
    @SELG = split(/:/,$TMP[2]);
    @PRIS = split(/:/,$TMP[3]);
    @VOLUM = split(/:/,$TMP[4]);
}
  $i++;

    print "<tr><td>$FIRM[1]</td><td>$FIRM[2]</td><td align=right>$PRIS[1]</td><td align=right>$VOLUM[1]</td><td align=right>$KJOP[1]</td><td align=right>$SELG[1]</td></tr>";  



}
}


sub footer {

    print "
</table>

</body>
</html>

";

    return;
}


dbmclose(%AKSJER);

close FIL;
	
