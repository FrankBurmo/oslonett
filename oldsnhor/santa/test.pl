#!/usr/local/bin/perl5 -w

use Sybase::DBlib qw(dbsettime);

$db = Sybase::DBlib->dblogin('psaadm', 'goldfinger');

$db->sql("select uname from uname where uname like 'aas%'",
	 sub { print "Out $word: @_\n"; });
