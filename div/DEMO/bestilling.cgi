#!/local/bin/perl


print "Content-type: text/html\n\n";

print "<Head><Title>Bestilling av CD'er fra Akers Mic</Title></Head>";
print "<Body BACKGROUND=\"/div/DEMO/bg2.gif\" rgb=\"#ff00ff\" TEXT=\"#FFFF00\" LINK=\"#00FF7F\" VLINK=\"#38B0DE\" ALINK=\"#0077FF\">\n";
print "<center><IMG SRC=/div/DEMO/topp20.gif></center>\n";

# Get the input
read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});

# Split the name-value pairs
@pairs = split(/&/, $buffer);

foreach $pair (@pairs)
{
    ($name, $value) = split(/=/, $pair);
    $value =~ tr/+/ /;
    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

    # Uncomment for debugging purposes
    #print "Setting $name to $value\n";

    $query{$name} = $value;
}

$db = "/local/www/div/DEMO/DB";

unless ($query{'id'}) {
    print "No id\n";
    exit;
} 

unless (open(F, "$db/$query{'id'}")) {
    print "Ulovlig kundernr.\n";
    exit;
}

while (<F>) {
    chomp;
    ($key,$val) = split(/:\s*/, $_, 2);
    #print "$key: $val\n";
    $db{$key} = $val;
}
close(F);

if ($db{'pin'} && $db{'pin'} ne $query{'pin'}) {
    print "Ulovlig pin.\n";
    exit;
}

$tmp = "$db/bestill$$.txt";

open(TMP, ">$tmp");
$t = localtime;
print TMP "
------- $t
Kunde: $query{id} $db{'navn'}
";
for (1..20) {
    if ($query{"cd$_"} eq "on") {
	print TMP "CD #$_\n";
    }
}
close(TMP);

$pgp = "/local/bin/pgp";

$| = 1; print;  # flush

$ENV{HOME} = "/home/gimle/www";
system "$pgp -esa $tmp akersm </dev/null >/dev/null 2>&1";

system "cat $tmp >>$db/liste.txt";
system "rm $tmp";

print "<h2>Bestilling registrert</h2>
<a href=\"http://www2.oslonett.no/div/DEMO/mtopp20.html\">Tilbake</a>
";

print "

<pre>



































";

system "cat $tmp.asc; rm $tmp.asc";  # Mail virker ikke

print "
</pre><p>
Denne bestillingsmeldingen blir sendt til Aksers Mic.
Meldingen er kryptert slik at bare Akers Mic kan lese den.
Meldingen er signert av Oslonett AS.

";

