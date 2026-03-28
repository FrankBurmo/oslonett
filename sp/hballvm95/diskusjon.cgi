#!/local/bin/perl5

# Generelt program for diskusjonsgrupper i web. Programmet brukes for
# å hente ut, sende inn og kansellere innlegg i vilkårlig gruppe. Aktuell 
# gruppe velges fra environment-variablen PATH_INFO. Ved innsending av
# nytt innlegg leses CGI-input som er sendt med med metode POST eller GET.
#
# Kaare Gunnar Nesheim, <kgn@a.sn.no>
# 8. oktober 1995, sist endret 11. desember 1995

# Konfigurering gjøres kun i de neste 7 linjene samt i subrutinene
# 'header' og 'footer'

$TOPPDIR	= "/local/www/sp/hballvm95";	# top directory
$TOPP		= "/hballvm95";		# top URL
$DISKUSJONDIR	= "$TOPPDIR/diskusjon-adm";	# subdirectory under top.
$TELLERFIL	= "$DISKUSJONDIR/teller.txt";	# which counter file to use
$MININDENT	= "      ";		# indentation for new level in thread
# recipients of new message notifications
$NOTIFYRCPT	= 'kgn@a.sn.no,steinar@a.sn.no';


@PWCHAR		= ("a" .. "z", "A".."Z", "0".."9", "_");
@MND		= ("januar", "februar", "mars", "april", "mai", "juni", "juli",
                   "august", "september", "oktober", "november", "desember");

$|=1;
%input = &getinput;

$gruppe = $1 if $ENV{'PATH_INFO'} =~ s%/([^/]+)/?%%;
$gruppeurl = &urlescape($gruppe); # some chars are illegal in URLs, escape these: %,/,SPC,?,&
$arg = $ENV{'PATH_INFO'};

&error("Du har ikke angitt noen diskusjons-gruppe") unless length $gruppe;
chdir "$DISKUSJONDIR/$gruppe"
       || &error("Diskusjonsgruppen \"$gruppe\" finnes ikke");

&form if $arg eq "new";
&reply if $arg eq "reply";
&submit if $arg eq "submit";
&cancel if $arg eq "cancel";
&showarticle if length $ENV{'PATH_INFO'};

# otherwise: show list of all articles...
# to be implemented: truncation of list, possibly archive/archive-adm
&header("$gruppe");
print qq!<center>!;
print qq!<h4><em>Innsender er ansvarlig for innholdet i innleggene</em></h4>!;
print qq!</center>!;

print &liste($ENV{'PATH_INFO'});

print <<EOT;

<p>

Hvis du vil starte en diskusjon med <a
href="$ENV{'SCRIPT_NAME'}/$gruppeurl/new">ny tittel</a> kan du gjøre
det herfra. Hvis du vil svare på innlegg i en pågående diskusjon, må
du først hente det aktuelle innlegget. Du kan også <a
href="$ENV{'SCRIPT_NAME'}/$gruppeurl/cancel">trekke tilbake et
innlegg</a> du selv har skrevet.

EOT

&footer;

exit 0;



sub form {
    &header(qq!Nytt innlegg i diskusjonsgruppen "$gruppe"!);
    $host = "\@$ENV{'REMOTE_HOST'}";
    while (<DATA>) {
	s/<!--\s*XXREF\s*-->/<input type="hidden" name="ref" value="$input{'ref'}">/
	    if length $input{'ref'};
	s/XXADDR/$host/;
	s/XXGRUPPE/$gruppeurl/;
	s/XXSCRIPT/$ENV{'SCRIPT_NAME'}/,
	s/XXTITLE/$ref{'title'}/;
	s/XXBODY/$quote/;
	print;
    }
    &footer;
    exit 0;
}


sub reply {
    if (open(REF, $input{'ref'})) {
	while (<REF>) {
	    chop;
	    ($key, $val) = split(/:/, $_, 2);
	    $key =~ s/\s+$//;
	    $val =~ s/^\s+//;
	    $val =~ s/"/&quot;/g;
	    $ref{$key} = $val;
	}
	close REF;
	$ref{'title'} =~ s/^(Re: )*/Re: /;
	$quote = "$ref{'from'} skriver ($ref{'date'}):\n\n> $ref{'body'}\n"
	    if (length($input{'quote'}) && $input{'quote'} !~ /^(nei|no)/i);
	$quote =~ s/(<br>)/\n> /g;
    }
    &form;
}





