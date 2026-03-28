#!/local/bin/perl5

require "intern/lib.pl";
print "Content-type: text/html\n\n";

&getinput;

&error("Ingen referanse til leserbrev medsendt")
    unless length $input{file};

$input{file} = "$intdir/$input{file}" unless $input{file} =~ m!/!;
open(FILE, $input{file})
    || &error("Kunne ikke åpne filen $input{file}");

while (<FILE>) {
    chop;
    ($name, $value) = split(": ", $_, 2);
    $name =~ tr/A-ZÆØÅ/a-zæøå/;
    $input{$name} = $value;
}

$svar = "<em>$input{svar}</em>";
$svar .= "\n<h3>$input{signatur}</h3>" if length $input{signatur};

print &header("$input{overskrift}"); 
print <<EOT;
<center>
    <table border="10" cellpadding="6" width="550">
    <tr>
    <td>
    $input{leserbrev}
<h3>$input{navn}</h3>
EOT

print <<EOT if length $input{svar};
    <tr>
    <td>
    $svar
</td>
EOT

    print <<EOT;
</table>
</center>

<h3>Send oppfølger til dette leserbrevet...</h3> ...<a
href="reply.cgi?sitat=ja&ref=$input{file}"><b>med</b></a> eller <a
href="reply.cgi?ref=$input{file}"><b>uten</b></a> sitat av teksten
ovenfor.
<hr noshade size="1"><p>
EOT

    if (defined $input{ref}) {
	open(REF, $input{ref}) || &error("Kan ikke åpne referansefilen $input{ref}");
	while (<REF>) {
	    $reftitle = $1 if /^overskrift\s*:\s*(.+)/i;
	    $refpub = $1 if /^publiseres\s*:\s*(.+)/i;
	}
	close REF;
	print qq{Dette leserbrevet er en oppfølger til <a href="$utscript?file=}
            . qq{$input{ref}">$reftitle</a>.} if $refpub =~ /^ja/i;
    }

print qq!Tilbake til <a href="liste.cgi">listen over leserinnlegg</a>!;

print &footer;
exit 0;
