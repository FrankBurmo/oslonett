#!/local/bin/perl
#
# CHANGE THE TOP LINE TO POINT TO PERL ON YOUR SYSTEM AS '#!<perl_path>'
#
##########################
## guestbook v2.20
##########################
## This script is called by the user with the appropriate Q_STRING
## that includes their login name, guest page path, and desired return page.
## It creates the forms page necessary for input POST portion of the script,
## which actually adds the guest to the noted guest page.
##
## The login name can be 'special' (see below), or a user in the passwd/NIS
## domain of the server.  A special user has the relative path listed, while
## passwd/NIS users must have their own public_html (or equivalent) directory
## and be readable/writeable by whatever group/user the http server is run as
## (this generally means world readable/writeable).
##
## The first thing you probably should change in these scripts is the
## path to the PERL executable.
##
## Thanks to tank@amoco.com (Jon A. Tankersley) for helping in the upgrade.
##########################
#
# QUERY_STRING should be of the form:
# [http://domain]/scriptname?owner!guestpage[!returnpage]
# where [...] are optional, depending on the configuration.
#
# For more help on this, you can read the auto-generated help script at
# http://www.cs.uoregon.edu/cgi-bin/guestbook2
#
# This same help file will be output by your guestbook script when it is
# properly placed in a script directory and accessed with no arguments

##########################
# EDITABLE PARAMETERS
# Some of these lines may need to be changed.
#
# For Perl5 the '@'s NEED TO BE ESCAPED as shown (with a backslash).
# Perl4 doesn't care either way.

## domain of your WWW server, as 'http://<domain>'
$wwwroot = "http://www.sn.no";

## domain name for email addresses
$domain = "\@oslonett.no";

## mail program that is opened with a pipe
## To:, From: & Subject: are printed to this pipe
$mailprog   = "/usr/lib/sendmail -t -oi -oem";

## name of directory inside user's home directory which holds a
## user's HTML pages.  Usually 'public_html'
$public_html = "www_docs";

## You can specify special users (those that do not have a login account).
## You specify a special key name to use a different directory as the root
## for the user's HTML pages.  The format is 'NAME, DIRECTORY' in tuples,
## where DIRECTORY is the root directory of NAME's pages.  'specialUserEmail'
## is used to specify an email address for special users since they probably
## aren't regular UNIX names.  These will also override normal usernames.

%specialUser = (
        "root", "/home/frogner/www",
        "www", "/home/frogner/www",
                );

%specialUserEmail = (
        "root", "webmaster$domain",
        "www", "webmaster$domain",
                     );

# END OF EDITABLE PARAMETERS
# YOU SHOULD NOT NEED TO EDIT ANYTHING BEYOND THIS POINT
##########################

# Information about the author
$authorurl = "http://www.cs.uoregon.edu/~jhobbs";
$author    = "jhobbs\@cs.uoregon.edu";

if (defined $ENV{SCRIPT_NAME}) {
    $scriptname = $ENV{SCRIPT_NAME};
} else {
    $scriptname = '/cgi-bin/guestbook.pl';
}

# This gets the necessary info from the QUERY_STRING, if any
#
($owner, $guestpage, $returnpage) = split('!', $ENV{QUERY_STRING});

# If not enough info was in the QUERY_STRING, it returns the help page
#
&Help() unless ($owner && $guestpage);