sub submit {
    &error("Du må fylle ut feltene navn, e-post-adresse, overskrift og innlegg!")
	unless (length $input{'name'} && length $input{'epost'}
		&& length $input{'title'} && length $input{'body'});
    $count = &uniquecount;
    $filename = sprintf("art%05d.txt", $count);
    open(FILE, ">$filename")
	|| &error("Kunne ikke skrive ny fil 'art$count.txt'.");
    $input{'from'} = "$input{'name'} ($input{'epost'})";
    delete($input{'name'});
    delete($input{'epost'});

    $passwd = $input{'passwd'} || &rndpasswd;
    $input{'passwd'} = crypt($passwd, &rndpasswd);
    $input{'date'} = &dato;
    $input{'host'} = "$ENV{'REMOTE_HOST'}/$ENV{'REMOTE_ADDR'}";
    &escape(@input{'title', 'body', 'from'});
    foreach (keys %input) {
	print FILE "$_: $input{$_}\n";
    }
    close FILE;

    &header("Ny artikkel mottatt");
    print <<EOT;

Takk for den innsendte artikkelen, den er nå lagret med URL\'en <a
href="$ENV{'SCRIPT_NAME'}/$gruppeurl/$filename">$ENV{'SCRIPT_NAME'}/$gruppeurl/$filename</a>.
Hvis du senere ønsker å slette artikkelen, må du oppgi passordet
"<em>$passwd</em>" og nummeret på artikkelen din: <em>$count</em>.<p>

For å trekke tilbake en innsendt artikkel, bruker du følgende URL:
<blockquote>
<h3><a href="$ENV{'SCRIPT_NAME'}/$gruppeurl/cancel">http://$ENV{'SERVER_NAME'}$ENV{'SCRIPT_NAME'}/$gruppeurl/cancel</a></h3>
</blockquote>

Gå tilbake til diskusjonsgruppen <a
href="$ENV{'SCRIPT_NAME'}/$gruppeurl">$gruppe</a>
EOT

    &footer;

    exit 0 unless length $NOTIFYRCPT;	# exit here if no notification address

    # "\n.\n" in $input{'body'} would terminate mail msg. Don't let it happen
    $input{'body'} =~ s/\n.\n/\n. \n/g;
    open(MAIL, "| /usr/lib/sendmail -t")
	|| exit 0;
    print MAIL "To: $NOTIFYRCPT\n";
    print MAIL "Subject: INFO: Nytt innlegg (#$count) i gruppen $gruppe\n";
    print MAIL "\n";		# separate headers from body

    print MAIL "\nMelding om nytt innlegg i diskusjonsgruppe:\n\n";
    print MAIL "        Nr.: $count\n";
    print MAIL "     Gruppe: $gruppe\n";
    print MAIL "   Avsender: $originput{'name'}\n";
    print MAIL "  Sendt fra: $ENV{'REMOTE_HOST'} ($ENV{'REMOTE_ADDR'})\n";
    print MAIL " Overskrift: $originput{'title'}\n";
    print MAIL "Innlegg-URL: http://$ENV{'SERVER_NAME'}$ENV{'SCRIPT_NAME'}/$gruppeurl/$filename\n";
    print MAIL "\nSelve meldingen:\n";
    print MAIL "------------------------------------------------------------\n";
    print MAIL "$originput{'body'}\n";
    print MAIL "------------------------------------------------------------\n";
    print MAIL "Denne meldingen er automatisk generert av $0\n";
    print MAIL "\n.\n";
    close MAIL;
    exit 0;
}


sub cancel {

    if (! length $input{'id'}) {
	# no article id given, respond with fill-in form
	&header("Slette artikkel fra \"$gruppe\"");
	print <<EOT;

For å slette en artikkel må du oppgi identifikasjonsnummeret (dette
finner du i URL\'en til innlegget du vil slette om du ikke har notert
deg det - se <a href="$ENV{'SCRIPT_NAME'}/$gruppeurl">listen</a> over
innleggene i gruppen). Videre må du oppgi passordet du valgte eller
fikk trukket da du sendte inn innlegget. Trykk deretter på
slette-knappen.

<form method="POST" action="$ENV{'SCRIPT_NAME'}/$gruppeurl/cancel">

<table border="0" cellpadding="2">
<tr>
<td><font size="+2">Artikkel-id:</font></td>
<td> <input name="id" size="10"><br></td>

<tr>
<td><font size="+2">Passord:</font></td>
<td><input type="password" name="passwd" size="20"><br></td>

<tr>
<td></td>
<td><input type="submit" value=" Slett innlegg "></td>
</tr>
</table>
</form>
EOT
&footer;
exit 0;
    } else {
	open(FILE, sprintf("$DISKUSJONDIR/$gruppe/art%05d.txt", $input{'id'}))
	    || &error("Finner ikke noe innlegg med id-nummer $input{'id'}.");
	while (<FILE>) {
	    next unless /^passwd:\s*(\S+)/;
	    $pwc = $1;
	    last;
	}

	&error("Du har oppgitt galt passord. Innlegget er ikke slettet")
	    unless crypt($input{'passwd'},$pwc) eq $pwc;
	&header("Har slettet innlegg fra \"$gruppe\"");
	$filename = sprintf("$DISKUSJONDIR/$gruppe/art%05d.txt", $input{'id'});

	# don't unlink. let operator restore if article was deleted by mistake
	rename($filename, "$filename.deleted");	

	print <<EOT;

Innlegg nr. $input{'id'} er nå slettet fra diskusjonsgruppen.<p>

Nedenfor følger artiklene i gruppen:<p>
EOT
        &liste;
	&footer;
	exit 0;
    }
}



