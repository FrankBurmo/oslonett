#/!local/bin/perl5

$TOP		= "/home/frogner/www/uh/am-kat";
$CATFILE	= "$TOP/intern/katalog.txt";
$ITEMINDEX	= "$TOP/intern/item-index"; # dbm file mapping item.no -> filepos
$CATINDEX	= "$TOP/intern/cat-index"; # dbm file mapping cat.name -> filepos
$REPLYADDR	= 'www@sn.no';

$ITEMLOG	= "$TOP/intern/itemlog.txt";
$SEARCHLOG	= "$TOP/intern/searchlog.txt";
$GIFURL		= "/uh/am-kat/gifs";

@FIELDS		= qw(product category no artist title
		     recording year price cover1 cover2);
@NORSKEFELTER	= qw(Produkttype Kategori Katalognummer Artist/gruppe 
		     Tittel Innspilling År Pris Forsidebilde Baksidebilde);
@NORSKEFELTER_SPILL	= qw(Produkttype Plattform Katalognummer Kategori
		     Tittel Informasjon År Pris Forsidebilde Baksidebilde);
@ENGELSKEFELTER	= ('Product type', 'Category', 'Catalogue number',
		   'Artist/group', 'Title', 'Recording', 'Year', 'Price',
		   'Front cover', 'Back cover');
%TRANSLATE_CAT	= (
		   'barneplater',		'children\'s music',
		   'div. klassisk',		'misc. classical',
		   'div. pop & rock',		'misc. pop & rock',
		   'etnisk',			'ethnic',
		   'film- /tv-musikk - musicals','film- /tv-music - musicals',
		   'klassisk',			'classical',
		   'new-age / elektronisk',	'new-age / electronic',
		   'underholdning',		'entertainment',
		   );
%TRANSLATE_ART	= (
		   'diverse artister',		'misc. artists',
		   'div. artister',		'misc. artists',
		   'diverse lydeffekter',	'misc. sound effects',
		   );


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
        $input{$name} = $value;
    }
    %input;                     # returnerer den assosiative array'en
}


sub error {
# returns HTML error message and exits program
    local($msg) = $_[0];

    &printheader("Feilmelding");
    print <<EOT;
Programmet ble avbrut med følgende feilmelding:
<blockquote>
<hr noshade size="2">
<font size="+1">
$msg
</font>
<hr noshade size="2">
</blockquote>

Eventuelle spørsmål kan rettes til <a
    href=\"mailto:$REPLYADDR\">$REPLYADDR</a>.
EOT
    &printfooter; 
    exit 1;
}


sub printheader {
    local($head, $shop) = @_;
    return if $VISITED++;

    $headerimage = qq!<a href="http://www.sn.no/kurv/vis.cgi"><img ! .
	qq!alt="[Vis innhold i handlekurv}" border="0" ! .
	    qq!src="/uh/am-kat/gifs/visinnhold.gif" align="right"></a>!
		if length $shop;
    $nyhet = "
<h1>Nyhet! Nå kan du også bestille via internett hos Akers Mic</h1>

Når du finner varer du har lyst til å kjøpe, legger du dem i den
elektroniske handlekurven din med et trykk på knappen ved siden av
hver vare. Hvis du ombestemmer deg kan du ta varer ut av handlekurven
igjen. Oversikten over hva du har kjøpt viser også hvor mye du har
handlet for.<p>

Handlekurven kan du ta med deg til alle butikkene i Schibsted Netts
virtuelle handlesenter. Når du vil bestille, henter du lett frem et
bestillingsskjema hvor du fyller inn navn, adresse osv. slik at varen
kan sendes til deg.

" if length $shop;

    print <<EOT;
<html>
<head>
 <title>$head</title>
 <link rev="made" href="mailto: $REPLYADDR">
</head>
<body background="$GIFURL/bg.gif" link="#0000ff" vlink="#000088">
<img alt="AkersMic" border="0" src="$GIFURL/logo.gif" width="375" height="55" align="left">$headerimage
<br clear="all">
$nyhet
<h1>$head</h1>
EOT

}


sub printfooter {
    print <<EOT;

<p>
  <hr>
   <center>
   <a href="/home/akersm/menubar.map"><img alt="Menylinje (7kB)" border="0"
     src="/home/akersm/gifs/menubar.gif" ismap></a>
   <br>
   <a href="/home/akersm/index.html">[Home]</a>
   <a href="/home/akersm/katalog/search_f.html">[Søk/Shopping]</a>
   <a href="/home/akersm/musikk/musikk.html">[Musikk]</a>
   <a href="/home/akersm/video/video.html">[Video & LaserDisc]</a>
   <a href="/home/akersm/spill/spill.html">[Spill & Multimedia]</a>
   <a href="/home/akersm/hifsu/hifsu.html">[HiFi & Surround]</a>
   <a href="/home/akersm/tandb/tand01.html">[Tandberg]</a>
   <a href="/home/akersm/butikk/butikker.html">[Akers Mic Butikkene]</a>
   <hr>

   Copyright © 1995
   <a href ="mailto:akersm\@sn.no">Akers Mic</a>
   <p>
   Laget for AkersMic av <a href="http://www.sn.no/">Schibsted Nett AS.</a>
</body>
</html>
EOT
}


sub printfooter_eng {
    print <<EOT;

<p>
<hr>
<center>
<a href="/home/akersm/menu_eng.map">
<img alt="Menubar (7kB)" border="0" src="/home/akersm/gifs/menu_eng.gif" 
    ismap>
</a><br>
   <a href="/home/akersm/index_e.html">[Home]</a>
   <a href="/home/akersm/katalog/sear_fe.html">[Search]</a>
   <a href="/home/akersm/musikk/music.html">[Music]</a>
   <a href="/home/akersm/video/video_e.html">[Video & LaserDisc]</a>
   <a href="/home/akersm/spill/games.html">[Games & Multimedia]</a>
   <a href="/home/akersm/hifsu/hifi_eng.html">[HiFi & Surround]</a>
   <a href="/home/akersm/tandb/tandeng.html">[Tandberg]</a>
   <a href="/home/akersm/butikk/stores.html">[Akers Mic Stores]</a>
   <hr>
   Copyright © 1995 
   <a href ="mailto:akersm\@sn.no">Akers Mic</a><br>

Programmed for <a href="http://www.sn.no/home/akersm/">AkersMic</a> by
<a href="http://www.sn.no/">Schibsted Nett AS</a>
</center>
</body>
</html>
EOT
}

