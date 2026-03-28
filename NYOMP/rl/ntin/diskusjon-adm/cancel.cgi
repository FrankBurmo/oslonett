#!/local/bin/perl

require "lib.pl";

%input = &getinput;
$urlgruppe = &urlescape($input{'gruppe'});

&error("Ingen diskusjonsgruppe angitt") 
    if (length $input{'id'} && !length $input{'gruppe'});
if (! length $input{'id'}) {
    # no article id given, respond with fill-in form
    &header("Master Cancel");
    print <<EOT;

For å slette et gammelt innlegg må du oppgi diskusjonsgruppe og
identifikasjonsnummer for den artikkelen du vil slette (dette finner
du i URL\'en til innlegget du vil slette)

<form method="POST" action="$TOPP/diskusjon-adm/cancel.cgi">

<font size="+2">
Velg diskusjonsgruppe du vil slette innlegg fra:</font>
<blockquote>
EOT
    opendir(DIR, $DISKUSJONDIR)
	|| &error("Kunne ikke åpne directory\'et $DISKUSJONDIR");
    foreach (sort readdir(DIR)) {
        next if /^\./;
	next unless -d $_;
	$urlgr = &urlescape($_);

	$checked = ($_ eq $input{'gruppe'}) ? " checked" : "";
	( $noquotes = $_ ) =~ s/\"/&quot;/g;
	print qq!<input type="radio" name="gruppe" value="$noquotes" $checked> !;
	print qq!<a href="$TOPP/diskusjon.cgi/$urlgr">$_</a><br>\n!;
    }
    closedir(DIR);
    
    print <<EOT;
</blockquote>
<font size="+2">Innlegg-id:</font>

<input name="id" value="$input{'id'}" size="10"><p>

<input type="submit" value=" Slett innlegg ">

</form>
EOT

&footer;
exit 0;


} else {
    $filename = sprintf("$DISKUSJONDIR/$input{'gruppe'}/art%05d.txt",
			$input{'id'});

    if ( rename($filename, "$filename.backup") ) {
	&header("Har slettet innlegg");
	print "Innlegg nr. $input{'id'} er nå slettet fra ";
	print qq!<a href="$TOPP/diskusjon.cgi/$urlgruppe">!;
	print qq!diskusjonsgruppen $input{'gruppe'}</a>.<p>!;
	print qq!<a href="$ENV{'SCRIPT_NAME'}/?gruppe=$urlgruppe">Slette flere innlegg</a><p>\n!;

    } else {
	&header("Ingen sletting utført");
	print "...fordi angitt artikkel (id=$input{'id'}) ikke finnes.<p>\n";
	print qq!Tilbake til <a href="$TOPP/diskusjon.cgi/$urlgruppe">!;
	print qq!diskusjonsgruppen "$input{'gruppe'}"</a> eller !;
	print qq!tilbake til <a href="$ENV{'SCRIPT_NAME'}?gruppe=$urlgruppe">!;
	print "skjema for sletting av inlegg</a>.<p>\n";
    }

    &footer;
    exit 0;
}

