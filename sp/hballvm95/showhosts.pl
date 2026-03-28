#!/local/bin/perl5

dbmopen(%a, 'karantene', 0644) || die;
while (($k,$v) = each %a) {
   $host = `nslookup $k | grep Name`;
   print "$k\t$host";
}
dbmclose(%a);
exit 0;
