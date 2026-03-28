#!/local/bin/perl5

require "lib.pl";

%input = &getinput;
$urlgruppe = &urlescape($input{'gruppe'});

if (! length $input{'gruppenavn'}) {
    # no group name given, respond with fill-in form
    &header("Opprett ny diskusjons-gruppe");
    print <<EOT;

Herfra kan det lages nye grupper. Følgende diskusjonsgrupper finnes allerede:

<form method="POST" action="$ENV{'SCRIPT_NAME'}">

<ul>
EOT
    opendir(DIR, $DISKUSJONDIR)
	|| &error("Kunne ikke åpne directory\'et $DISKUSJONDIR");
    foreach (sort readdir(DIR)) {
        next if /^\./;
	next if /^bin$/;
	next unless -d $_;
	$urlgr = &urlescape($_);

	( $noquotes = $_ ) =~ s/\"/&quot;/g;
	print qq! <li> <a href="$TOPPURL/diskusjon.cgi/$urlgr">$_</a><br>\n!;
    }
    closedir(DIR);
    
    print <<EOT;
</ul>

<font size="+2">Navn på ny gruppe:</font>
<input name="gruppenavn" size="40"><p>

<center><input type="submit" value=" Lag ny gruppe "></center>

</form>
EOT

&footer;
exit 0;


} else {
    &error("Angitt gruppe finnes allerede")
	if -d "$DISKUSJONDIR/$input{'gruppenavn'}";
    mkdir("$DISKUSJONDIR/$input{'gruppenavn'}", 0775);

    &header("Har opprettet ny gruppe");
    $urlgr = &urlescape($input{'gruppenavn'});
    print <<EOT;

Den nye gruppen har URL'en <a
href="$TOPPURL/diskusjon.cgi/$urlgr">http://$ENV{'SERVER_NAME'}$TOPPURL/diskusjon.cgi/$urlgr</a>.<p>

<center>
<a href="$ENV{'SCRIPT_NAME'}">Opprette flere nye grupper</a>
</center>
EOT
    &footer;
    exit 0;
}

