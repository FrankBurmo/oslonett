#!/local/bin/perl5 

$dir = "/local/www/map";
$urlprefix = "http://www.oslonett.no/map";

$| = 1;  # flush
print "Content-type: text/html\n\n";

# print "<pre>\n";
# system "env";
# print "-----\n\n</pre>\n";

&die("No user name defined")
    unless length $ENV{REMOTE_USER};
$user = $ENV{REMOTE_USER};

for (split(/&/, $ENV{QUERY_STRING})) {
	($name, $val) = split(/=/, $_);
        $val =~ s/\+/ /g;
        $val =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;
	#print "$name: $val\n" if length $val;
	$query{$name} = $val;
}

if (defined $query{"id"}) {
    $id = $query{"id"};
    $id =~ s/\.map$//;
    $map = "$dir/$id.map";
    if (-f $map) {
        print qq{<title>Edit mapfile</title>
<h1>Edit mapfile ($id)</h1>
<form action="new.cgi" method=POST>
<input type=hidden name=id value="$id">
<textarea name=map cols=60 rows=12>
};
        system "cat", $map;
	print qq{</textarea>
<p><input type=submit value="Update it!"

</form>
};	system "cat", "$dir/format.html"
    } else {
        print "<h2>No mapfile with ID=$id</h2>\n";
    }
    exit;
} else {
    print "<body bgcolor=ffffff>\n";
    print "<h2>Select a mapfile for user $user:</h2>\n<ul>\n";

    opendir(DH, $dir) or &die("Can't open $dir: $!");
    foreach (sort readdir(DH)) {
	next unless /\.map$/;
        next unless /^$user-/o;
        print qq{<li> <a href="edit.cgi?id=$_">$_</a>\n};
    }
    print "</ul>\n";

    print "<a href=\"/map/\"><img alt=\"[Map Service]\" border=0 src=\"/gifs/on/home.gif\"></a>\n";
    print "<hr align=left size=1 noshade width=30%>\n";
    print "<address>\n";
    print "Copyright © 1995, Oslonett AS\n</address>\n</body></html>\n";
    closedir(DH);
}

sub die
{
    print "<h2>Intern feil</h1> @_";
    print "</body>\n";
    exit;
}

