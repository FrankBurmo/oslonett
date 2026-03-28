#!/local/bin/perl5

print "Content-type: text/html\n\n";

require "fd-lib.pl";

&getinput;

$input{base} = "fd95" unless length $input{base};

$input{base} =~ s/\W//g;
&error("Ingen tilbakemeldingsdatabase angitt (feil i HTML FORM eller "
       ."-dokument)") unless length $input{base};

opendir(DIR, $intdir) || &error("Kunne ikke lese directory $intdir");
@file = sort grep(/^$input{base}reg\d+.txt$/, readdir(DIR));
closedir(DIR);

if (! scalar(@file)) {
    print &header("Ingen registreringer i databasen '$input{'base'}'");
    print <<EOT;

Det er foreløpig ikke lagt ut noen svar på spørsmål eller kommentarer
til tilbakemeldinger. Den oppgite databasen '$input{'base'}' er ikke opprettet ennå.
EOT
    print &footer;
    exit 0;
}

print &header("Spørsmål og kommentarer");
print <<EOT;

Nedenfor følger en datosortert liste over spørsmål som er besvart
eller tilbakemeldinger som er kommentert. Ved å klikke på titlene
kommer man frem til et skjema for å besvare og evt. redigere
innkommende meldinger.

<pre>
EOT

printf "<b>%-9s %-50s %-10s %s</b>\n", "Dato", "Tittel", " Status", "Avsender";
foreach $filename (reverse @file) {
    undef %attrib;
    open(FILE, "$intdir/$filename")
	|| &error("Kunne ikke åpne filen $intdir/$filename");
    while (<FILE>) {
	chop;
	($name, $value) = split(": ", $_, 2);
	$name =~ tr/A-ZÆØÅ/a-zæøå/;
	$attrib{$name} = $value;
    }

    next if ($input{'subset'} =~ /^nye$/i && length $attrib{revdato});
    next if ($input{'subset'} =~ /^gamle$/i && ! length $attrib{revdato});

    $count++;
    $dato = $1 if $attrib{regdato} =~ /(\S+)/;
    $status = "  Sett";
    $status = " Besvart" if length $attrib{'besvart'};
    $status = qq!<a href="/forskdag95/respons/ut.cgi?file=$intdir/$filename">Publisert</a>!
	if $attrib{'publiseres'} =~ /^ja/i;
    $status = "   Ny" unless length $attrib{'revdato'};
    printf(qq{%-9s <a href="$redutscript?file=$intdir/$filename">%-54s %-10s %s\n},
	   $dato, $attrib{overskrift}."</a>", $status, ( $attrib{anonym} =~ /^ja$/i ) ? 
	   "[anonym]" : $attrib{navn});
    close(FILE);
}

print "</pre>\n";
if (!$count) {
    $msg = "Dessverre ingen kommentarer eller svar tilgjengelig ennå.";
    $msg = "Ingen nye spørsmål eller kommentarer innsendt."
	if $input{'subset'} =~ /^nye$/;
    $msg = "Ingen allerede besvarte spørsmål eller kommentarer registrert."
	if $input{'subset'} =~ /^gamle$/;
    print <<EOT;
<blockquote>
<hr noshade size="2">
<b>$msg</b>
<hr noshade size="2">
</blockquote>
EOT
    } else {
	print "Tilsammen $count oppføringer i listen ovenfor\n";
    }
print &footer;
exit 0;
