#!/local/bin/perl5

require "intern/lib.pl";

print "Content-type: text/html\n\n";

&printheader("Browser er ikke implementert ennå\n");

print qq!<font size="+2>Gå tilbake til <a href="index.html">toppsiden</a>!;

&printfooter;
exit 0;
