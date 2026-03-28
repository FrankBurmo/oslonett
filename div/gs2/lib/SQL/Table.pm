# This is a -*- perl -*- module
#
# $Id: Table.pm,v 1.15 1995/09/20 13:17:30 aas Exp $

package SQL::Table;
use Carp;


sub new
{
    my($class,$tabname) = @_;

    $tabname =~ s/\.tab$//;
    my $self = bless { name => $tabname }, $class;

    my $tabfile = $self->tabfile($tabname);
    if (!defined($tabfile) || !open(F, $tabfile)) {
	croak "Can't find table definition for $tabname";
    }

    my %field;   # hash indexed by field-name.
    my @seq;     # defines the field sequence
    my @index;   # indexes

    while (<F>) {
	s/\s*#.*//;      # remove comments
	next if /^\s*$/; # skip blank lines
	chomp;
	if (s/^\s*index\b\s*//i) {
	    push(@index, $_);
	} else {
	    my($field_no, $field, $type) = split(' ', $_, 3);
	    $type = 'varchar' unless defined $type;
	    $field{$field} = {type => $type, field_no => $field_no};
	    push(@seq, $field);
	}
    }
    close(F);
    $self->{field} = \%field;
    $self->{seq}   = \@seq;
    $self->{idx}   = \@index;
    $self;
}


sub tabfile
{
    my($self, $tabname) = @_;
    unless (defined @TAB_PATH) {
	@TAB_PATH = $self->tabpath;
    }
    for (@TAB_PATH) {
	my $f = "$_/$tabname.tab";
	return $f if -f $f;
	$f = "$_/tabname";
	return $f if -f $f;
    }
    return undef;
}

sub tabpath
{
    split(/:/, $ENV{TAB_PATH} || ".:/local/lib/tables");
}

# Some methods to extract information

sub name
{
    shift->{'name'};
}

sub fields
{
    @{shift->{'seq'}};
}

sub type
{
    my($this,$field) = @_;
    $this->{'field'}{$field}{'type'};
}

sub field_no
{
    my($this,$field) = @_;
    $this->{'field'}{$field}{'field_no'};
}


sub has_field
{
    my($this, $field) = @_;
    exists $this->{'field'}{$field}
}

sub value_as_sql
{
    my($this, $field, $val) = @_;
    my $type = $this->type($field);
    croak "No such field ($field)" unless defined $type;

    my $notnull = $type =~ /\bnot\s+null\b/;

    if ($type =~ /\bbit\b/) {
	# bit, e.g. boolean type must be 0 or 1
	if ($val =~ /^[-+]?\d+(\.\d+)?/) {
	    # nummeric
	    return ($val) ? 1 : 0;
	} else {
	    $val = lc($val);
	    return ($val eq "n" || $val eq "no" || $val eq "nil" ||
		    $val eq "null" || $val eq "false" || $val eq "")
	      ? 0 : 1;
	}
    } elsif ($type !~ /\b(tiny|small)?(int|numeric|real|float|money)\b/) {
	# not a numeric type, i.e. a string value, quote it
	unless (defined $val) {
	    return $notnull ? "''" : "null";
	}
	$val =~ s/'/''/g;  #';  # double single quotes
	return "'$val'";
    } else {
	# numeric type
	unless (defined $val) {
	    return $notnull ? 0 : "null";
	}
    	return $val + 0;
    }
}

# Some methods that creates SQL statements on the table

sub sql_insert
{
    my($this, %hash) = @_;
    # foreach(keys %hash) { print "$_: $hash{$_}\n"; }
    my $tablename = $this->name;
    my @fields = ();
    my @values = ();
    foreach $field (@{$this->{'seq'}}) {
	next unless exists $hash{$field};
	my $value = $this->value_as_sql($field, $hash{$field});
	delete $hash{$field};
	next if $value eq "null";
	push(@fields, $field);
	push(@values, $value);
    }

    # Make warnings for remaining fields
    for $field (keys %hash) {
	warn "No place for $field in $tablename\n";
    }

    my @sql;
    if (@fields) {
	push(@sql, "INSERT INTO $tablename");
	push(@sql, "  (" . join(", ", @fields) . ")");
	push(@sql, "VALUES");
	push(@sql, "  (" . join(", ", @values) . ")");
    } else {
	warn "Nothing to insert";
    }
    join("\n", @sql, "")
}

sub sql_update
{
    my($this, $where, %hash) = @_;
    my $tablename = $this->name;
    my @fields = ();
    my @values = ();
    foreach $field (@{$this->{'seq'}}) {
	next unless exists $hash{$field};
	push(@fields, $field);
	push(@values, $this->value_as_sql($field, $hash{$field}));
	delete $hash{$field};
    }

    # Make warnings for remaining fields
    for $field (keys %hash) {
	warn "No place for $field in $tablename\n";
    }

    my @sql;
    if (@fields) {
	push(@sql, "UPDATE $tablename");
	push(@sql, "SET");
	my($field,$value);
	my(@lines);
	while (($field,$value) = (shift(@fields), shift(@values))) {
	    push(@lines, "  $field = $value");
	}
	push(@sql, join(",\n", @lines));
	push(@sql, "WHERE $where");
    } else {
	warn "Nothing to update";
    }
    join("\n", @sql, "");
}

sub sql_delete
{
    my($this, $where) = @_;
    "DELETE FROM $this->{'name'} WHERE $where\n";
}

sub sql_drop
{
    my($this) = @_;
    "DROP TABLE $this->{'name'}\n";
}

sub sql_create
{
    # output sql statements to create the table.
    my($this) = @_;
    my @lines;
    for $field (@{$this->{'seq'}}) {
	my $type = $this->{'field'}{$field}{'type'};
	$type =~ s/^(\S+)/$1 null/
	  unless $type =~ /\bnull\b/
	      || $type =~ /\bkey\b/
	      || $type =~ /\bbit\b/
	      || $type =~ /\bidentity\b/
	      || $type =~ /\breferences\b/;
	$type =~ s/\bvarchar\s+/varchar(255) /;
	push(@lines, "  $field " . (" " x (10 - length $field)) . $type);
    }
    "CREATE TABLE $this->{'name'} (\n" . join(",\n", @lines) . "\n)\n";
}

sub sql_create_index
{
    my($this) = @_;
    my $tab = $this->{'name'};
    my $i = 1;
    my $sql = "";
    for (@{$this->{idx}}) {
	my $idxkind = "";
	if (s/\[([^\]]+)]//) {   # remove initial string in [brackets]
	    $idxkind = $1;
	    $idxkind .= " " unless $idxkind =~ /\s+$/;
	}
	$sql .= "CREATE ${idxkind}INDEX i" . $i++ . " ON $tab(";
	$sql .= join(", ", split(' ', $_));
	$sql .= ")\n";
    }
    $sql;
}

sub sql_drop_index
{
    my($this) = @_;
    my $tab = $this->{'name'};
    my $i = 1;
    my @idx = map { "$tab.i" . $i++ } @{$this->{idx}};
    return "" unless @idx;
    "DROP INDEX " . join(", ", @idx) . "\n";
}


1;
