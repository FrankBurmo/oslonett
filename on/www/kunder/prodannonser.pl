#!/usr/local/bin/perl
#prodside.pl: Genererer en oversikt over Kvasir annonsører for et år.
#
#Tar året som parameter.



$aarstall = $ARGV[0];

$HTMLFILE = "kvasir-annonse$aarstall.html";

open(STDERR, "/dev/null");

open(OUT, ">$HTMLFILE" || die "can't open input file $HTMLFILE\n");



	    print OUT "
<html>
<head>
  <title>Annonsering i Kvasir: $aarstall</title>
 <link rev=made href=\"mailto:webmaster@sn.no\">
</head>
<body background=\"/gifs/on/onbg.gif\">
<a href=\"priser.map\">
<img alt=\"\" align=middle src=\"/gifs/on/www-h.gif\" border=0 ISMAP>
</a>
<h1>Annonsering i Kvasir : $aarstall</h1>


<blockquote>
<table border=1 cellpadding=5>
<dl>
<tr> <td valign=\"middle\" align=\"center\" colspan=\"4\">
 <font size=+1><h3>Annonsepakker</h3></font></td></tr>
<tr>
 <td><dt><b>Uke</td>
 <td align=\"right\"><dd><b>annonsør</td>     
 <td align=\"right\"><dd><b>Logo URL</td>
 <td align=\"right\"><dd><b>Pris</td>
</tr>
";

for ($uke = 1; $uke<53; $uke++) {
    print OUT "
<tr>
 <td><dt>$uke</td>
 <td align=\"right\"><dd>ledig</td>
 <td align=\"right\"><dd>logo</td>
 <td align=\"right\"><dd>pris</td>
</tr>
";
}

print OUT "
</dl>      
</table>
</blockquote>


<hr size=\"2\" noshade>

<address>
 <font size=\"-1\">
  Copyright &#169; 1995,  Schibsted Nett AS.
 </font>
</address>

</body>
</html>
";

close(HTMLFILE);

