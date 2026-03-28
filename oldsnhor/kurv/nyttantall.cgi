#!/local/bin/perl5

require "lib.pl";

%input = &getinput;

open(KURV, "$DATADIR/kurv-$input{id}.data")
    || &error("Finner ikke igjen handlekurven din");

while (<KURV>) {
    ($vareid, $antall) = ( m,^/*(.+)\s+(\d+)$, );
    $vareantall{$vareid} += $antall;
}

close KURV;

if (length $input{antall}) {
    $vareantall{$input{vareid}} = $input{antall};
#    print "Content-type: text/html\n\n";
    open(KURV, ">$DATADIR/kurv-$input{id}.data")
	|| &error("Kan ikke lagre nytt antall i handlekurven din");
    foreach (sort keys %vareantall) {
	next if $vareantall{$_} <= 0;
	print KURV "/$_ $vareantall{$_}\n";
#	print  "/$_ $vareantall{$_}<br>\n";
    }
    close KURV;
    print "Location: http://$ENV{SERVER_NAME}/kurv/vis.cgi\n\n";

} else {

    &header("Velg antall");

    ($butikk, $varenr) = split(m!/!, $input{vareid});
    %info = &vareinfo($butikk,$varenr);

    $url = $butikkinfo{$butikk . '-url'};
    print <<EOT;

<form method="POST" action="$ENV{SCRIPT_NAME}">
<input type="hidden" name="id" value="$input{id}">
<input type="hidden" name="vareid" value="$input{vareid}">
<dl>
   <dt> <b>Butikk:</b>
   <dd> <a href="$url">$butikk</a>

   <dt> <b>Varenavn</b>
   <dd> <a href="$info{url}">$info{navn}</a>

   <dt> <b>Pris</b>
   <dd> $info{pris}

    <dt> <b>Antall</b>
    <dd> <input name="antall" value="$vareantall{$input{vareid}}" size="8">
</dl>
<input type="submit" value=" Velg nytt antall ">
</form>

</body>
</html>

EOT

}

exit 0;
