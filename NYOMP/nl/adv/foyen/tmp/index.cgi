#!/local/bin/perl

($ua, $ver) = ($ENV{HTTP_USER_AGENT} =~ m,([^/]+)/(\S+),);

if ($ua eq "Mozilla" && $ver >= 1.1) {
    system("echo Content-type: text/html; echo; cat /home/frogner/www/nl/adv/foyen/tmp/indexn.htm");
} else {
    system ("echo Content-type: text/html; echo; cat /home/frogner/www/nl/adv/foyen/tmp/index2.htm");
}
