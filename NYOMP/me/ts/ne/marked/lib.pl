
$BASE   = '/local/www/me/ts/ne/autolink/links.txt';
$replyaddr	= 'webmaster@sn.no';

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
        $input{$name} .= "|" if length $input{$name};
	$input{$name} .= $value;
    }
    %input;                     # returnerer den assosiative array'en
}


sub error {
# returns HTML error message and exits program
    local($msg) = $_[0];

    &printheader("Schibsted Nett CGI-GW: Kvittering");
    print "<h2>$msg</h2>";
    print "Eventuelle spørsmål kan rettes til ";
    print "<a href=\"mailto:$replyaddr\">$replyaddr</a>.";
    &printfooter;
    open(ERR, ">>$ERRORFILE") || exit 1;
    print ERR "Date:        ", `/usr/bin/date`;
    print ERR "Remote-host: $ENV{REMOTE_HOST}\n";
    print ERR "Remote-addr: $ENV{REMOTE_ADDR}\n";
    print ERR "HTTP referer:$ENV{HTTP_REFERER}\n" if length $ENV{HTTP_REFERER};
    print ERR "Error:       $msg\n";
    print ERR "\n";
    close ERR;

    exit 1;
}


sub printheader {
    local($txt) = $_[0];

    print "Content-type: text/html\n\n";

    print <<EOT;
<html>
<head>
<title>$txt</title>
</head>
<body bgcolor="#edda74">
<center>
    <a href="/home/bladetne"><img width="204" height="76" 
	border="0" src="/home/bladetne/ne-logo.gif"></a>
</center>
<h1>$txt</h1>
EOT
}


sub printfooter {
    print qq{\n<hr><font size="-1"><a href="$ENV{SCRIPT_NAME}">Markedsoversikten</a> er lagt opp i WWW for };
    print qq{<a href="/home/bladetne/">NæringsEiendom</a> av };
    print qq{<a href="http://www.sn.no/sn/">Schibsted Nett AS</a></font>\n};
    print qq{</body>\n</html>\n};
}



1;				# return 1 since this is a library
