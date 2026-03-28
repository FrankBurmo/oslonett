#!/local/bin/perl

print "Content-type: text/html\n\n";

&write_header;
&write_contents;
&write_footer;



exit 0;

sub write_header
{
    print <<"stopp_her";

<html>
<head>
<title>
Stillingsbeskrivelse
</title>
</head>

<body background="http://www.oslonett.no/gifs/on/onbg.gif">
<img alt="" src="http://www.oslonett.no/gifs/on/oslonett-h.gif" border=0>

<center><h1>OVERSIKT OVER <br> STILLINGER</h1></center>
    
<p>
<hr size=2 noshade>
<p>
<ul>
stopp_her

    return;
}


sub write_contents
{
    opendir(DIR,'.') || die "Can't open $dir";
    local(@filenames) = readdir(DIR);
    closedir(DIR);

    for (@filenames) {
	next if $_ eq '.';
	next if $_ eq '..';
	$name2 = $_;
	$name = "$dir/$_";
	if (substr($name,-5) eq ".html") {
	    print "<li>";
	    print "<a href=\"/on/www/adm/stdata$name\"> $name </a>";
	}			
    }			

}

sub write_footer
{
    print STDOUT <<"HERSLUTTERVI";

</ul>
<hr size="1" noshade>
<a href="/">
  <img alt="[Oslonett Home]" border="0" src="/gifs/on/home.gif" border=0></a>
<a href="/help.html">

HERSLUTTERVI

    print <<TEST2;

  <img alt="[Hjelp]" border="0" src="/gifs/on/hjelp.gif"></a>
<a href="/search.html">
  <img alt="[Søk]" border="0" src="/gifs/on/sok.gif"></a>
<hr size=2 noshade>
TEST2

    print <<TEST3;
<address>
 <font size="-1">
  Copyright 1995,  Oslonett AS.
 </font>
</address>
</body>

TEST3

    print "</html>";


    return;

}
