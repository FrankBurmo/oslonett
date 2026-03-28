#!/local/bin/perl5

$DATADIR = "/local/www/kurv/kunder";

$tillegg{intershop} = qq{
<h2>Leveringsbetingelser for <a href="/sh/is/">InterShop</a></h2>

Varen kan leveres med post (postoppkrav) såfremt samlet vekt ikke
overskrider 30 kg. Alt over 30 kg må avtales nærmere med <a
href="mailto:rsas\@sn.no">InterShop</a>. Firmakunder har også anledning
til å bruke bedriftspakken til Linjegods og Posten.<p>

Velg transport:

<select name="transport">
<option value="postoppkrav" selected>Postoppkrav
<option value="etter_avtale">Intershop tar kontakt
<option value="linjegods">Linjegods' bedriftspakke
<option value="posten">Postens bedriftspakke
</select>
<p>

Oppkrav koster kr 17, eksempel på frakt-kostnad: 5-30 kg = ca. 30-100
kr, etter postverkets satser. Dette kommer i tillegg til prisen angitt
ovenfor.<p>
};

$tillegg{akersmic} = '<h2><a href="/akersmic/order.html">Fraktomkostninger</a> ved bestilling fra 
<a href="/home/akersm/">AkersMic</a></h2>

I tillegg til prisen ovenfor kommer frakt, kr 45.-.
For ytterligere informasjon, kontakt <a href="mailto:akersm@sn.no">akersm@sn.no</a>';

%butikkinfo = (
	       'sn-url',		'/',
	       'sn-attrib',		' bgcolor="#ffffff"',
	       'intershop-vareinfo',	'/local/www/sh/is/perl/vareinfo.pl',
	       'intershop-secondaryimg','/kurv/gifs/handle_full-t.gif',
	       'intershop-secondaryimg-empty',
					'/kurv/gifs/handle_tom-t.gif',
	       'intershop-url',		'/sh/is/',
	       'intershop-logo',	'/sh/is/gifs/rsi.gif',
	       'intershop-attrib',	' bgcolor="#ffffbb" link="#ff2000" vlink="#ff2000"',
	       'akersmic-vareinfo',	'/local/www/uh/am-kat/intern/vareinfo.pl',
	       'akersmic-url',		'/uh/am-kat/form-new.html',
	       'akersmic-logo',		'/uh/am-kat/gifs/logo.gif',
	       'akersmic-vareinfo',	'/local/www/uh/am-kat/vareinfo.pl',
	       'akersmic-attrib',	'background="/uh/am-kat/gifs/bg.gif" link="#0000ff" vlink="#000088"',
	       );


sub getinput {
# Return %input array, associating input names with input values
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

        $input{$name} = $value;
	push(@datanames,$name);
    }
    %input;                     # returnerer den assosiative array'en
}



sub error {
# returns HTML error message and exits program
    local($msg) = $_[0];

    &header("Feilmelding");
    print <<EOT;

<font size="+1">Programmet ble avbrutt med følgende feilmelding:</font>
<blockquote>
<hr noshade>
<center>
<font size="+2">
$msg
</font>
<hr noshade>
</center>
</blockquote>
</body>
</html>
EOT
    exit 1;
}


sub header {
    local($txt) = @_;

    return if $headershown++;

    $sistebutikk = 'sn' unless length $sistebutikk;
    $attrib = $butikkinfo{$sistebutikk.'-attrib'};

    print <<EOT;
Content-type: text/html

<html>
<head>
<title>
$txt
</title>
</head>

<body $butikkinfo{$sistebutikk.'-attrib'}>

<a href="/"><img align="right" alt="[Schibsted Nett]" 
   border="0" src="/img/sn_horisont_liten-t.gif"></a>
EOT
    print qq!<a href="$butikkinfo{$sistebutikk.'-url'}">
	<img align="left" alt="[Intershop]"
	    src="$butikkinfo{$sistebutikk.'-logo'}" border="0"></a>!
		if length $butikkinfo{$sistebutikk.'-logo'};

    print qq!<br clear="all">\n<h1>$txt</h1>\n\n!;
}


sub vareinfo {
    local($butikk, $varenr) = @_;
    local(%info);
    $varenr =~ s/([;\"!&\'\`*?$~])/\\$1/g;

    open(VARE, "$butikkinfo{$butikk.'-vareinfo'} $varenr| ")
	|| &error("Finner ikke vareinfo");
    while (<VARE>) {
	next unless /:/;
	$info{lc $1} = $2 if /^([^\s:]+)\s*:\s*(.+)\s*$/;
    }
    close VARE;
    return %info;
}



sub velkommen {

    &header("Velkommen til Schibsted Netts handlesenter");
    print <<EOT;

Du har nå fått en elektronisk handlekurv i <a href="/">Schibsted
Netts</a> handlesenter. Denne kurven kan du ta med deg til de
forskjellige butikkene i Schibsted Netts virtuelle handlesenter.

<h2>Slik virker handlekurven</h2>

<ul>
    <li> Når du finner varer du vil ta med deg, kikker du på handlekurv-link\'en
ved varen og den blir lagt opp i handlekurven din. 

<li> Hvis du trykker på handlekurv-symbolet, får du opp en oversikt
     over hvilke varer du har lagt i handlekurven.

<li> På oversikts-siden ser du hvor mye du har handlet for tilsammen.
     Om du skulle ombestemme deg kan du ta varer ut av handlekurven og
     legge dem tilbake igjen.

<li> Fra oversiktssiden kan du også hente opp bestillingsskjema hvor
     du taster inn navn, adresse, e-post-adresse osv.

<li> Når du ønsker å bestille varer sender du inn det ferdig utfylte
     bestillingsskjemaet.

<li> Når du bestiller sendes det en e-mail til adressen din. Denne må
    du svare på for å bekrefte bestillingen. Det er viktig at du sender
    med subject-feltet tilbake, f.eks. ved å bruke en 'reply'-funksjon i
    mail-leseren din eller ved å kopiere subject-linjen til svaret du
    sender.

</ul>


<a href="$goto">Trykk her for å komme videre</a>

</body>
</html>


EOT


    exit 0;

}


sub getid {
    # is ID given explicitly?
    return $input{id} if length $input{id};

    # get input from HTTP-cookie
    return $1 if $ENV{HTTP_COOKIE} =~ /$cookiename=(\d+)/;

    # only one user registered from REMOTE_ADDR?
    # not implemented yet

    srand(time || $$);
    $id = int(rand(1e+8)) + 1;	# don't want id=0.
    $intercept = 1;

    return $id;
}


$id = getid;
if (open(SB, "$DATADIR/kurv-$id.sistebutikk")) {
    $sistebutikk = <SB>;
    close(SB);
}

1;				# returnerer 1 siden dette er en lib-fil


