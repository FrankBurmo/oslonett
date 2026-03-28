#!/local/bin/perl5

# Program for diskusjonsgrupper i NTINs web-sider. Programmet brukes for
# å hente ut og å sende inn innlegg i vilkårlig gruppe. Aktuell gruppe
# velges fra environment-variablen PATH_INFO. Ved innsending av nytt
# oppslag leses CGI-input som er sendt med med metode POST eller GET.
#
# Kaare Gunnar Nesheim, <kgn@oslonett.no>
# 23. november 1995

require "diskusjon-adm/lib.pl";

$|=1;
%input = &getinput;
$originput{'body'} = $input{'body'};

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
<h2><a href="$ENV{'SCRIPT_NAME'}/$gruppeurl/cancel">http://$ENV{'SERVER_NAME'}$ENV{'SCRIPT_NAME'}/$gruppeurl/cancel</a></h2>
</blockquote>

Gå tilbake til diskusjonsgruppen <a
href="$ENV{'SCRIPT_NAME'}/$gruppeurl">$gruppe</a>
EOT

    &footer;

    exit 0 unless length $NOTIFYRCPT;	# exit here if no notification address.

    # "\n.\n" in $input{'body'} would terminate mail msg. Don't let it happen
    $input{'body'} =~ s/\n.\n/\n. \n/g;
    open(MAIL, "| /usr/lib/sendmail -t")
	|| exit 0;
    print MAIL "To: $NOTIFYRCPT\n";
    print MAIL "Subject: INFO: Nytt innlegg (#$count) i gruppen $gruppe\n";
    print MAIL "\n";		# separate headers from body

    print MAIL "\nMelding om nytt innlegg i diskusjonsgruppe:\n\n";
    print MAIL "     Gruppe: $gruppe\n";
    print MAIL "Innlegg nr.: $count\n";
    print MAIL "   Avsender: $input{'from'}\n";
    print MAIL "  Sendt fra: $input{'host'}\n";
    print MAIL " Overskrift: $input{'title'}\n";
    print MAIL "        URL: http://$ENV{'SERVER_NAME'}$ENV{'SCRIPT_NAME'}/$gruppeurl/$filename\n";
    print MAIL "\nSelve meldingen:\n\n";
    print MAIL "$originput{'body'}\n\n";

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

<hr noshade size="1"><p>

<em>Send oppfølger til dette innlegget <a
href="$ENV{'SCRIPT_NAME'}/$gruppeurl/reply?ref=$arg&amp;quote=yes">med</a>
eller <a href="$ENV{'SCRIPT_NAME'}/$gruppeurl/reply?ref=$arg">uten</a>
sitat av dette innlegget. Dersom du siterer fra det opprinnelige
innlegget er det en fordel om du redigerer bort eventuelle unødvendige
deler av innlegget du svarer på.</em>

EOT
    print qq!<p><hr size="1" noshade>Foregående og/eller etterfølgende artikler:\n!;
    &liste($arg, 2, 4);
    print "<em>Gå tilbake til diskusjonsgruppen for å se ";
    print qq!<a href="$ENV{'SCRIPT_NAME'}/$gruppeurl">alle innleggene</a></em>\n!;
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
teksten.

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
