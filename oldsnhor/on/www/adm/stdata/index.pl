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

<center><h1>OVERSIKT OVER <br> STILLINGSBESKRIVELSER</h1></center>
    
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
	    print "<a href=\"$name\"> $name </a>";
	}			
    }			

}

sub write_footer
{
    print "

<pre>

</pre>
<center>
<font size=+2>Gjennomgang foretatt og godkjent<br>
Oslo, XX.juni 1995</font>
</center>
<pre>

</pre>
<hr size=1 width=50% align=left noshade>
<font size=-1>Nærmeste overordnet</font>
<p>
			
<hr size=1 width=50% align=left noshade>
<font size=-1>Stillingsinnehaver</font>
</body>
</html>
";				


}