sub showarticle {
    &header("$gruppe");
    print qq!<center>!;
    print qq!<h4><em>Innsender er ansvarlig for innholdet i innleggene</em></h4>!;
    print qq!</center>!;

    open(FILE, $arg)
	|| &error("Kan ikke lese filen $DISKUSJONDIR/$gruppe/$arg");
    while (<FILE>) {
	($key, $val) = split(/:/, $_, 2);
	$art{$key} = $val;
    }

    print <<EOT;
<h2>$art{'title'}</h2>
Innsender: <b>$art{'from'}</b><br>
Dato: <b>$art{'date'}</b><p>
$art{'body'}

<hr size="1"><p>

<em>Send oppfølger til dette innlegget <a
href="$ENV{'SCRIPT_NAME'}/$gruppeurl/reply?ref=$arg&amp;quote=yes">med</a>
eller <a href="$ENV{'SCRIPT_NAME'}/$gruppeurl/reply?ref=$arg">uten</a>
sitat av dette innlegget. Dersom du siterer fra det opprinnelige
innlegget er det en fordel om du redigerer bort eventuelle unødvendige
deler av innlegget du svarer på.</em>

EOT
    print qq!<p><hr size="1">Foregående og/eller etterfølgende artikler:\n!;
    &liste($arg, 2, 4);
    print "<em>Gå tilbake til diskusjonsgruppen for å se ";
    print qq!<a href="$ENV{'SCRIPT_NAME'}/$gruppeurl">alle innleggene</a></em>\n!;
    print qq!<hr size="1">\n!;

    &footer;

    exit 0;
}




