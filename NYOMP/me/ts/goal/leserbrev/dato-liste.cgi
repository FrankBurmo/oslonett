#!/local/bin/perl5

print "Content-type: text/html\n\n";

require "intern/lib.pl";
$utscript = "$topurl/ut.cgi";

&getinput;

opendir(DIR, $intdir) || &error("Kunne ikke lese directory $intdir");
@file = sort grep(/^brev\d+.txt$/, readdir(DIR));
closedir(DIR);

if (! scalar(@file)) {
    print &header("Ingen leserbrev tilgjengelig");
    print <<EOT;

Det er foreløpig ikke lagt ut noen leserbrev.
EOT
    print &footer;
    exit 0;
}

print &header("Leserbrev");
print <<EOT;

Nedenfor følger en datosortert liste over leserbrev. De tre feltene er
1) dato for innsending, 2) tittel og 3) navn på innsender

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
    $input{overskrift} =~ s/<.+?>//g;
    printf(qq{%-9s<a href="$utscript?file=$intdir/$filename">%-60s%s\n},
	   $dato, $input{overskrift}."</a>", $input{navn});
    close(FILE);
}

print "</pre>\n";
if (!$count) {
    print <<EOT;
<hr noshade size="2">
<blockquote>
Dessverre ingen leserbrev tilgjengelige ennå.
</blockquote>
<hr noshade size="2">
EOT
    } else {
	print "Tilsammen $count brev i listen ovenfor\n";
    }

print <<EOT;
<p>

Du kan selv <a href="brevskjema.html">sende inn leserbrev</a> ved å
bruke WWW. Det er også mulig å sende inn oppfølgerbrev til tidligere
innsendte leserbrev - dette kan du gjøre med "Oppfølger"-knappen etter
hvert leserbrev.

EOT

print &footer;
exit 0;
