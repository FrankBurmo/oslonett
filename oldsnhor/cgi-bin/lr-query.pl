#!/local/bin/perl5 
#
# CGI-script som tar imot input fra HTML FORM og sender mail til
# nærmere angitt mottaker. Følgende felter 
# 	mailto		mottaker for mail
#	reply-to	hvor evt. svar på tilsendt mail skal sendes
#	subject		ønsket tittel i utsendt mail
#	rcpt-url	URL til kvitteringsdokument dersom standard
#			kvittering ikke ønskes
#	allow-any-host	Send med ett eller annet innhold her for å tillate at
#			mailit brukes fra dokumenter utenfor Oslonetts domene

$replyaddr	= "webmaster\@oslonett.no";
$defaultsubj	= "[Mail relayed through Oslonett Netsite CGI gateway]";

%input = &getinput;

$input{'reply-to'} = $replyaddr unless $input{'reply-to'};
$input{subject} = $defaultsubj unless $input{subject};

$bodyattr = " $input{bodyattr}";
$imgattr = "<img $input{imgattr}>" if $input{imgattr};
delete($input{bodyattr});
delete($input{imgattr});

&assert;

open(MAIL, "| /usr/lib/sendmail -t")
    || &error("Feil i CGI-script: kunne ikke starte sendmail");
print MAIL "To: $input{mailto}\nSubject: $input{subject}\n";
print MAIL "Reply-To: $input{'reply-to'}\n" if $input{'reply-to'};
print MAIL "X-Ref: Mail relayed through Oslonett Netsite CGI gateway\n";
print MAIL "\n";	# Extra LF to separate header from body

foreach (@datanames) {
    next if $_ eq "bodyattr";
    next if $_ eq "imgattr";
    next if /^mailto$|^subject$|^reply-to$|^rcpt-url$/;
    $input{$_} =~ s/^\.$/. /;	# "\n.\n" must not end mail msg. being composed
    printf MAIL "%20s : %s\n", $_, $input{$_};
}
printf MAIL "%20s : %s\n", "Sendt fra maskin", $ENV{REMOTE_HOST};
printf MAIL "%20s : %s\n", "Aksessert fra", $ENV{HTTP_REFERER};
print MAIL "\n\n ---\n\n";
print MAIL "Henvendelser angående denne tjenesten rettes til $replyaddr\n";
print MAIL "\n.\n";
close (MAIL);

if ($input{'rcpt-url'}) {
    print "Location: $input{'rcpt-url'}\n\n";
    exit 0;
}

&printheader("Oslonett CGI-GW: Kvittering");

print "Vi har registrert flg. informasjon postet fra deg:<p>\n<hr>\n";

print "<pre>\n";

foreach (@datanames) {
    next if /^mailto$|^subject$|^reply-to$|^rcpt-url$/;
    next unless $input{$_} =~ /\S/;
    printf "%30s : %s\n", $_, $input{$_};
}
printf "%30s : %s\n", "Sendt fra maskin", $ENV{REMOTE_HOST};
printf "%30s : %s\n", "Aksessert via", $ENV{HTTP_REFERER}
    if $ENV{HTTP_REFERER};
print "</pre>\n";

print "Denne informasjonen er elektronisk oversendt til $input{mailto}.\n";
&printfooter;

exit 0;


sub assert {
# Return error message if
#	- wrong CONTENT_TYPE
#	- access from HTML document not within oslonett.no domain
#	- no "mailto" input field indicated (no one to send mail to)

    &error("Dette programmet kan kun dekode input fra HTML FORMS")
	unless $ENV{CONTENT_TYPE} eq "application/x-www-form-urlencoded";

    &error("Programmet kan kun brukes fra HTML-filer som ligger på Oslonetts" .
	   "web-servere</h2>Programmet ble aksessert via $ENV{HTTP_REFERER}")
	unless ($ENV{HTTP_REFERER} =~ /oslonett\.no/
		|| ! length $ENV{HTTP_REFERER}
		|| defined($input{'allow-any-host'}));

    &error("Ingen mottakeradresse medsendt (feil i HTML FORM)")
	unless  length $input{mailto};
}



sub getinput {
# Return %input array, associating input names with input values
# Also builds global array @datanames, giving original order of input
# field names.
    local($i, $name, $value, $data, @data, %input);

    if ($ENV{'REQUEST_METHOD'} eq "GET") {
        $data = $ENV{'QUERY_STRING'};
    } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
        read(STDIN, $data, $ENV{'CONTENT_LENGTH'});
    } else {
        return;
    }

    # Del opp input-data i felter ved alle forekomster av '&'.
    @data = split(/&/, $data);

    for $i (0 .. $#data) {

        # Pluss oversettes til SPC
        $data[$i] =~ tr/+/ /;

        # Alt til venstre for første "=" er feltnavn, resten er felt-verdi
        ($name, $value) = split(/=/, $data[$i], 2);

        # Erstatt forekomster av %<hexkode> med tilsvarende tegn
        $name =~ s/%(..)/pack("c",hex($1))/ge;
        $value =~ s/%(..)/pack("c",hex($1))/ge;

	$value =~ s/\s+/ /g;
	push(@datanames, $name);
	$input{$name} = $value;
    }
    %input;                     # returnerer den assosiative array'en
}


sub error {
# returns HTML error message and exits program
    local($msg) = $_[0];

    &printheader("Oslonett CGI-GW: Kvittering");
    print "<h2>$msg</h2>";
    print "Eventuelle spørsmål kan rettes til ";
    print "<a href=\"mailto:$replyaddr\">$replyaddr</a>.";
    &printfooter;
    exit 1;
}


sub printheader {
    local($head) = $_[0];
    local($img);
    $img = "<img $input{imgattr}>" if $input{imgattr};

    print "Content-type: text/html\n\n";

    print "<html>\n<head>\n <title>$head</title>\n";
    print qq{ <link rev="made" href="mailto: $replyaddr"></head>\n};
    print "<body >\n$imgattr<h1>$head</h1>\n\n";
}


sub printfooter {
    print qq{\n<hr>\n<a href="http://www.oslonett.no/">\n};
    print qq{  <img border="0" alt="[Oslonett Home]" src="/gifs/on/oslonett-i.gif"></a>\n};
    print "</body>\n</html>\n";
}