if ($ENV{'REQUEST_METHOD'} eq 'GET') {

    # This associative array relates the last internet domain segment
    # to the most probable country of origin
    %countryid = ('edu', 'USA', 'org', 'USA', 'com', 'USA', 'net', 'USA',
              'gov', 'USA', 'mil', 'USA', 'us', 'USA', 'um', 'USA',
              'af', 'Afghanistan',            'al', 'Albania',
              'dz', 'Algeria',                'as', 'American Samoa',
              'ad', 'Andorra',                'ao', 'Angola',
              'ai', 'Anguilla',               'aq', 'Antarctica',
              'ag', 'Antigua and Barbuda',    'ar', 'Argentina',
              'am', 'Armenia',                'aw', 'Aruba',
              'au', 'Australia',              'at', 'Austria',
              'az', 'Azerbaijan',             'bs', 'Bahamas',
              'bh', 'Bahrain',                'bd', 'Bangladesh',
              'bb', 'Barbados',               'by', 'Belarus',
              'be', 'Belgium',                'bz', 'Belize',
              'bj', 'Benin',                  'bm', 'Bermuda',
              'bt', 'Bhutan',                 'bo', 'Bolivia',
              'ba', 'Bosnia and Herzegowina', 'bw', 'Botswana',
              'bv', 'Bouvet Island',          'br', 'Brazil',
              'io', 'British Indian Ocean Territory',
              'bn', 'Brunei Darussalam',      'bg', 'Bulgaria',
              'bf', 'Burkina Faso',           'bi', 'Burundi',
              'kh', 'Cambodia',               'cm', 'Cameroon',
              'ca', 'Canada',                 'cv', 'Cape Verde',
              'ky', 'Cayman Islands',         'cf', 'Central African Republic',
              'td', 'Chad',                   'cl', 'Chile',
              'cn', 'China',                  'cx', 'Christmas Island',
              'cc', 'Cocos (Keeling) Islands',
              'co', 'Colombia',               'km', 'Comoros',
              'cg', 'Congo',                  'ck', 'Cook Islands',
              'cr', 'Costa Rica',             'ci', 'Cote d\'Ivoire',
              'hr', 'Croatia (Hrvatska)',     'cu', 'Cuba',
              'cy', 'Cyprus',                 'cz', 'Czech Republic',
              'dk', 'Denmark',                'dj', 'Djibouti',
              'dm', 'Dominica',               'do', 'Dominican Republic',
              'tp', 'East Timor',             'ec', 'Ecuador',
              'eg', 'Egypt',                  'sv', 'El Salvador',
              'gq', 'Equatorial Guinea',      'er', 'Eritrea',
              'ee', 'Estonia',                'et', 'Ethiopia',
              'fk', 'Falkland Islands',       'fo', 'Faroe Islands',
              'fj', 'Fiji',                   'fi', 'Finland',
              'fr', 'France',                 'fx', 'France,',
              'gf', 'French Guiana',          'pf', 'French Polynesia',
              'tf', 'French Southern Territories',
              'ga', 'Gabon',                  'gm', 'Gambia',
              'ge', 'Georgia',                'de', 'Germany',
              'gh', 'Ghana',                  'gi', 'Gibraltar',
              'gr', 'Greece',                 'gl', 'Greenland',
              'gd', 'Grenada',                'gp', 'Guadeloupe',
              'gu', 'Guam',                   'gt', 'Guatemala',
              'gn', 'Guinea',                 'gw', 'Guinea-Bissau',
              'gy', 'Guyana',                 'ht', 'Haiti',
              'hm', 'Heard and McDonald Islands',
              'hn', 'Honduras',               'hk', 'Hong Kong',
              'hu', 'Hungary',                'is', 'Iceland',
              'in', 'India',                  'id', 'Indonesia',
              'ir', 'Iran',                   'iq', 'Iraq',
              'ie', 'Ireland',                'il', 'Israel',
              'it', 'Italy',                  'jm', 'Jamaica',
              'jp', 'Japan',                  'jo', 'Jordan',
              'kz', 'Kazakhstan',             'ke', 'Kenya',
              'ki', 'Kiribati',
              'kp', 'Democratic People\'s Republic of Korea',
              'kr', 'Republic of Korea',      'kw', 'Kuwait',
              'kg', 'Kyrgyzstan',             'la', 'Lao Democratic Republic',
              'lv', 'Latvia',                 'lb', 'Lebanon',
              'ls', 'Lesotho',                'lr', 'Liberia',
              'ly', 'Libya',                  'li', 'Liechtenstein',
              'lt', 'Lithuania',              'lu', 'Luxembourg',
              'mo', 'Macau',                  'mk', 'Macedonia,',
              'mg', 'Madagascar',             'mw', 'Malawi',
              'my', 'Malaysia',               'mv', 'Maldives',
              'ml', 'Mali',                   'mt', 'Malta',
              'mh', 'Marshall Islands',       'mq', 'Martinique',
              'mr', 'Mauritania',             'mu', 'Mauritius',
              'yt', 'Mayotte',                'mx', 'Mexico',
              'fm', 'Micronesia',             'md', 'Moldova',
              'mc', 'Monaco',                 'mn', 'Mongolia',
              'ms', 'Montserrat',             'ma', 'Morocco',
              'mz', 'Mozambique',             'mm', 'Myanmar',
              'na', 'Namibia',                'nr', 'Nauru',
              'np', 'Nepal',                  'nl', 'Netherlands',
              'an', 'Netherlands Antilles',   'nc', 'New Caledonia',
              'nz', 'New Zealand',            'ni', 'Nicaragua',
              'ne', 'Niger',                  'ng', 'Nigeria',
              'nu', 'Niue',                   'nf', 'Norfolk Island',
              'mp', 'Northern Mariana Islands',
              'no', 'Norway',                 'om', 'Oman',
              'pk', 'Pakistan',               'pw', 'Palau',
              'pa', 'Panama',                 'pg', 'Papua New Guinea',
              'py', 'Paraguay',               'pe', 'Peru',
              'ph', 'Philippines',            'pn', 'Pitcairn',
              'pl', 'Poland',                 'pt', 'Portugal',
              'pr', 'Puerto Rico',            'qa', 'Qatar',
              're', 'Reunion',                'ro', 'Romania',
              'ru', 'Russian Federation',     'rw', 'Rwanda',
              'kn', 'Saint Kitts and Nevis',  'lc', 'Saint Lucia',
              'vc', 'Saint Vincent and the Grenadines',
              'ws', 'Samoa',                  'sm', 'San Marino',
              'st', 'Sao Tome and Principe',  'sa', 'Saudi Arabia',
              'sn', 'Senegal',                'sc', 'Seychelles',
              'sl', 'Sierra Leone',           'sg', 'Singapore',
              'sk', 'Slovakia',               'si', 'Slovenia',
              'sb', 'Solomon Islands',        'so', 'Somalia',
              'za', 'South Africa',           'gs', 'South Georgia',
              'es', 'Spain',                  'lk', 'Sri Lanka',
              'sh', 'St. Helena',             'pm', 'St. Pierre and Miquelon',
              'sd', 'Sudan',                  'sr', 'Suriname',
              'sj', 'Svalbard and Jan Mayen Islands',
              'sz', 'Swaziland',              'se', 'Sweden',
              'ch', 'Switzerland',            'sy', 'Syria',
              'tw', 'Taiwan',                 'tj', 'Tajikistan',
              'tz', 'Tanzania',               'th', 'Thailand',
              'tg', 'Togo',                   'tk', 'Tokelau',
              'to', 'Tonga',                  'tt', 'Trinidad and Tobago',
              'tn', 'Tunisia',                'tr', 'Turkey',
              'tm', 'Turkmenistan',           'tc', 'Turks and Caicos Islands',
              'tv', 'Tuvalu',                 'ug', 'Uganda',
              'ua', 'Ukraine',                'ae', 'United Arab Emirates',
              'gb', 'United Kingdom',         'uk', 'United Kingdom',
              'uy', 'Uruguay',                'uz', 'Uzbekistan',
              'vu', 'Vanuatu',                'va', 'Vatican City',
              've', 'Venezuela',              'vn', 'Viet Name',
              'vg', 'British Virgin Islands', 'vi', 'US Virgin Islands',
              'wf', 'Wallis and Futina Islands',
              'eh', 'Western Sahara',         'ye', 'Yemen',
              'yu', 'Yugoslavia',             'zr', 'Zaire',
              'zm', 'Zambia',                 'zw', 'Zimbabwe',
              );

    if (defined $specialUser{$owner}) {
        $dir        = $specialUser{$owner};
        $htmlpage   = "$wwwroot/$guestpage";
        if (defined $specialUserEmail{$owner}) {
            $address    = $specialUserEmail{$owner};
        } else {
            $address    = "$owner$domain";
        }
    }
    else {
        $dir = (getpwnam($owner))[7];
        if (!$dir) {
            die "Content-type: text/plain\n\n$owner is not a valid user, stoppe
d";
        }
        $htmlpage   = "$wwwroot/~$owner/$guestpage";
        $address    = "$owner$domain";
    }

    @tmp = split(/\./, $ENV{REMOTE_HOST});
    $country = $tmp[$#tmp];
    $country =~ tr/A-Z/a-z/;
    $country = $countryid{$country};

    print <<GUESTPAGE;
Content-type: text/html

<HTML>
<HEAD><TITLE>$owner\'s gjestebok</TITLE></HEAD>

<BODY bgcolor="#ffffff">
<H2>Welcome to the guest book registry.</H2>

All the information below is optional, except for your name :^).  Please
note that all names registered in the guest book are viewable by anyone.
You can alternatively just <A HREF="mailto:$address">send mail</A>
or look at the <A HREF="$scriptname">help</A>.
<P>
<B>Thanks for stopping by!</B>

<HR>
<FORM METHOD="POST" ACTION="$scriptname?$ENV{QUERY_STRING}">
<PRE>
      Name: <INPUT TYPE="text" SIZE=44 NAME="name" VALUE="$ENV{REMOTE_IDENT}">
City/State: <INPUT TYPE="text" SIZE=24 NAME="from"> Country: <INPUT TYPE="text"
SIZE=8 NAME="country" VALUE="$country">
     Email: <INPUT TYPE="text" SIZE=44 NAME="email"
VALUE="$ENV{REMOTE_IDENT}\@$ENV{REMOTE_HOST}">

Home/Favorite HTML Page (form: http://host.domain/page):
<INPUT TYPE="text" SIZE=56 NAME="html" value="http://">
 Page name: <INPUT TYPE="text" SIZE=44 NAME="pname">

Leave a note for all to see (will be shown in &lt;PRE&gt; tags):
<TEXTAREA NAME="note" ROWS=3 COLS=55></TEXTAREA>

Leave a private note (only seen by $address):
<TEXTAREA NAME="comment" ROWS=3 COLS=55></TEXTAREA>
            <INPUT TYPE="submit" VALUE="Sign Guestbook">           <INPUT
TYPE="reset" VALUE="Clear Form">
</PRE>
</FORM>

<HR>
<P align=center><A HREF="$htmlpage"><B>View the guest book</B></A></P>
<HR>
The scripts for this guest book are written in Perl and available upon request
from <A HREF="$authorurl">$author</A>.
<P><ADDRESS>$address</ADDRESS>
</BODY>
</HTML>

GUESTPAGE

} elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {

    ###############################
    ## addguest
    ################################
    ## This script, denoted "addguest", is called by submitting an entry
    ## from the guestbook page.  This script mails the owner that a person has
    ## signed the guest book, unless no name is specified, in which case an
    ## error page is shown to the guest.  Otherwise the guest gets a thank you
    ## page with a pointer to his name in the guestbook, the guestbook itself,
    ## and the return page specified.
    ################################
    #
    # keys: name, from, email, html, pname, note, comment

    if (defined $specialUser{$owner}) {
        $dir        = $specialUser{$owner};
        $returnpage = "$wwwroot/$returnpage";
        $htmlpage   = "$wwwroot/$guestpage";
        $guestpage  = "$dir/$guestpage";
        if (defined $specialUserEmail{$owner}) {
            $address    = $specialUserEmail{$owner};
        } else {
            $address    = "$owner$domain";
        }
    }
    else {
        $dir = (getpwnam($owner))[7];
        if (!$dir) {
            die "Content-type: text/plain\n\n$owner is not a valid user, stoppe
d";
        }
        $returnpage = "$wwwroot/~$owner/$returnpage";
        $htmlpage   = "$wwwroot/~$owner/$guestpage";
        $guestpage  = "$dir/$public_html/$guestpage";
        $address    = "$owner$domain";
    }

    $date = `date`;
    chop $date;

    # Get info from form and parse it
    read(STDIN, $raw_data, $ENV{CONTENT_LENGTH});

    $items = split('&', $raw_data);
    for ($i = 0; $i < $items; $i++) {
        ($key,$value) = split('=', $_[$i]);
        $value =~ tr/+/ /;
        $value =~ s/%(..)/pack("C", hex($1))/eg;
        $data{"$key"} = $value;
    }
    $rname = $data{name};
    $rname =~ tr/ /+/;
    $rname =~ tr/[A-Z]/[a-z]/;

    if ($data{name}) {
    if (!$data{pname}) { $data{pname} = $data{html}; }

    open(GUESTS, ">> $guestpage") ||
        die "Content-type: text/plain\n\nCan't open guest book $guestpage: $!\n
";
    print GUESTS "<HR>\n";
    print GUESTS "<A NAME=\"$rname\"><B>$data{name}</B></A><BR>\n";
    print GUESTS "$data{from}\t" if $data{from};
    print GUESTS "$data{country}" if $data{country};
    print GUESTS "<BR>\n";
    print GUESTS "<I>$data{email}</I><BR>\n"           if $data{email};
    if ($data{html} ne "http://") {
        print GUESTS "<A HREF=\"$data{html}\">$data{pname}</A><BR>\n";
    }
    print GUESTS "<PRE>$data{note}</PRE>\n"         if $data{note};
    print GUESTS "Signed on: $date<BR>\n\n";
    close(GUESTS);

    print <<NEWPAGE;
Content-type: text/html

<HTML>
<HEAD><TITLE>Thank You</TITLE></HEAD>
<BODY>
<H3>Thank you $data{name}.</H3>

Feel free to view <A HREF="$htmlpage#$rname">your entry</A> in the
<A HREF="$htmlpage">guest book</A> or <A HREF="$returnpage">return to
$returnpage</A>. <P>
<A HREF="$scriptname">Help</A><P>

<HR>
<ADDRESS><A HREF="mailto:$address">$address</A></ADDRESS></BODY>
</HTML>

NEWPAGE

    open(MAIL, "| $mailprog") ||
        die "Content-type: text/plain\n\nCan't open mailprog $mailprog, stopped
";
    print MAIL <<"STOP";
To: $address
From: $data{email}
Subject: $data{name} signed guest book
Precedence: junk

\tName:\t$data{name}
\tFrom:\t$data{from}, $data{country}
\tHREF:\t$data{html}, $data{pname}
\tEmail:\t$data{email}
\tHost:\t$ENV{REMOTE_HOST}
\tPage signed: $htmlpage

\tNote:
$data{note}

\tComment:
$data{comment}
STOP
    close(MAIL) || die "Content-type: text/plain\n\npipe exited $?";
    }
    else {
        print <<NEWPAGE;
Content-type: text/html

<HTML>
<HEAD><TITLE>Oops...</TITLE></HEAD>
<BODY>
<H3>Oops...</H3>

You did not specify your name.  If you would like to submit
an entry, please specify your name. <P>Thank you.<P>

<HR>
<ADDRESS><A HREF="mailto:$address">$address</A></ADDRESS></BODY>
</HTML>

NEWPAGE
    }
}

sub Help {

    print <<HELPPAGE;
Content-type: text/html

<HTML>
<HEAD>
<TITLE>GuestBook help information</TITLE>
</HEAD>

<BODY>
<A HREF="#EndUser">Web Roamer Usage</A> of the guest book form.<BR>
<A HREF="#Invocation">Invocation</A> of the guest book script.<BR>
<A HREF="#Other">Other</A> information.<BR>
<P>
<HR>

<H3><A NAME="EndUser">Usage</A></H3>

All information in the guest book form beyond your name is optional.  The
country name is best-guessed by checking your remote host's domain name.
This domain name is also placed in the email field.
<P>
<P>
Everything except the 'private note' will be viewable on the guestpage.
<P>
<HR>

<H3><A NAME="Invocation">Invocation</A></H3>
To invoke the script, make the following HREF link:
(information in []'s is optional)
<PRE>
[http://domain]$scriptname?owner!guestpage[!returnpage]
</PRE>
<P>

<UL>
<LI><I>$scriptname</I> is the path to the <A
HREF="$authorurl/guestbook">guest book script</A>, and may vary from server
to server.  The script must be placed in a valid script directory (ask you
webmaster for details).  If, when accessing the script, you are receiving
the script code back instead of the guest book form, it means that the
script is not in a valid script directory.
 <P>
<LI>The ? and ! are required syntax for this script to function properly.
 <P>
<LI><I>owner</I> toggles how the script functions, and can be one of the
following:
    <UL>
    <LI><i>username</i><BR>
        A valid UNIX username for the system.  This makes the
        guestpage/returnpage relative to ~username/$public_html.
    <LI><i>http</i> or <i>root</i> (not the superuser)<BR>
        Makes guestpage/returnpage relative to the WWW server's root directory
        (\$wwwroot = $wwwroot).
    <LI>special user name listed in the script<BR>
        Makes the guestpage/returnpage relative to the special user's directory
        as listed in the script.  This allows for non-UNIX usernames to be
        used for guest books.
    </UL>
 <P>

<LI><I>guestpage</I> is the HTML file where the guestbook script will append
input from the guestbook form.  This file MUST already exist and be writable
by the WWW server (which usually means world writable, e.g.
<CODE>-rw-rw-rw-</CODE>).  The file should probably start out something
like:

<PRE>   &lt;HTML&gt;
        &lt;HEAD&gt;
        &lt;TITLE&gt;My Guestbook Title&lt;/TITLE&gt;
        &lt;/HEAD&gt;
        
        &lt;BODY&gt;
        &lt;H1&gt;Welcome to My Guestbook&lt;/H1&gt;
        &lt;HR&gt;</PRE>
 <P>

<LI><I>returnpage</I> is an HTML page that will be referenced after the user
signs in as a return point.  It is based of the user's home page (or special
user's root page) and defaults to the user's home page if nothing is
specified.
</UL>
 <P>
<HR>

<H3><A NAME="Other">Other information</A></H3>
Feel free to obtain the <A HREF="$authorurl/guestbook">latest source
code</A> for your own use, or <A HREF="mailto:$author">mail the author</A>
any feedback/suggestions about the script.
 <P>
<ADDRESS><A HREF="$authorurl">$author</A></ADDRESS>
</BODY>
</HTML>
HELPPAGE
    exit;
}

