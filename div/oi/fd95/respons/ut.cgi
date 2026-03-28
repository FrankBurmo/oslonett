#!/local/bin/perl5

require "intern/fd-lib.pl";
print "Content-type: text/html\n\n";

&getinput;

&error("Ingen referanse til spørsmål/svar medsendt")
    unless length $input{file};

open(FILE, $input{file})
    || &error("Kunne ikke åpne filen $input{file}");

while (<FILE>) {
    chop;
    ($name, $value) = split(": ", $_, 2);
    $name =~ tr/A-ZÆØÅ/a-zæøå/;
    $input{$name} = $value;
}

#&error("Ikke autorisert til å se på denne oppføringen")
#    unless ($input{publisert} =~ /^ja$/);


$navn = "<p><font size=\"+1\"><b>$input{navn}</b></font>";
$navn .= "<br>\n$input{stilling}" if $input{stilling};
$navn .= "<br>\n$input{firma}" if $input{firma};

undef($navn) if ($input{anonym} =~ /^ja$/i);

print &header("Tema: $input{overskrift}"); 
print <<EOT;
<center>
    <table border="6" cellpadding="4">
    <tr>
    <td><h2><em>Spørsmål eller tilbakemelding:</em></h2>
    $input{kommentar}
    $navn
    <tr>
    <td>
    <h2><em>Svar på spørsmål eller kommentar til tilbakemelding:</em></h2>
    $input{svar}
<h3>$input{signatur}</h3>
</td>
EOT

    print "</table>\n</center>\n";

print &footer;
exit 0;
