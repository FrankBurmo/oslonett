#!/local/bin/perl

$LOGGFILE =	'/home/hasle/g/kgn/tmp/irc/log.txt';
$NICKNAME =	'sn1';
$SERVER =	'irc.ifi.uio.no';
$PORT =		6667;
$CHANNEL =	'#norge';
$SKIPINFO =	1;		# don't show join/leave messages

$SIG{INT} = inthandler;
open(LOG, ">$LOGGFILE") || die;
open(IRC, "irc -d -p $PORT -c $CHANNEL $NICKNAME $SERVER |");

$|=1;
select(IRC);$|=1;select(STDOUT);
$start = `date`;
chop $start;
print LOG <<EOT;
New IRC log started:	$start
Logging channel:	$CHANNEL
Listeners nicname:	$NICKNAME
Server:			$SERVER
Port:			$PORT

EOT


while (<IRC>) { 
    print LOG $_;
    # gjør HTML formattering her.
    print unless /^\*\*\*/;
}

$stop = `date`;
print LOG "\n\nIRC log ended $stop\n";
close LOG;
close IRC;

exit 0;

sub inthandler {
    $stop = `date`;
    print LOG "\n\nIRC log interrupted by SIGINT, $stop\n";
    close LOG;
    close IRC;
    exit 0;
}
