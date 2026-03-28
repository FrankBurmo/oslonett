#!/local/bin/perl5

print "Content-type: text/html\n\n";

require "lib.pl";

&getinput;


opendir(DIR, $intdir) || &error("Kunne ikke lese directory $intdir");
@file = sort grep(/^brev\d+.txt$/, readdir(DIR));
closedir(DIR);

if (! scalar(@file)) {
    print &header("Ingen leserbrev har kommet inn ennå'");
    print <<EOT;

Det er foreløpig ikke lagt inn noen leserbrev.
EOT
    print &footer;
    exit 0;
}

print &header("Leserbrev");
print <<EOT;

Nedenfor følger en datosortert liste over innsendte leserbrev. Ved å
klikke på titlene kommer man frem til et skjema for å besvare og evt.
redigere innkommende brev.

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
    $status = qq!<a href="$utscript?file=$intdir/$filename">Publisert</a>!
	if $attrib{'publiseres'} =~ /^ja/i;
    $status = "   Ny" unless length $attrib{'revdato'};
    printf(qq{%-9s <a href="$redutscript?file=$intdir/$filename">%-54s %-9s %s\n},
	   $dato, $attrib{overskrift}."</a>", $status, $attrib{navn});
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
