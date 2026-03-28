#!/local/bin/perl5 -w

BEGIN {
    local($|) = 1;
    print "Content-Type: text/html\n\n";

    # This is needed so that sybase find it's interface file
    $ENV{SYBASE} = "/home/frogner/www2/sybase";
}

use lib "/home/hasle/a/aas/gs/lib";

use CGI::Query;
use GsSQL;

sql("set rowcount 50
select firma.navn, postnr, poststed.navn from firma, poststed
where firma.postnr = poststed.nr
order by firma.navn
",

sub {
    my($navn, $nr, $sted) = @_;
    print "<br><b>$navn</b> ";
    printf "%04d %s\n", $nr, $sted;
}

);
