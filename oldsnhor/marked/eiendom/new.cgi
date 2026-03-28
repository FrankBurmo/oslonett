#!/local/bin/perl -w

$DEBUG = 1;
$| = 1;
print "Content-type: text/html

";
#system "env";

print "\n<body>\n";

&die("Wrong content type posted")
   unless $ENV{CONTENT_TYPE} eq "application/x-www-form-urlencoded";
&die("Request method is not POST")
    unless $ENV{REQUEST_METHOD} eq "POST";
&die("Content-length is zero!")
    if $ENV{CONTENT_LENGTH} <= 0;

$top   = "/local/www/marked";
$lib   = "$top/lib";
$count = "$lib/COUNT";

# Read the posted data
$data = "";
$buf = "";
$bytes_left = $ENV{CONTENT_LENGTH};
while ($bytes_left > 0) {
    $n = sysread(STDIN, $buf, $ENV{CONTENT_LENGTH});
    &die("read failed: $!") unless defined $n;
    $data .= $buf;
    $bytes_left -= $n;
}

# Split the query string
#print "---form---\n" if $DEBUG;
for (split(/&/, $data)) {
	($name, $val) = split(/=/, $_);
        $val =~ s/\+/ /g;
        $val =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;
	#print "$name: $val\n" if length $val && $DEBUG;
	$query{$name} = $val;
}
#print "----------\n" if $DEBUG;

# Find the category
($category) = ($ENV{SCRIPT_NAME} =~ m,^/marked/([^/]+),);
&die("No category found in SCRIPT_NAME=$ENV{SCRIPT_NAME}")
    unless defined $category;
&die("No directory for category '$category'")
    unless -d "$top/$category";
# print "Category: $category\n";

$id = 0;
if ($query{id}) {
    $id = $query{id};
    delete $query{id};
    $op = "edited";
} else {
    # Get a new identifier by updating the $count file
    open(COUNT, "+<$count") or &die("Can't open $count: $!");
    flock(COUNT, 2) or &die("Can't flock: $!"); # exlusive lock
    chomp($id = <COUNT>);
    seek(COUNT, 0, 0) or &die("Can't seek to beginning: $!");
    $id++;
    print COUNT "$id\n";
    close(COUNT);
    $op = "created"
}
# print "ID: $id\n";

# Construct a file name.  This name should be unique.
$dir  = sprintf("%s/%s/%05d", $top, $category, $id);
$file = "$dir/DATA";
unless (-d $dir) {
   mkdir($dir, 0755) or &die("Can't make directory $dir: $!");
}
# print "File: $file\n";

if ($query{remove}) {
    delete $query{remove};
    # should not update the file, but instead just remove an existing one
    my $newdir = $dir;
    $newdir =~ s:/([^/]+)$:/,$1:;
    &die("Can't make a backupdir for $dir") if $newdir eq $dir;
    rename($dir, $newdir) or &die("Can't rename($dir, $newdir): $!");
    print "<h1>Entry $id removed</h1>\n</body>\n";
    system "$top/eiendom/mkindex 1>/dev/null 2>&1";
    exit;
}

# Fill the content of the data file
open(FILE, ">$file") or &die("Can't open $file: $!");

$tekst = $query{text};
delete $query{text};

for (sort keys %query) {
    $k = $_;
    $v = $query{$_};
    $v =~ s/\s+/ /g;  # also removes newlines
    next unless length $v;
    $k =~ s/\b\w/\U$&/g;

    #print STDOUT "$k: $v\n" if $DEBUG;
    print FILE "$k: $v\n";
}
if ($tekst) {
    print FILE "\n$tekst\n";
}
close(FILE);


print qq{<h1>Entry $id $op</h1>
<a href="edit.cgi?id=$id">[EDIT]</a>

};

print "</body>\n";
system "$top/eiendom/mkindex 1>/dev/null 2>&1";
exit;


#--- Library ---
sub die
{
    print "<h2>Intern feil</h1> @_";
    print "</body>\n";
    exit;
}

