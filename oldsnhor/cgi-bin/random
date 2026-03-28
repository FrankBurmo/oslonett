#!/local/bin/perl5

#print "Content-type: text/plain\n\n";

# $Id$
#
# This script picks some random url from the Www urldb.  It can also
# run a slideshow for Netscape.
#
# Author: Gisle Aas, Oslonett AS


$urldb = "/home/frogner/www/me/rt/janco/URL-DB";
$count = 21;

&fail if ($count <= 0);

$query{'notprefix'} = [];

for (split(/&/, $ENV{QUERY_STRING})) {
	($name, $val) = split(/=/, $_);
        $val =~ s/\+/ /g;
        $val =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;
	#print "$name: $val\n" if length $val;
	if (defined $query{$name}) {
	    $query{$name} = [ $query{$name} ] unless ref($query{$name});
	    push(@{$query{$name}}, $val);
	} else {
	    $query{$name} = $val;
	}
}

if ($query{'url'}) {  # slideshow callback
    #print "Content-type: text/plain\n\n";
    print "Location: $query{url}\n";
    my $sleep = $query{'sleep'} || 30;
    ($q = $ENV{QUERY_STRING}) =~ s/&?url=[^&]*//; # remove url from query
    print "Refresh: $sleep; URL=http://www.oslonett.no$ENV{SCRIPT_NAME}?$q\n";
    print "\n";
    exit;
}

srand(time);

$domain    = $query{'domain'};
@notprefix = @{$query{'notprefix'}};

# print "Content-type: text/plain\n\n";   # useful while debugging

open(U, $urldb) || &fail;

if ($domain || @notprefix) {
    # hvis vi har begrensende kriterier så lager vi først en liste
    # av de ressursene som er potensielle valg.
    @potential = ();
  URL:
    while (<U>) {
	($url, $name) = split(' ', $_, 2);
	next URL unless domain_accepted($url, $domain);
	for $pre (@notprefix) {
	    next URL if substr($name, 0, length $pre) eq $pre;
	}
	push(@potential, [$url, $name]);
    }
    fail("Ingen ressurser å velge blandt") unless @potential;

    # så velger vi en av disse
    ($url, $name) = @{ $potential[rand @potential] };
} else {
    # ellers så kan vi bare velge en tilfeldig linje i fila.
    $random = int(rand $count);
    while (<U>) {
	last if $random-- <= 0;
    }
    &fail unless $_;
    ($url, $name) = split(' ', $_, 2);
}
close(U);


unless (defined $query{'no'}) {
    print "Location: $url\n\n";
    exit;
} else {
    ($ua, $ver) = ($ENV{HTTP_USER_AGENT} =~ m,([^/]+)/(\S+),);
    &you_need_mozilla unless $ua eq "Mozilla" && $ver >= 1.1;

    $no = int($query{'no'});
    if ($no > 0) {
	my $sleep = $query{'sleep'} || 30;
        my $domain = "";
        $domain = "&domain=$query{'domain'}"
	    if defined $query{'domain'} && length $query{'domain'};
	if (defined $query{'noposter'}) {
	    $no--;
	    print "Location: $url\n";
	    print "Refresh: $sleep; ",
	      "URL=http://www.oslonett.no$ENV{SCRIPT_NAME}?no=$no&sleep=$sleep&noposter=1$domain\n\n";
	    exit;
	} else {
	    $of = int($query{'of'}) || $no;
	    $no--;
	    my $qurl = $url;  # need to escape url before using it
	    $qurl =~ s/["%&=+\177-\377]/sprintf("%%%02X", ord($&))/ge;
	    print "Content-type: text/html\n";
	    print "Refresh: 3; ",
            "URL=http://www.oslonett.no$ENV{SCRIPT_NAME}?no=$no&sleep=$sleep$domain",
	           "&url=$qurl&of=$of\n\n";
	    poster($url, $name, $no, $of, $sleep, $domain);
	    exit;
	}
    } else {
        # Present THE END page
	print <<"EOT";
Content-type: text/html

<title>The End</title>
<body bgcolor="#ffffff">

<center>

<p><font size=+2>Jancos World Wide Web slideshow over kabelnett ble presentert av</a></font>

<p>
<table border=0 cellspacing=10 cellpadding=10>
<tr><td><a href="http://www.oslonett.no/"><img align="middle" src="/gifs/on/oslonett-i.gif" alt="Oslonett AS" border=0></a></td><td><font size=+3>OG</font></td><td><a href="/me/rt/janco/"><img align="middle" src=/me/rt/janco/gifs/janco.gif border=0 alt="Janco"></a></td></tr>
</table>
</center>


<hr width="25%" align=left>
<i>Design og program, Copyright © 1995 <a href="http://www.oslonett.no/">Oslonett AS</a>
</body>


EOT
    }
}



sub domain_accepted
{
    my($url, $domain) = @_;
    return 1 if !defined($domain) || length($domain) == 0;

    $url =~ m,^\w+://([\w.\-]+),;
    my $host = $1;
    return 0 unless defined $host;
    scalar($host =~ /$domain$/o);
}


sub poster
{
    my($url, $name, $no, $of, $sleep, $domain) = @_;
    $name =~ s,(.*)/,,;
    $place = $placedir = $1;
    $name =~ s/_#\d+$//g;
    $name =~ s/_/ /g;
    $place =~ s,/, : ,g;
    $place =~ s/_/ /g;

    $domain =~ s/^&domain=//;    

    $n = $of - $no;

    print <<"EOT";
<title>Slideshow poster</title>
<body background="/me/rt/janco/gifs/j_bg2.gif">
<center>
<h3>Janco og Oslonett demonstrerer Internett slideshow over kabel:</h3>
<table border=8 cellpadding=15>
<tr><th>
<b><font size=6>$name</font></b>
<br><br><font size=3>$url</font>
</th></tr>
</table>
<p>
($n av $of)
<br><br>

<table>
<tr>

<td>
<form action="http://www.oslonett.no$ENV{SCRIPT_NAME}">
<input type=hidden name=no value=$no>
<input type=hidden name=sleep value=$sleep>
<input type=hidden name=of value=$of>
<input type=hidden name=domain value=$domain>
<input type=submit value="Hopp videre">
</form>
</td>

<td>
<form action="http://www.oslonett.no$ENV{SCRIPT_NAME}">
<input type=hidden name=no value=0>
<input type=submit value="Avbryt showet">
</form>
</td>

</table>

</center>
</body>
EOT
}


sub fail
{
    my $message = shift || "Internal error.";
    print <<"EOF";
<title>Www - Random link failed!</title>
<h1>JANCO - Random link failed!

$message

<p>
&lt;<a href="mailto:www\@oslonett.no">www\@oslonett.no</a>&gt;

EOF
  exit;

}

sub you_need_mozilla
{
    print <<"EOT";
Content-type: text/html


<title>You Need Mozilla</title>
<body bgcolor="#ffffff">

<h2>Du må ha Netscape versjon 1.1 eller bedre</h2>

Så vidt vi vet er det bare Netscape som implementerer "client pull" som
benyttes i slideshowet.

<p><a href="/www/">Gå tilbake til Wwws toppside!</a>
</body>
EOT
   exit;
}
