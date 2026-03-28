#!/usr/bin/perl

# $Id: personell.pl,v 1.17 1995/03/15 07:49:01 aas Exp $

BEGIN {
   $| = 1;
   print <<EOT;
Content-Type: text/html

<head>
<title>SNs ansatte</title>
</head>

<body background="/img/snbg.gif">
EOT

   $| = 0;
}

$ME         = "/sn/a/finn.cgi";

$TOP        = "/home/steinar/frogner";
$DB         = "$TOP/sn/a/ansatte.db";
$IMAGE_PRE  = "/sn/a/img";
$IMAGE_DIR  = "$TOP$IMAGE_PRE";
$IMAGE_ICON = "/sn/a/photo.gif";

%AVD = (
   ADM     => 'Administrasjon',
   PROFF   => 'Profesjonelle tjenester',
   PRIVAT  => 'Privatmarked',
   NETT    => 'Nettverk',
   UTV     => 'Utvikling',
   SUPPORT => 'Kundeservice',
);



use CGI::Query;
use URI::Escape;

$searchexp = $query{isindex};

unless (defined $searchexp and length $searchexp) {
    form();
    sn();
    exit;
}


# Let's construct a seach routine
$code = "";
for (split(' ', $searchexp)) {
    $ignorecase = (/^[A-ZÆØÅ]+$/ ? "" : "i");
    $code .= "  /\Q$_\E/$ignorecase and\n";
}
$code = "sub found {\n$code  1;\n}\n";
$code = "sub found { 1; }\n" if $searchexp eq "ALLE";
# print $code;  # useful while debugging
eval $code;
die $@ if $@;

# Do the searching
open(DB, $DB) || die "Database not found";
@res = ();
$/ = '';   # one paragraph at a time
while (<DB>) {
    next if /^#/;
    push(@res, $_) if found();
}
close(DB);


if (!@res) {
    print "Ingen personer som tilfredstiller '$searchexp' ble funnet\n";
    form();
} 
elsif (@res > 3) {
    form();
    print "<table border=1>\n";
    print "<tr><th></th><th>Navn</th><th>Epost</th></tr>\n";
    
    $no = 0;
    for (@res) {
	print "<tr><td>", join("</td><td>", ++$no, short()), "</td></tr>\n";
    }
    print "</table>\n";
}
else {
    form();
    for (@res) {
	print full(@res < 2);
    }
}
sn();
print "<p><i><font size=-3>Oppdatert " . dbmod() . "</font></i>\n";
print "</body>\n";
exit;


sub dbmod {   # return DB modification time as a formatted string
    my($modd,$modm,$mody) = (localtime((stat($DB))[9]))[3,4,5];
    $modm++;
    $mody += 1900;
    "$modd/$modm-$mody";
}

sub form {   # print search form

    print <<EOT;
<form action="$ME">

<img src="http://www.oslonett.no/img/snikon.gif" align=right alt="">

Personsøk: <input name=isindex>
</form>
EOT
    
}

sub sn {
    print <<EOT;
<p><hr>
<b>Schibsted Nett AS</b><br>
Gjerdrumsvei 11, 0486 OSLO<br>
Postboks 1178 Sentrum, 0107 OSLO<br>
Telefon 22 02 01 10, Telefax 22 02 09 77

EOT

}


sub short {
    parse_entry($_);
    my $ref = uri_escape(lc("$E{EN}+$E{FN}"));
    $ref = "$ME?$ref";
    my $mail = "";
    if (defined $E{E}) {
	$mail = qq(<a href="mailto:$E{E}">$E{E}</a>);
    }

    (qq(<a href="$ref">$E{EN}, $E{FN}</a>), $mail);
}

