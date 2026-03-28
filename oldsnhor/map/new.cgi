#!/local/bin/perl5

$dir = "/home/frogner/www/map";
$urlprefix = "http://www.oslonett.no/map";

$| = 1;  # flush
print "Content-type: text/html\n\n";

# print "<pre>\n";
# system "env";
# print "-----\n\n</pre>\n";


&die("Wrong content type posted")
    unless $ENV{CONTENT_TYPE} eq "application/x-www-form-urlencoded";
&die("Request method is not POST")
    unless $ENV{REQUEST_METHOD} eq "POST";
&die("Content-length is zero!")
    if $ENV{CONTENT_LENGTH} <= 0;
&die("No user name defined")
    unless length $ENV{REMOTE_USER};

$user = $ENV{REMOTE_USER};

$data = "";
$buf = "";
$bytes_left = $ENV{CONTENT_LENGTH};
while ($bytes_left > 0) {
    $n = sysread(STDIN, $buf, $ENV{CONTENT_LENGTH});
    &die("read failed: $!") unless defined $n;
    $data .= $buf;
    $bytes_left -= $n;
}

for (split(/&/, $data)) {
	($name, $val) = split(/=/, $_);
        $val =~ s/\+/ /g;
        $val =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;
	#print "$name: $val\n" if length $val;
	$query{$name} = $val;
}

&die("No mapfile passed in") unless defined $query{"map"};


@map = split(/\n/, $query{"map"});

# Check map syntax
$line = 0;     # line number
$error = 0;    # is there errors in the file
$content = 0;  # is there any content in the file
foreach (@map) {
    $line++;
    next if /^\s*#/;  # comment line
    next if /^\s*$/;  # empty line
    if (/^(circle|poly|rect|default)\s+/) {
       $content = 1;
       next;
    }
    $error = 1;
    print "Syntax error in line $line: $_\n";
}

if ($error) {
   exit;
}

if (! $content) {
    print "No map instructions in the file\n";
    exit;
}

if (defined $query{"id"}) {
    $id = $query{"id"};
    $id =~ s/\.map$//;
    unless (-f "$dir/$id.map") {
	print "No mapfile with ID=$id\n";
	exit;
    }
} else {
    # Try to allocate a filename
    $id = "a0";  # suitable for magical increment
    $id++ while -f "$dir/$user-$id.map";
    $id = "$user-$id";
}

$url  = "$urlprefix/$id.map";
$map  = "$dir/$id.map";

open(F, ">$map") or &die("Can't create $map: $!");
print F join("\n", @map);
close(F);

print "<h1>$url</h1>\n";

$sample = qq{<a href="$url">
   <img ismap src="sample.gif">
</a>};

print "$sample\n";

$sample =~ s/&/&amp;/g;
$sample =~ s/</&lt;/g;
$sample =~ s/>/&gt;/g;

print "<hr><h2>Sample usage:</h2><pre>
$sample
</pre><hr>
";

print "<h2>Mapfile content:</h2><pre>
";
print join("\n", @map);
print "</pre><hr>\n";

print qq{<form action="edit.cgi" method="GET">
<input type=hidden name="id" value="$id">
<input type=submit value="Edit mapfile">
</form>
};


sub die
{
    print "<h2>Intern feil</h1> @_";
    print "</body>\n";
    exit;
}

