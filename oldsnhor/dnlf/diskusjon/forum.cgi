#!/local/bin/perl5

# Program som implementerer lukkede diskusjonsgrupper under WWW. Det er mulig å
# ha flere diskusjonsgrupper. Programmet aksesseres med
#
#	/diskusjon/forum.cgi/<gruppe>		vis alle innlegg i en gruppe
#	/diskusjon/forum.cgi/<gruppe>/4711	vis ett innlegg i en gruppe
#	/diskusjon/forum.cgi/<gruppe>/new	hent skjema for å sende nytt innlegg
#	/diskusjon/forum.cgi/<gruppe>/reply	hent skjema for å sende oppfølgerinnlegg
#	/diskusjon/forum.cgi/<gruppe>/cancel	trekk tilbake tidligere innsendt innlegg
#
# Kaare Gunnar Nesheim, <kgn@oslonett.no>
# 16. oktober 1995, sist endret 17. oktober 1995

$TOPP		= "/local/www/dnlf/diskusjon";
$DISKUSJONDIR	= $TOPP;
$TELLERFIL	= "$DISKUSJONDIR/teller.txt";
$MININDENT	= "      ";
@PWCHAR		= ("a" .. "z", "A".."Z", "0".."9", "_");
@MND		= ("januar", "februar", "mars", "april", "mai", "juni", "juli",
                   "august", "september", "oktober", "november", "desember");

#$|=1;
%input = &getinput;

$gruppe = $1 if $ENV{'PATH_INFO'} =~ s%/([^/]+)/?%%;
$arg = $ENV{'PATH_INFO'};

&error("Ingen diskusjonsgruppe angitt") unless length $gruppe;
chdir "$DISKUSJONDIR/$gruppe"
       || &error("Den angitte gruppen \"$gruppe\" er ikke opprettet");

&form if $arg eq "new";
&reply if $arg eq "reply";
&submit if $arg eq "submit";
&cancel if $arg eq "cancel";
&showarticle if length $ENV{'PATH_INFO'};

# otherwise: show list of all articles...
# to be implemented: truncation of list, possibly archive/archive-adm

&header("Diskusjonsforum");

# print qq!<center>!;
# print qq!<h4><em>Alle innlegg står for innsenderens regning</em></h4>!;
# print qq!</center>!;

print &liste($ENV{'PATH_INFO'});

print <<EOT;

<p>
Vil du sende inn et <a href="$ENV{'SCRIPT_NAME'}/$gruppe/new">innlegg
med ny tittel</a> kan du gjøre det herfra, om du vil sende inn
oppfølger til et innlegg må du først hente det aktuelle innlegget.
EOT

&footer;

exit 0;



sub form {
    &header("Send inn et nytt innlegg");
    $host = "\@$ENV{'REMOTE_HOST'}";
    while (<DATA>) {	# leser skjema fra slutten av kildekoden
	s/<!--\s*XXREF\s*-->/<input type="hidden" name="ref" value="$input{'ref'}">/
	    if length $input{'ref'};
	s/XXADDR/$host/;
	s/XXGRUPPE/$gruppe/;
	s/XXTITLE/$ref{'title'}/;
	s/XXBODY/$quote/;
	s/XXSCRIPT/$ENV{'SCRIPT_NAME'}/;
	print;
    }
    &footer;
    exit 0;
}


sub reply {
    # Trenger title, date & body fra innlegg som det refereres til
    if (open(REF, $input{'ref'})) {
	while (<REF>) {
	    chop;
	    ($key, $val) = split(/:/, $_, 2);
	    $key =~ s/\s+$//;
	    $val =~ s/^\s+//;
	    $ref{$key} = $val;
	}
	close REF;
	# Tittel skal begynne med én forekomst av "Re: ".
	$ref{'title'} =~ s/^(Re: )*/Re: /;
	$quote = "$ref{'from'} skriver ($ref{'date'}):\n\n> $ref{'body'}\n"
	    if (length($input{'quote'}) && $input{'quote'} !~ /^(nei|no)/i);
	$quote =~ s/(<br>)/\n> /g;
    }
    &form;
}




sub submit {
    &error("Feltene navn, e-post-adresse, overskrift og innlegg må fylles ut!")
	unless (length $input{'name'} && length $input{'epost'}
		&& length $input{'title'} && length $input{'body'});
    $count = &uniquecount;	# hent nytt id-nr. - garantert unikt
    $filename = sprintf("art%05d.txt", $count);
    open(FILE, ">$filename")
	|| &error("Kunne ikke skrive ny fil 'art$count.txt'.");
    $input{'from'} = "$input{'name'} ($input{'epost'})";
    delete($input{'name'});
    delete($input{'epost'});

    $passwd = $input{'passwd'} || &rndpasswd; # velg tilfeldig passord hvis ikke angitt
    $input{'passwd'} = crypt($passwd, &rndpasswd);
    $input{'date'} = &dato;
    $input{'host'} = "$ENV{'REMOTE_HOST'}/$ENV{'REMOTE_ADDR'}";
    &escape(@input{'title', 'body', 'from'});
    foreach (keys %input) {	# skriv alle felter til fil
	print FILE "$_: $input{$_}\n";
    }
    close FILE;

    &header("Ny artikkel registrert"); # HTML-kvittering til innsenderen
    print <<EOT;

Takk for det innsendte innlegget, det er nå lagret med URL\'en <a
href="$ENV{'SCRIPT_NAME'}/$gruppe/$filename">http://$ENV{'SERVER_NAME'}/$ENV{'SCRIPT_NAME'}/$gruppe/$filename</a>.
Dersom du senere ønsker å slette det, må du oppgi passordet
"<em>$passwd</em>" og nummeret på innlegget ditt: <em>$count</em>.<p>

For å trekke tilbake et innsendt innlegg, bruker du følgende URL:
<blockquote>
<h3><a href="$ENV{'SCRIPT_NAME'}/$gruppe/cancel">http://$ENV{'SERVER_NAME'}$ENV{'SCRIPT_NAME'}/$gruppe/cancel</a></h3>
</blockquote>

Gå tilbake til <a
href="$ENV{'SCRIPT_NAME'}/$gruppe">diskusjonsgruppen</a>
EOT

    &footer;

    exit 0;
}


