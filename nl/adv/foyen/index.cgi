#!/local/bin/perl

($ua, $ver) = ($ENV{HTTP_USER_AGENT} =~ m,([^/]+)/(\S+),);

if ($ua eq "Mozilla" && $ver >= 1.1) {
    system("echo Content-type: text/html; echo; cat /home/frogner/www/nl/adv/foyen/indexN.html");
} else {
    system ("echo Content-type: text/html; echo; cat /home/frogner/www/nl/adv/foyen/index2.html");
}
