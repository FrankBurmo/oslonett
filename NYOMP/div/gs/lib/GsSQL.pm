package GsSQL;

# $Id: GsSQL.pm,v 1.4 1995/11/23 17:40:58 aas Exp $


=head1 NAME

sql - Send sql statements to a Sybase server

DBCOUNT - Returns number of rows affected

=head1 SYNOPSIS

 use GsSQL;
 $rows = sql("select * from foo");
 foreach (@$rows) {
    # do something
 }
 print &DBCOUNT, " rows affected.\n";

=head1 DESCRIPTION

This module provide a simplified interface to Sybase.  All you have to
do is to use this module and the you are able to send sql statements
directly.

The variable C<$TelissSQL::SQL_AS_HTML> controls whether the sql
statements executed should be printed when the program terminates.  It
is on by default.

=head1 AUTHOR

Gisle Aas <aas@oslonett.no>

=cut


require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw($db sql DBCOUNT dbsafestr);

#$SQL_AS_HTML = 1;
my @html;

use Sybase::DBlib;

dberrhandle(\&error);
dbmsghandle(\&message);

$db = Sybase::DBlib->dblogin('oslonett', 'oslonett');
dbsettime(5*60);  # set timeout

=head1 sql($cmds, [\&rowcallback])

Runs the sql command and returns the result as a reference to an array
of the rows.  Each row is a reference to an array of scalars.

If you provide a second parameter it is taken as a procedure to call
for each row.  The callback is called with the values of the row as
parameteres.

=cut

sub sql
{
    my($cmd, $sub) = @_;

    unless ($db) {
	return undef;
    }

    $db->dbcmd($cmd);
    $db->dbsqlexec;

    my @res;
    my @data;
    while($db->dbresults != NO_MORE_RESULTS) {
	while (@data = $db->dbnextrow) {
	    if (defined $sub) {
		&$sub(@data);
	    } else {
		push(@res, [@data]);
	    }
	}
    }

    remember_sql($cmd);

    \@res;  # return the result array
}

sub remember_sql
{
    if ($SQL_AS_HTML) {
	my $html = shift;
	$html =~ s/&/&amp;/g;
	$html =~ s/</&lt;/g;
	$html =~ s/>/&gt;/g;
	push(@html, $html);
    }
}

sub DBCOUNT
{
    $db->DBCOUNT;
}


sub dbsafestr
{
    "'" . $db->dbsafestr($_[0], "'") . "'";
}


sub error
{
    my($db, $severity, $dberr, $oserr, $dbmsg, $osmsg) = @_;
    print "<h3>ERROR-$dberr: $dbmsg</h3>\n";
    INT_EXIT;
}

sub message
{
    my($db, $no, $state, $severity, $text, $server, $proc, $line) = @_;
    return if $no == 5701;  # use DB
    return if $no == 5703;  # language setting
    print "<h3>$text ($no/$state/$severity)</h3>\n";
}

sub END
{
    if ($SQL_AS_HTML && @html) {
	my $html = $cmd;
	print "<p><br><br><hr width = 50% align=left>
<h3>SQL-Statements</h3><font size=-1>\n";
	print "<pre>\n";
	print join("</pre><hr size=3 width = 20% align=left noshade><pre>\n",
		   @html);
	print "</pre></font>\n";
    }
}

1;
