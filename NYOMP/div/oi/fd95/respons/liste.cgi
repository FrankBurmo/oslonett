#!/local/bin/perl5

print "Content-type: text/html\n\n";

require "intern/fd-lib.pl";

&getinput;

$input{base} = "fd95" unless length $input{base};

$input{base} =~ s/\W//g;
&error("Ingen tilbakemeldingsdatabase angitt (feil i HTML FORM eller "
       ."-dokument)") unless length $input{base};

opendir(DIR, $intdir) || &error("Kunne ikke lese directory $intdir");
@file = sort grep(/^$input{base}reg\d+.txt$/, readdir(DIR));
closedir(DIR);

if (! scalar(@file)) {
    print &header("Ingen kommentarer tilgjengelig");
    print <<EOT;

Det er foreløpig ikke lagt ut noen svar på spørsmål eller kommentarer
til tilbakemeldinger.
EOT
    print &footer;
    exit 0;
}

print &header("Spørsmål og kommentarer");
print <<EOT;

Nedenfor følger en datosortert liste over spørsmål som er besvart
eller tilbakemeldinger som er kommentert. De tre feltene er 1) dato
for innsending av spørsmål/tilbakemelding, 2) tittel og 3) Navn på
innsender

<pre>
EOT

foreach $filename (reverse @file) {
    undef %input;
    open(FILE, "$intdir/$filename")
	|| &error("Kunne ikke åpne filen $intdir/$filename");
    while (<FILE>) {
	chop;
	($name, $value) = split(": ", $_, 2);
	$name =~ tr/A-ZÆØÅ/a-zæøå/;
	$input{$name} = $value;
    }
    next unless $input{publiseres} =~ /^ja/i;
    $count++;
    $dato = $1 if $input{regdato} =~ /(\S+)/;
    printf(qq{%-9s<a href="$utscript?file=$intdir/$filename">%-60s %s\n},
	   $dato, $input{overskrift}."</a>", ( $input{anonym} =~ /^ja$/i ) ? 
	   "[anonym]" : $input{navn});
    close(FILE);
}

print "</pre>\n";
if (!$count) {
    print <<EOT;
<hr noshade size="2">
<blockquote>
Dessverre ingen kommentarer eller svar tilgjengelig ennå.
</blockquote>
<hr noshade size="2">
EOT
    } else {
	print "Tilsammen $count oppføring(er) i listen ovenfor\n";
    }
print &footer;
exit 0;