sub full {   # full presentation
    my($showphoto) = shift;
    parse_entry($_);
    passwd_info();

    my @P = ();


    my($navn) = "$E{FN} $E{EN}";
    # Check to see if this person has its own home page location
    if ($E{HOME} && -d "$E{HOME}/www_docs") {
	$navn = qq(<a href="/~$E{UID}/">$navn</a>);
    }
    push(@P, "<h1>$navn");
    
    # Try to locate images
    my($img,$gif,$jpg);
    $img = "$E{FN}_$E{EN}";
    $img =~ tr/ ./__/;
    $img =~ s/_+/_/g;

    $gif = uri_escape("$IMAGE_PRE/$img.gif") if -f "$IMAGE_DIR/$img.gif";
    $jpg = uri_escape("$IMAGE_PRE/$img.jpg") if -f "$IMAGE_DIR/$img.jpg";
    $jpg = $gif unless $jpg;
    $showphoto = 0 unless $gif;

    if ($gif || $jpg) {
        push(@P,"</h1>") if $showphoto;
        $gif = $IMAGE_ICON if !$showphoto;
        push(@P, " <a href=\"$jpg\">") if $jpg && $jpg ne $gif;
        push(@P, "<img src=\"$gif\" alt=\"(Foto)\" border=0>");
        push(@P, "</a>") if $jpg && $jpg ne $gif;
        push(@P, "</h1>") if !$showphoto;
    } else {
	push(@P, "</h1>");
    }

    # Div opplysninger:
    @A = (["Navn", "$E{EN}, $E{FN}"],
	  ["Tittel", $E{TI}],
	  ["Stilling", $E{ST}],
	  ["Avdeling", $AVD{$E{AVD}} || $E{AVD}],
	 );
    if ($E{E}) {
	push(@A, ["Epost", qq(<a href="mailto:$E{E}">$E{E}</a>)]);
    }
    push(@A, ["Telefon", phone($E{KT})]);
    push(@A, ["Mobil",   phone($E{MT})]);
    if ($E{PA} || $E{PT}) {
	my $priv = "";
	$priv .= $E{PA} if defined $E{PA};
	if ($E{PT}) {
	    $priv .= ", Tel.: " if length $priv;
	    $priv .= phone($E{PT});
	}
	push(@A, ["Privat",  $priv]);
    }
    #push(@A, ["Skall", $E{SHELL}]);

    push(@P, "<table cellspacing=0 cellpadding=0>");
    for (@A) {
	next unless defined $_->[1];
	next unless length $_->[1];
	push(@P, "<tr><td><b>$_->[0]:</b></td><td>$_->[1]</td></tr>");
    }
    push(@P, "</table>");

    join("\n", @P);
}

sub parse_entry
{
    %E = ();
    for (split(/\n/, $_[0])) {
	my($key,$val) = /^(\w+)\s*:\s*(.*)/;
	next unless defined $key;
	$val =~ s/\s+$//;
	$E{$key} = $val;
    }
    $E{E} = "$E{UID}\@a.sn.no" if !$E{E} && $E{UID};
}

sub passwd_info
{
    my $uname = $E{UID};
    return unless defined $uname;
    my @a = getpwnam($uname);
    return unless @a;
    shift(@a); # don't need name
    (@E{'PASSWD','UID#', 'GID#', 'QUOTA',
        'COMMENT', 'GCOS', 'HOME', 'SHELL'}) = @a;
}

sub phone  # reformat a phone number
{
    my $in = shift;
    return undef unless defined $in;
    if ($in =~ /^[\d\s]+$/ && length($in) == 8) {
	$in =~ s/\s+//g;
	if ($in =~ /^(9\d\d)(\d\d)(\d{3})$/) {
	    $in = "$1 $2 $3";
	} elsif ($in =~ /^(\d\d)(\d\d)(\d\d)(\d\d)$/) {
	    $in = "$1 $2 $3 $4";
	}
    } elsif ($in =~ /,/) {
	# if we find a comma, then we reformat each path
	$in = join(", ", map phone($_), split(/,\s*/, $in));
    }
    $in;
}