sub cancel {

    if (! length $input{'id'}) {
	# no article id given, respond with fill-in form
	&header("Slette artikkel fra diskusjonsgruppe");
	print <<EOT;

For å slette en artikkel må du oppgi identifikasjonsnummeret (dette
finner du i URL\'en til innlegget du vil slette om du ikke har notert
deg det - se <a href="$ENV{'SCRIPT_NAME'}/$gruppe">listen</a> over
innleggene i gruppen). Videre må du oppgi passordet du valgte eller
fikk trukket da du sendte inn innlegget. Trykk deretter på
slette-knappen.

<form method="POST" action="$ENV{'SCRIPT_NAME'}/$gruppe/cancel">

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
	&header("har slettet innlegg fra \"$gruppe\"");
	$filename = sprintf("$DISKUSJONDIR/$gruppe/art%05d.txt", $input{'id'});

	# don't unlink. let operator restore if article was deleted by mistake
	rename($filename, "$filename.deleted");	

	print <<EOT;

Innlegg nr. $input{'id'} er nå slettet fra diskusjonsgruppen.<p>

Gå tilbake til <a href="$ENV{'SCRIPT_NAME'}/$gruppe">diskusjonsgruppen</a>
EOT
	&footer;
	exit 0;
    }
}



sub showarticle {
    &header("Diskusjonsforum");
    print qq!<center>!;
    print qq!<h4><em>Alle innlegg står for innsenderens regning</em></h4>!;
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

<hr noshade size="1"><p>

<em>Send oppfølger til dette innlegget <a
href="$ENV{'SCRIPT_NAME'}/$gruppe/reply?ref=$arg&amp;quote=yes">med</a>
eller <a href="$ENV{'SCRIPT_NAME'}/$gruppe/reply?ref=$arg">uten</a>
sitat av dette innlegget. Dersom du siterer fra det opprinnelige
innlegget er det en fordel om du redigerer bort eventuelle unødvendige
deler av innlegget du svarer på.</em>

EOT
    print qq!<p><hr size="1" noshade>Foregående og/eller etterfølgende artikler:\n!;
    &liste($arg, 2, 4);
    print "<em>Gå tilbake til diskusjonsgruppen for å se ";
    print qq!<a href="$ENV{'SCRIPT_NAME'}/$gruppe">alle innleggene</a></em>\n!;
    print qq!<hr noshade size="1">\n!;

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
        $_[$i] =~ s/\&/&amp;/g;	# Oversett '&' til "&amp;"...
        $_[$i] =~ s/\&amp;(\w{1,6}|\#\d{1,3});/&$1;/g; # ...men ikke hvis del av entity
        $_[$i] =~ s/æ/&aelig;/g; # HTML'ifiser særnorske tegn
        $_[$i] =~ s/ø/&oslash;/g;
        $_[$i] =~ s/å/&aring;/g;
        $_[$i] =~ s/Æ/&AElig;/g;
        $_[$i] =~ s/Ø/&Oslash;/g;
        $_[$i] =~ s/Å/&Aring;/g;
        # This is a good place to make sure no 
	# user can exploit server side includes!
        $_[$i] =~ s/<\!/<!-- COMMENT: /g;
    }

}



sub dato {
    local(@t);
    @t = localtime(time);
    return sprintf("%d. %s %d %02d:%02d:%02d",
		   $t[3], $MND[$t[4]], @t[5,2,1,0]);
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
	$on = "<strong>";	# don't make link to article being shown
	$off = "</strong>";
	$index = $#text;	# store index of current article
    } else {
	$on = qq!<a href="$ENV{'SCRIPT_NAME'}/$gruppe/$o">!;
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

    opendir(DIR, ".") || &error("Får ikke tilgang til filområdet $gruppe ");
    @file = sort grep(/^art\d+.txt$/, readdir(DIR));
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
	if (defined $input{ref}) {
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
	$info = "Tilsammen $count innlegg i listen ovenfor\n";
    } else {
	$info = qq!<blockquote><hr noshade size="2"><font size="+1"><b>\n!;
	$info .= qq!Dessverre ingen leserbrev tilgjengelige ennå.\n!;
	$info .= qq!</b></font><hr noshade size="2"></blockquote>! ;
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

	$value =~ s/\n/<br>/g;
        $input{$name} =  $value; # assosier verdi med feltnavn...
    }
    return %input;
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
bevares. Flere forekomster av blanke tegn oversettes til ett blankt
tegn. Hvis du ønsker å bruke blanke tegn for å oppnå spesiell
formattering av innlegget må du bruke &lt;pre&gt; før og &lt;/pre&gt;
etter området med spesiell formattering.

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
