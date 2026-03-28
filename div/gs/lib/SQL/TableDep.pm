# This is a -*- perl -*- module
#
# $Id: TableDep.pm,v 1.3 1995/08/29 10:35:07 aas Exp $

package SQL::TableDep;

use Carp;

$TABDIR = "." unless defined $TABDIR;


# The following code tries to deduce the right sequence of tables
# based on dependensies found in tables.dep.  I don't know why it had 
# to be so complex...

my %depseq = ();  # sort sequence based on dependencies
my %tab =    ();  # record tables involving dependensies
my %dep =    ();  # dependensies
my %dep2 =   ();  # dependensies in keys
my @dep =    ();  # used to collect sequence
my %seen =   ();  # used to check for circular dependensies

if (open(TABDEP, "$TABDIR/tables.dep")) {
    warn "Parsing $TABDIR/tables.dep...\n";
    my($tab, @tab, $dep);
    while (<TABDEP>) {
	next if /^\s*#/;
	next if /^\s*$/;
	($tab, $dep) = split(/=>/, $_, 2);
	foreach $tab (split(' ', $tab)) {
	    foreach $dep (split(' ', $dep)) {
		push(@{$dep{$tab}}, $dep);
		$dep2{"$tab;$dep"} = 1;
		$tab{$tab} = 1;
		$tab{$dep} = 1;
	    }
	}
    }
    close(TABDEP);
    
    # check for circulay dependencies
    foreach $tab (keys %dep) {
        foreach (@{$dep{$tab}}) {
	    %seen = ();
	    $dep2{"$tab;$_"} = 1;
	    _traverse_dep($tab, $_);
	}
    }
} else {
    die "Can't open $TABDIR/tables.dep: $!\n";
}

# create sequene.  The basic strategy is to first remove those tables
# that are not dependency targes.  Then we remove all dependencyes involving
# these and continue until there are no more tables left.
my @dep = ();
while (keys %tab) {
    #@tab = keys %tab; print "@tab\n";
    my %deptarget = ();
    my %nodep = ();
    for (keys %dep2) {
	($tab,$dep) = split(/;/, $_, 2);
	$deptarget{$dep} = 1;
    }
    for (keys %tab) {
	next if $deptarget{$_};
	$nodep{$_} = 1;
	delete $tab{$_};
    }
    for (keys %dep2) {
	($tab,$dep) = split(/;/, $_, 2);
	delete $dep2{$_} if $nodep{$tab};
    }
    push(@dep, sort keys %nodep);
}

my $i = 0;
for (@dep) {
    $depseq{$_} = $i++;
}
#print STDERR "SEQ: @dep\n";
undef(%seen);
undef(%dep2);
undef(%dep);
undef(%tab);
undef(@dep);
undef($i);

# only %depseq is needed for sorting in cmp_tables()


# This routine is only used to check circular dependencies
sub _traverse_dep
{
    my($tab,$dep) = @_;
    #print STDERR "dep($tab,$dep)\n";
    die "circular dependecy $tab => $dep\n" if $seen{$dep}++;
    for (@{$dep{$dep}}) {
	_traverse_dep($tab, $_);
    }
}

# Sort tables based on dependencies.  Tables should be created in this
# sequence.  Tables should be droped in the opposite sequence.

sub cmp_tables
{
    $depseq{$a} = 9999 unless defined $depseq{$a};
    $depseq{$b} = 9999 unless defined $depseq{$b};
    $depseq{$b} <=> $depseq{$a} || $a cmp $b;
}


sub sort_tables
{
    sort cmp_tables @_;
}

# Enough of this dependency rubbish...

1;
