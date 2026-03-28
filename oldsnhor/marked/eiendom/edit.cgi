#!/local/bin/perl -w

$top   = "/local/www/marked";
$lib   = "$top/lib";

require "$lib/parse.pl";

$DEBUG = 1;
$| = 1;
print "Content-type: text/html

";

if (0 && $DEBUG) {
    print "<font size=-1><pre>\n"; system "env"; system "pwd"; print "</pre></font>\n";
}
# Split the query string
#print "---form---\n" if $DEBUG;
for (split(/&/, $ENV{QUERY_STRING})) {
	($name, $val) = split(/=/, $_);
        $val =~ s/\+/ /g;
        $val =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;
	#print "$name: $val\n" if length $val && $DEBUG;
	$query{$name} = $val;
}
#print "----------\n" if $DEBUG;

$id = $query{id};
unless ($id) {
   # Present an empty form
    print qq{<title>Eiendom Administrasjon</title>

<body>
<h1>Make a new ad</h1>

<form action="new.cgi" method="POST">
};

    &print_form( {} );

    print qq{
<p><input type=submit value="Create...">
<input type=reset value="Clear">
</form></body>
};
    exit;
}

# print "\n\nID: $id\n";
&die("No entry called $id") unless -d $id;

$e = parse("$id/DATA");
&die("Can't parse $id/DATA") unless $e;

print "<title>Eiendom Administrasjon</title>

<body>
<h1>Administrasjon [$id]</h1>

";

print qq{<form action="new.cgi" method="POST">
<input type=hidden name="id" value="$id">
};

&print_form($e);

print qq{
<p><input type=checkbox name=remove value="1"> Remove this ad
<p><input type=submit value="Edit...">
<input type=reset value="Reset">
</form>
};

unless ($query{cmd}) {
   print "</body>\n";
   exit;
}

print "\nCMD: $query{cmd}\n";
&remove($id) if $query{cmd} eq "remove";
&edit($id)   if $query{cmd} eq "edit";

&die("Unknown command: $query{cmd}");


#--- Library ---
sub die
{
    print "<h2>Intern feil</h1> @_";
    print "</body>\n";
    exit;
}

sub remove
{
    print "REMOVE....\n";
    my($id) = @_;

    exit;
}

sub edit
{
    print "EDIT....\n";
    exit;
}

sub print_form
{
    my($e) = @_;
    local($^W) = 0;  # suppress warning for using undefined values
    print <<"EOF";
<pre>
Tittellinje: <input name=title size=50 value="$e->{title}">
Boligtype:   <select name=type>
<option>Enebolig
<option>Tomannsbolig
<option>Rekkehus
<option>Leilighet
<option>Hybel
</select>  Eierform: <select name=eierform>
<option>Selveier
<option>Aksjeleilighet
<option>Andelsleilighet
<option>Leie
</select>
Adresse:     <input name=address size=50 value="$e->{address}>
Postnr/sted: <input name=zipcode size=4 value="$e->{zipcode}"> <input name=place size=30 value="$e->{place}">
Område:      <input name=area size=50 value="$e->{area}">

Prisantyding:<input name=price value="$e->{price}" size=7> Takst: <input name=takst size=14 value="$e->{takst}">  Leie: <input name=leie size=5 value="$e->{leie}> pr/mnd.
Boligareal:  <input name=size size=6 value="$e->{size}"> m²  Antall soverom: <input name=rooms size=4 value="$e->{rooms}">
Visning:     <input name=visning size=50 value="$e->{visning}">

Tekst:       <textarea name=text cols=50 rows=4>$e->{text}</textarea>

Utgår om:    <select name=expires>
<option value="2">2 dager
<option value="7">1 uke
<option value="14">2 uker
<option value-"0">Aldri
</select>
</pre>
EOF
}
