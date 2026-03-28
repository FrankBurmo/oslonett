#!/local/bin/perl

$LOCK_EX = 2;
$LOCK_UN = 8;


open(LOCK, ">foo.bar") || &err("Failed to open");

print "Trying to lock files\n";
$SIG{'ALRM'} = 'timeout';	# call subroutine timeout if alarm occurs
alarm 10;			# seconds til timeout/alarm
flock(LOCK, $LOCK_EX) || &err("Failed to lock"); # try to lock in
$SIG{'ALRM'} = 'IGNORE';	# ignore any alarm signals
alarm 0;			# cancel alarm

print "File is locked - press enter to unlock: ";
$foo = <>;

flock(LOCK, $LOCK_UN) || &err("Failed to unlock");
print "File unlocked\n";
close(LOCK) || &err("Failed to close");	# unlock
print "File closed\n";
exit;

sub err {
    print "error: $_[0]\n";
}

sub timeout {
    print "timeout - files are locked\n";
    flock(LOCK, $LOCK_UN);
    close LOCK;
    exit 1;
}
