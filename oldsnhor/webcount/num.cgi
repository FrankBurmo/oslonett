#!/usr/local/bin/perl5

# $Id: num.cgi,v 1.3 1995/09/11 08:50:16 aas Exp $
# Author: Gisle Aas, Oslonett AS

$PBMBIN  = "/local/pbm/bin";            # where is pbm programs installed
$IMGDIR  = "/local/www/webcount";  # where is digit images stored
$DBDIR   = $IMGDIR;                     # where counter database is stored
$COUNTDB = "$DBDIR/counters";

$DEBUG   = 0;

{
    local($|) = 1;
    $ct = $DEBUG ? "text/plain" : "image/gif";
    print "Content-Type: $ct\n\n";
}

sub run
{
    if ($DEBUG) {
	print "@_\n";
	return;
    }
    system @_;
}


$no = $ENV{PATH_INFO};

if (defined $no) {
    $no =~ s,^/,,;
    $no =~ s,;(.*),,;
    for (split(';', $1)) {
	($key,$val) = split(/=/, $_, 2);
	$param{$key} = $val;
    }
}

if ($no =~ /^rand\((\d+)\)$/) {
    srand(time || $$);
    $no = int(rand($1));
    $no_cache = 1 if $1 > 100;
} elsif ($no =~ /^counter\(([^\)]+)\)(?:=(\d+))?$/) {
    $id = $1;
    $setvalue = $2;
    
    require Fcntl;
    $lockfile = "$COUNTDB.lck";
    open(LOCK, ">$lockfile") or die "Can't open $lockfile: $!";
    flock(LOCK, &Fcntl::F_WRLCK) or die "Can't flock: $!";  # 2 = exlusive lock

    require NDBM_File;
    tie %counter, NDBM_File, $COUNTDB, &Fcntl::O_RDWR|&Fcntl::O_CREAT, 0664;

    ($no, $time) = split(';', $counter{$id});
    if (defined $setvalue) {
	$no = $setvalue;
    } else {
	$no++;
    }
    $counter{$id} = $no . ";" . time;

    untie %counter;
    close(LOCK);
    $no_cache = 1 if $no > 100;
}

%filemap =
(
 ' ' => 'space',
 ',' => 'comma',
 '.' => 'period',
 '+' => 'plus',
 '-' => 'minus',
);
for (0..9) { $filemap{$_} = $_; }

$no =~ tr/0-9 ,.+-//cd;

$pad = "0";
if (defined $param{'pad'}) {
    $tmp = $param{'pad'};
    $pad = ' ' if $tmp eq " " || $tmp eq "_";
}

if (defined $param{'w'}) {
    $width = int($param{'w'});
    $width = 30 if $width > 30;
    $no = ($pad x ($width - length $no)) . $no;
}
$no = $pad unless length $no;

%known_styles = (grotesk => 1, big => 1, std => 1);
$style = $param{'style'};
$style = 'std' unless exists $known_styles{$style};

chdir $IMGDIR;

$cache = "cache/$style-$no.gif";
$cache =~ tr/ /_/;

if (open(CACHE, $cache)) {
    while (read(CACHE, $cache, 4096)) {
	print STDOUT $cache;
    }
    exit;
}

# Must generate new number
@files = map { "'$style-$filemap{$_}.pgm'" } split(//, $no);

unless ($no_cache) {
    run "$PBMBIN/pnmcat -lr @files | $PBMBIN/ppmtogif 2>/dev/null | tee $cache";
} else {
    run "$PBMBIN/pnmcat -lr @files | $PBMBIN/ppmtogif 2>/dev/null";
}
