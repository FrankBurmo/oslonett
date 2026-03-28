#!/local/bin/perl5


$cookiename = "kurvid";
$DATADIR = "/local/www/kurv/kunder";

%input = &getinput;

$input{id} = &getid;

# Make sure netscape client remembers cookie till next time
print "Set-Cookie: $cookiename=$input{id}; path=/\n";

# $DEBUG = 1;
if ($DEBUG) {
    print "Content-type: text/html\n\n";
    print "<pre>\n";
    print "$ENV{HTTP_COOKIE}\n";
}


open(KURV, ">>$DATADIR/kurv-$input{id}.data")
    || &error("Kunne ikke legge varen ned i kurven");
print KURV "$ENV{PATH_INFO} 1\n";
close KURV;

$goto = (length $input{'ref'})
    ? $input{'ref'} : "/kurv/vis.cgi?id=$input{id}";

# $goto = "/kurv/vis.cgi?id=$input{id}";

print "Set-Cookie: $cookiename=$input{id}; path=/\n";
print "Location: $goto\n\n";


exit 0;


sub getid {
    # is ID given explicitly?
    return $input{id} if length $input{id};

    # get input from HTTP-cookie
    return $1 if $ENV{HTTP_COOKIE} =~ /$cookiename=(\d+)/;

    # only one user registered from REMOTE_ADDR?
    # not implemented yet

    srand(time || $$);
    $id = int(rand(1e+8)) + 1;	# don't want id=0.

    return $id;
}



sub getinput {
# Return %input array, associating input names with input values
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

        $input{$name} = $value;
    }
    %input;                     # returnerer den assosiative array'en
}



sub error {
# returns HTML error message and exits program
    local($msg) = $_[0];

    print "Content-type: text/html\n\n";
    print <<EOT;
<html>
<head>
<title>$msg</title>
</head>
<body bgcolor="#ffffff">
<h1>Feilmelding</h1>

Programmet ble avbrutt med følgende feilmelding:
<center>
<font size="+2">
$msg
</font>
</center>
EOT
    exit 1;
}