sub uniquecount {
    local(%COUNT, $count);
    open(COUNT, "+<$TELLERFIL") || open(COUNT, "+>$TELLERFIL")
	|| &error("Kunne ikke åpne tellerfilen $COUNTERFILE");
    $count = <COUNT>;
    $count++;
    seek(COUNT, 0, 0);
    print COUNT "$count\n";
    close COUNT;
    return $count;
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


sub urlescape {
    local($url) = $_[0];
    # some chars are illegal in URLs. Code these as %<hexcode>

    $url =~ s!(["% &?/])!sprintf("%%%02X",unpack("c",$1))!ge;
    return $url;
}



sub dato {
    local(@t);
    @t = localtime(time);
    return sprintf("%d. %s %d %02d:%02d:%02d",
		   $t[3], $MND[$t[4]], $t[5], @t[2,1,0]);
}


sub rndpasswd {
    local($pw);
    # make up a random passwd consiting of 7 random characters

    srand time || $$;
    foreach (0..6) {
	$pw .= $PWCHAR[int rand($#PWCHAR)];
    }
    return $pw;
}


sub item {
    # recursively print one article-line (for DL-list) and its children
    local ($o) = $_[0];
    local ($child, $on, $off);
    if ($o eq $arg) { 
	$on = "<strong>";
	$off = "</strong>";
	$index = $#text;
    } else {
	$on = qq!<a href="$ENV{'SCRIPT_NAME'}/$gruppeurl/$o">!;
	$off = "</a>";
    }
    push(@text, $indent . qq! $on$title{$o}$off, $name{$o}\n!);
    if (defined $children{$o}) {
	$indentlevel++;
	$indent = $MININDENT x $indentlevel;
	foreach $child (split(/,/, $children{$o})) {
	    &item($child);
	}
	$indentlevel--;
	$indent = $MININDENT x $indentlevel;
    }
}


sub liste {
    local($id, $sub, $add) = @_;
# pass 0 read directory

    opendir(DIR, ".") || &error("Kan ikke åpne directory for gruppen $gruppe");
    @file = sort grep(/^art\d+\.txt$/, readdir(DIR));
    closedir(DIR);

# pass 1 read file, build @children lists for all articles
    foreach $filename (@file) {
	undef %input;
	open(FILE, $filename) || next;
	while (<FILE>) {
	    chop;
	    ($name, $value) = split(": ", $_, 2);
	    $name =~ tr/A-ZÆØÅ/a-zæøå/;
	    $input{$name} = $value;
	}
	$count++;
	$dato = $1 if $input{regdato} =~ /(\S+)/;
	$input{'title'} =~ s/<.+?>//g;
	$title{$filename} = $input{'title'};
	$date{$filename} = $input{'date'};
	$name{$filename} = $input{'from'};
	if (length $input{ref}) {
	    $input{'ref'} =~ s%.+/%%;
	    $children{$input{'ref'}} .= "," 
		if defined( $children{$input{ref}});
	    $children{$input{'ref'}} .= $filename;
	    $ref{$filename} = $input{'ref'};
	}
	close(FILE);
    }


# pass 2 traverse article titles, build array of orphans sorted by date

    foreach $filename (keys %title) {
	next if length $ref{$filename} && -r $ref{$filename};
	push(@orphans, $filename);
    }

# pass 3 traverse @orphans, print reference tree

    foreach (sort @orphans) {
	&item($_);
    }

    if ( $count ) {
	$endelse = ($count == 1) ? "kel" : "ler";
	$info = "Tilsammen $count artik$endelse i listen ovenfor\n";
    } else {
	$info = qq!<blockquote><hr size="2"><font size="+1"><b>\n!;
	$info .= qq!Dessverre ingen leserbrev tilgjengelige ennå.\n!;
	$info .= qq!</b></font><hr size="2"></blockquote>! ;
    }
    print "<pre></tt>";
    $lo = $index-$sub;
    $lo = $[ if $lo < $[ || ! $sub;
    $hi = $index+$add;
    $hi = $#text if $hi > $#text || ! $add;
    print @text[$lo .. $hi];
    print "</pre>\n";
    return $info;
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

	$originput{$name} = $value;
	$value =~ s/\n/<br>/g;
	$value =~ s/\r//g;
        $input{$name} =  $value; # assosier verdi med feltnavn...
    }
    return %input;
}


sub error {
    local($msg) = $_[0];

    &header("Feilmelding");

    print "Programmet ble avbrutt med følgende feilmelding:\n\n<blockquote>\n";
    print qq!<hr size="2">\n<font size="+1"><b>$msg</b></font>\n!;
    print qq!<hr size="2">\n</blockquote>\n!;
    &footer;
    exit 0;
}


sub header {
# returnerer standard header for HTML-dokumentene. Tilpasses aktuell bruker
    local($txt) = $_[0];

    return if $HEADER++;
    print <<EOT;
Content-type: text/html

<html>
<head>
<title>$txt</title>
</head>
<body background="/sp/hballvm95/img/vmlogo-bg.jpg">

<a href="/sp/hballvm95/">
<img alt="[Hjem]" src="/sp/hballvm95/img/vmikon.gif"
     border="0" align="right"></a>
<h1>$txt</h1>

EOT
}


sub footer {
# returnerer standard footer for HTML-dokumentene. Tilpasses aktuell bruker
    print <<EOT;

<p>
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
}



# Finally, include HTML form to use when submitting new articles

__END__

Fyll inn feltene nedenfor og trykk på "Send"-knappen. 


<form method="POST" action="XXSCRIPT/XXGRUPPE/submit">
<!-- XXREF -->
<table border="0" cellpadding="2">

<tr>
<td><font size="+2">Navn:</font></td>
<td><input name="name" size="45"><br></td>

<tr>
<td><font size="+2">Epost-adresse:</font></td>
<td><input name="epost" size="45" value="XXADDR"><br></td>

<tr>
<td><font size="+2">Overskrift:</font></td>
<td><input name="title" size="45" value="XXTITLE"><br></td>

<tr>
<td colspan="2">

Selve innlegget skriver du nedenfor. Alle linjeskift du skriver
bevares men formattering i form av blanke tegn forsvinner med mindre
du angir HTML-kode for preformattering omkring den ferdig formatterte
teksten.<br>

<textarea name="body" cols="70" rows="15">XXBODY</textarea>
</td>

<tr>
<td colspan="2">

Det er mulig å kansellere en innsendt artikkel. For å gjøre dette må
du oppgi et passord. Hver artikkel har et eget passord for å
kansellere (men du kan gjerne velge et passord du har brukt
tidligere). Hvis du ikke fyller inn noe passord nedenfor, velges det i
stedet et passord med 7 tilfeldige tegn.<br>

</td>
<tr>
<td><font size="+2">Passord:</font></td>
<td><input type="password" name="passwd" size="15"></td>
<tr>
<td><input type="submit" value=" Send "></td>
<td><input type="reset" value=" Blankt skjema "></td>
</td>
<tr>
</table>


</form>
