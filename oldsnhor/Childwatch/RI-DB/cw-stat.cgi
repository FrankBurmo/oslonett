#!/local/bin/perl5

$DB = "Childwatch/DATABASE";

$HEADER = <<"---";
<title>Childwatch</title>
<h2>Academic and other research institutions undertaking research and/or
with information on the rights of the child</h2>

<hr>
---

$TRAILER = <<"---";
<hr>
<a href="/Childwatch/top.html"><img src="/Childwatch/back2.gif" alt="Childwatch home"></a>
---

print "Content-type: text/html\n\n";

$_ = $ENV{PATH_INFO};

print $HEADER;

&fields if /fields/;
&xxxx   if /xxxx/;

print <<"---";

<ul>
   <li><a href="/$DB">The complete database!</a>
    <li><a href="stat/fields">Fields</a>
</ul>

$TRAILER
---

sub fields
{
    print "Fields seen in the database:
<pre>\n";
    open(F, "cut -d: -f1 $DB | sort | uniq -c | sort -rn|");
    while (<F>) {
	print "$_";
    }
    print "</pre>\n";
    print $TRAILER;
    exit;
}
