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

Nedenfor følger listen over alle publiserte leserbrev. 

EOT

# pass 1 read file, build @children lists
foreach $filename (@file) {
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
    $title{$filename} = $input{overskrift};
    $date{$filename} = $input{regdato};
    $name{$filename} = $input{navn};
    if (defined $input{ref}) {
	$input{ref} =~ s%.+/%%;
        $children{$input{ref}} .= "," if defined( $children{$input{ref}});
        $children{$input{ref}} .= $filename;
        $ref{$filename} = $input{ref};
    }
    close(FILE);
}

# pass 2 traverse titles, build array of orphans sorted 
FILE:
foreach $filename (keys %title) {
    if (!defined $ref{$filename}) {
	push(@orphans, $filename);
        next FILE;
    }
    open(REF, "$intdir/$ref{$filename}")
        || &error("Kunne ikke åpne referansefilen $ref{$filename}");
    $pub = "";
    while (<REF>) {
        $pub = $1 if /^publiseres\s*:\s*(.+)/i;
	last if length $pub;
    }
    push(@orphans, $filename) if $pub =~ /^nei/i;
}

# pass 3 traverse @orphans, print reference tree

print "<dl>\n";
foreach (sort @orphans) {
    &printitem($_);
}
print "</dl>\n";

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
hvert leserbrev.<p>

Det er også mulig å se en liste over <a href="dato-liste.cgi">alle
leserinnlegg sortert etter registreringsdato</a>.

EOT

print &footer;
exit 0;



sub printitem {
    local ($o) = $_[0];
    local ($child);

    print qq!<dt> <a href="$utscript?file=$o">$title{$o}</a> ($name{$o})\n!;
    if (defined $children{$o}) {
	print "<dl>\n";
	foreach $child (split(/,/, $children{$o})) {
	    &printitem($child);
	}
	print "</dl>\n";
    }
}
