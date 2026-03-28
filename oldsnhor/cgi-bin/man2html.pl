#!/local/bin/perl
#
# bbc_man2html v0.4.1 by Brooks Cutter (bcutter@paradyne.com)
#
# This program allows you view man pages through a World Wide Web
# server like NCSA's httpd..  It works either as a CGI gateway or
# using NCSA httpd's older htbin (OldScriptAlias) interface.
# This program uses the <isindex> tag to get user input (and not forms)
#
# Features:
# - Supports use of RosettaMan for formatting Man pages on SunOS 4.1,
#   Solaris 2, and HP/UX 9.0
# - Will format man pages without RosettaMan on SunOS 4.1, and Solaris 2
# - Security conscious - checks pathnames against list of pathname prefices
#   and list of regular expressions to allow access.  Catches '..'
# - Supports compressed man pages including gzip'd (via gnu's zcat if avail)
#
# Installation:
#
# You will need a HTTPD program that supports CGI gateways.
# I recommend NCSA's httpd (ftp.ncsa.uiuc.edu:/Web/ncsa_httpd)
# (I believe (but don't know) that plexus also supports CGI)
#
# This program attempts to determine what it needs to know at run time
# about your environment, but you may need to tweak it...
# Variables to look at:
#
# $man2html_url - the URL of this script
# (default: `hostname` and/or `domainname`)
#
# @manpath - Just like MANPATH except comma seperated and 'quoted'
# @manregex - List of regular expressions to match against
#             (useful if you install packages in their own directories)
#
# $rosetta - if you have it installed as 'rman' in /local/bin or it's
#            in the standard path, then you're all set.  Otherwise set to
#            the path of rosetta
#
#
# The program also calls these programs...
#
# ls, nroff, cat, zcat, uname, hostname, domainname, file
#
# and will try to figure out their paths
# (Actually the hostname call is rem'd out - I use uname -n to get hostname)
#
# Changes in v0.4.1:
# (Sun Mar 20 23:02:37 EST 1994)
# - Jennifer Myers (jmyers@epsilon.eecs.nwu.edu) pointed out that my
#   script passed through `` and allowed users to submit commands to be
#   executed with the authority of the httpd process.
#   I patched the hole (I hope) by removing these commands from the
#   argument passed to the script: ! | ^ < > ` $ \ ' "
# Changes in v0.4:
# (Sat Mar 19 20:49:38 EST 1994)
# - Tries to automatically determine it's own URL..
# - Script should not require _any_ modification by the user to work
#   assuming that the user uses it as a CGI script, or puts it in /htbin
#   and uses NCSA's httpd OldScriptAlias option.
#   (Paths have been tested on SunOS 4.1,Solaris 2.x and HP/UX 9.x)
# (Sun Mar 13 20:58:06 EST 1994)
# - Support for compressed man pages.  This was added so it would work
#   on HP/UX 9.0, but compression is also supported on Sun platform.
# - Automatic search for pathname of programs used. (On startup will
#   exit immediately if path for all sub programs isn't known)
# - if /usr/share/man is a directory and /usr/man is a link pointing
#   to /usr/share/man (or ./share/man) it deletes /usr/man from @manpath
#
# Changes in v0.3:
# (Thu Mar 10 22:38:05 EST 1994)
#
# - Added support for RosettaMan to format man page instead of man2html.
#   RosettaMan supports multiple Unix style man pages and does the touch stuff
#   parsing numerous variations of man page formats...
#   (see comments for more info.)
# - @manregex is a list of regular expressions to match requests against.
# - Better recognition (or at least sooner) of '..' in a path.
#   (todo: remove reference and following dir from path instead of
#    immediately "access denied")
#
# Changes in v0.2:
# (Sun Feb 13 13:24:59 EST 1994)
#
# A bit more documentation..
#
# Alan Coopersmith (alanc@ocf.berkeley.edu) pointed out a major
#  security hole - any file from the file system could be accessed with
#  the script.  oops.
#
# Wes Barris (wes@msc.edu) pointed out that I had embedded control
#  characters in the script
#
# Todo:
# - Interface to apropos or man -k for looking up man pages by keyword.
# - Treat '..' as they should be instead of immediately "access denied"
#
# Would be nice: (These may (probably will) never be implemented)
# - Option to show the SEE ALSO's in all man pages mentioned
#   in this man page's SEE ALSO. (parse on the fly or pre-generated database?)
#

$ENV{'LC_CTYPE'}='iso_8859_1';

# Whence returns the path of a file (arg1), looking first in the
# directories supplied (args 2-n) and then using the PATH env variable.

$ls = &whence('ls','/bin','/usr/bin');
$nroff = &whence('nroff','/bin','/usr/bin','/local/bin');
# Must support the -r option
$cat = &whence('cat','/bin','/usr/bin');
# gzip (/local/bin/zcat) is preferred
$zcat = &whence('zcat', '/local/bin', '/bin','/usr/bin');
$uname = &whence('uname','/bin','/usr/bin');
#$hostname = &whence('hostname','/bin','/usr/bin');
$hostname = &whence('uname','/bin','/usr/bin');
$hostname .= ' -n'; # Equivalent
$domainname = &whence('domainname','/bin','/usr/bin');
chop($os = `$uname`);
chop($ver = `$uname -r`);
$file = &whence('file','/usr/ucb','/usr/bin');
# Must support the -L option - if a symlink stat the file itself
# Required for SunOS/Solaris, default behavior on HP-UX
$file_args = '-L' unless($os =~ /hp.?ux/i);

# If you have the RosettaMan package, set the variable below to
# the path of the binary.  If it is set to a valid program, man2html
# will use RosettaMan to format the man page... if it isn't, the
# script will markup the man page itself.. (RosettaMan does a
# better job - get it)
#
# It was written by Tom A. Phelps (phelps@CS.Berkeley.EDU) and
# is available from the following ftp site
# ftp.cs.berkeley.edu:/ucb/people/phelps/tcl/rman.tar.Z
# (or if you prefer:
# <a href="ftp://ftp.cs.berkeley.edu/ucb/people/phelps/tcl/rman.tar.Z">Rman</a>
#
# Here's a bit from the README:
# RosettaMan improves on other man page filters in several ways: (1) its
# analysis recognizes the structural pieces of man pages, enabling high
# quality output, (2) its modular structure permits easy augmentation of
# output formats, (3) it accepts man pages formatted with the varient
# macros of many different flavors of UNIX, and (4) it doesn't require
# modification or cooperation with any other program.

$rosetta = '';
$rosetta = &whence('rman','/appl/httpd/local/bin','/local/bin');
if (($rosetta) && (-x $rosetta)) { # My Little Green Rosetta... (FZ/JG)
#  $rosetta_exists = 1; # Flag to avoid future -x's
  chop($rosetta_ver = `$rosetta -v`);
  # Don't use '>' - will screw up <!-- comment
  $rosetta_contact = "Tom A. Phelps [phelps@CS.Berkeley.EDU]";

  $rosetta_subsection = 1; # Enables -b option
  # Try to recognize subsection titles in addition to section
  # titles.  This can cause problems on some UNIX systems

  # $rosetta_tabstops = 5; # for -t option
  #  Set tabstops every # columns.

  $rosetta_agressive = 1; # Enables -m option
  # Enable aggressive man page parsing - elides headers and
  # footers, identifies sections and more.
}

#$paradyne = 1;

$is_cgi = ($ENV{'GATEWAY_INTERFACE'} =~ /CGI/);
chop($this_hostname=`$hostname`);
chop($this_domainname=`$domainname`);
if (($this_domainname) && (index($hostname,'.') == -1)) {
        $this_hostname_full = "$this_hostname.$this_domainname";
} else {
        $this_hostname_full = $this_hostname;
}

# Must be set to a valid URL - used in html hyperlinks
# if not set, will produce text instead of html
if ($is_cgi) {
        $man2html_url = "http://${this_hostname_full}$ENV{'SCRIPT_NAME'}";
} else {
        $man2html_url = "http://$this_hostname_full/htbin/man2html";
}
# If it doesn't guess correctly, use a fixed string..
# Sometimes the value of `hostname` isn't fully qualified or you
# want to use a alias...
$man2html_url = 'http://www.oslonett.no/cgi-bin/man2html.pl';

# set manpath to a comma seperated list of paths where manpath will
# check (and allow access) to man pages
# SunOS: /usr/share/man(/usr/man),/usr/openwin/man
# HP-UX: /usr/man,/usr/contrib/man
# Site: /local/man
@manpath = ('/local/man','/usr/man','/local/gnu/man','/home/frogner/adm/tlist/man','/local/x11/man');

# List of regular expressions - /pdn/appl/pkg/man/man1 is valid but
# /pdn/appl/pkg/bin isn't (nor is /pdn/appl/pkg/man/../bin)
if ($paradyne) {
        @manregex = ('^(/pdn)?/appl/[^/]+/man/'); # Paradyne specific
} else {
        @manregex = ();
}

# Set this link to somebody that can be contacted...
# Unless you are on the AT&T R&D Internet (Behind the AT&T Firewall)
# you won't be able to access this link... (Feel free to change it to
# your address - as long as my name remains in the program comments...)
$contact = <<EOF;
<a href="http://wwwhome.paradyne.com/users/bcutter/intro.html">
Brooks Cutter (bcutter@paradyne.com)</a>
EOF

# Please leave these alone - used in HTML comment for each manpage
# Don't use '>' - will screw up <!-- comment
$man2html_contact = "Brooks Cutter [bcutter@paradyne.com]";
$man2html_ver = "man2html v0.4.1";

# This message describes the current status - feel free to change
# to suite your environment.  Good place for disclaimers, etc
$filter_status = <<EOF;
This is $man2html_ver written by $man2html_contact.<br>
EOF


# There has to be a blank line after this...
print "Content-type: text/html\n\n";

if ($is_cgi) {
        if ($ENV{'REQUEST_METHOD'} eq 'GET') {
                $desired_manpage = $ENV{'QUERY_STRING'};
        } elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
                read(STDIN, $desired_manpage,$ENV{'CONTENT_LENGTH'});
        } else{
                die "Unknown REQUEST_METHOD: $ENV{'REQUEST_METHOD'}";
        }
} else {
        # Old httpd htbin (OldScriptAlias) method of passing arguments...
        $desired_manpage = $ARGV[0];
}
# UnEscape
$desired_manpage =~ s/\+/ /g;
$desired_manpage =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
# Delete characters which are unlikely to be in path, and are special to shell
$desired_manpage =~ tr/\\'"!|^<>`$//d;
# Character and why deleted:
# ! because it can mean escape to shell
# | because it's the pipe symbol
# ^ because it's the old pipe symbol
# <> redirect file
# ` to avoid executing a command in ``
# to avoid ksh's $() equiv to `` and ()'s are valid for section number

unless ($desired_manpage) {
  print "
<title> $os $ver Manual Pages </title>
<h1> $os $ver Manual Pages </h1>

Enter the name of the man page, optionally surrounded
by parenthesis with the number.  For example:
<p>
<ul>
<li> ls to find one or more man pages for ls
<li> stat(2) for the system call stat
</ul>

$filter_status
<p>
$contact
";
  print "<isindex>\n";
  exit(0);
}

# Quick klude to avoid to ignore /usr/man when it's a symlink
# to /usr/share/man (and similar cases)
for (@manpath) {
        next unless (-d $_);
        if (-l $_) {
                local($ln) = readlink($_);
                if ($ln =~ m!^/!) {
                        $manpath{$_} = $ln;
                } elsif ($ln =~ m!^\./(.+)$!) {
                        local(@cur) = split(/\//,$_);
                        $manpath{$_} = join('/',@cur[0..($#cur-1)]) . '/' . $1;
                } elsif ($ln =~ m!^\.\./(.+)$!) {
                        local(@cur) = split(/\//,$_);
                        $manpath{$_} = join('/',@cur[0..($#cur-2)]) . '/' . $1;
                }
        } else {
                $manpath{$_} = 1;
        }
}
for (sort { length($a)<=>length($b) } keys %manpath) {
        if (($manpath{$_} ne '1') && ($manpath{$manpath{$_}})) {
                # If it's a symlink, and the directory it points to
                # is in the list, then delete it.
                # (There's no guarantee that link1 -> link2 -> dir3 doesn't
                # exist and that I'll process link1 before link2 (otherwise
                # link1 doesn't get deleted) - but the sort routine above
                # sorts by dir length doing shortest first - so that should
                # minimize the frequency of problems occuring (and making
                # it a annoying hard to find bug..) Moral: Customize @manpath!
                delete $manpath{$_};
        }
}
@manpath = keys %manpath;
$_ = &check_man_path($desired_manpage,*manpath,*manregex);

if ((/^-$/)) {
  $manpages[0] = $_;
} elsif ((m!^/!)) {
  $manpages[0] = $_;
} elsif (($name, $sect) = /(\S+)\((\d.*)\)/) {
  @manpages = &findman($name, $sect, @manpath);
} elsif (($name, $sect) = /(\S+)<(\d.*)>/) {
  @manpages = &findman($name, $sect, @manpath);
} elsif (($name, $sect) = /(\S+)\[(\d.*)\]/) {
  @manpages = &findman($name, $sect, @manpath);
} else {
  @manpages = &findman($_, '', @manpath);
}
if (!scalar @manpages) {
  print "Sorry, I was unable to find a match for <b>$_</b>\n";
  exit(0);
} elsif (scalar @manpages > 1) {
  &which_manpage(@manpages);
} else {
  if (!-e $manpages[0]) {
    die "man2html: Error, Can't locate file '$manpages[0]'\n";
  }

  chop($type=`$file $file_args $manpages[0]`);
  if ($type =~ /compressed/i) {
    local($data);
    chop($data = `$zcat $manpages[0] | head -1`);
    if ($data =~ /^\.\\"/) { # Roff output - preformat
      $manpages[0] = "$zcat $manpages[0] | nroff -man";
    } else {
      $manpages[0] = "$zcat $manpages[0]";
    }
  } elsif ($type =~ /roff/i) {
    $manpages[0] = "$nroff -man $manpages[0]";
  } elsif ($type =~ /text|shell/i) {
    # Do nothing $manpages[0] already set
  } else {
    $manpages[0] = ''; # Don't know what type it is
  }
  unless ($manpages[0]) {
    print "
<title>Man2HTML: An Error has occurred</title>
<h1>Man2HTML: An Error has occurred</h1>

man2html found the following match for your query:</hr>
$manpages[0]
<p>
When  '$file $file_args $manpages[0]' was run
(which should follow symbolic links)
it returned the following value '$type'
<p>

";
    if (($type =~ /link/i) || ($type =~ /cannot\s+open/i)) {
    print "
This problem appears to be that there is a symbolic link
for a man page that is pointing to a file that doesn't exist.
<p>
";
    }
    print "
Please report this problem to someone who can do something about it.
<i>(Assuming you aren't that person...)</i>
If you don't know who that is, try emailing 'root' or 'postmaster'.
<p>
There was only one match for your query - and it can't currently
be accessed.
";
    exit(0);
    #die "Unknown type '$type' for manpage '$manpages[0]'";
  }
  &print_manpage($manpages[0]);
}

exit(0);

sub findman {
# Take a argument like 'ls' or 'vi(1)' or 'tip(1c)' and return
# a list of one or more manpages.
# Arguments 2- are the directories to search in
  local($lookfor) = shift(@_);
  local($section) = shift(@_);
  local($file, @files, @return, $return);
  local(%men,%man);
  die "lookfor($lookfor) is null\n" unless($lookfor);
  for (@_) {
    # I'm... too lazy... for... opendir()... too lazy for readdir()...
    # too lazy for closedir() ... I'm too lazy!
    if (!$section) {
      @files = `$ls $_/*/$lookfor.* 2> /dev/null`;
    } else {
      # if the section is like '1b' then just search *1b
      # otherwise if '1' search *1* (to catch all sub-sections)
      # Reason for wildcards: ($_/*$section*/$lookfor.*)
      # (given $section = '2')
      # 1st: So it catches cat2 and man2
      # 2nd: So it catches man2 and man2v
      # (This should make it compatiable with HP/UX's man2.Z - not tested)
      # 3rd: So it catches stat.2 and stat.2v
      #
      if (length($section) == 1) {
        @files = `$ls $_/*$section*/$lookfor.* 2> /dev/null`;
      } else {
        local($section_num) = substr($section, 0, 1); # Just the number...
        @files = `$ls $_/*$section_num*/$lookfor.* $_/*$section/$lookfor.* 2> /
dev/null`;
      }
    }
    next if (!scalar @files);
    # This part checks the files that were found...
    for $file (@files) {
      chop($file);
      local(@dirs) = split(/\//,$file);
      local($fn) = pop(@dirs);
      local($catman) = pop(@dirs);
      local($dir) = join('/',@dirs);
      local($key) = "$dir/$fn";
      next if ($man{$key}); # forces unique
      if (!$men{$key}) {
        $men{$key} = $catman;
        $man{$key} = $file;
      } else {
        # pre-formatted man pages always take precedence unless zero bytes...
        next if (($men{$key} =~ /^cat/i) && (!(-z $man{$key})));
        $men{$key} = $catman;
        $man{$key} = $file;
      }
    }
  }
  return(values %man);
}


sub which_manpage {
# Print a list of manpages...
  print "
There were multiple matches for the argument '$desired_manpage'.
Below are the fully qualified pathnames of the matches, please
click on the appropriate one.

<ul>
";
  for (@_) {
    print "<li><a href=\"$man2html_url?$_\">$_</a>\n";
  }
  print "</ul>\n";
  return;
}

sub print_manpage {
  local($page) = @_;
  local($label, $before, $after, $begtag, $endtag, $blanks, $begtag2, $endtag2)
;
  local($pre);
  local($standard_indent) = 0;

  #if ($rosetta_exists) {
  if ($rosetta_ver) {
    $page = "$cat $page" if (index($page,' ') == -1);
    $page .= "| $rosetta";
    if ($man2html_url) { # If not set, it produces text
      $page .= " -f html";
      $page .= " -r '${man2html_url}?%s(%s)'";
    }
    $page .= " -b" if ($rosetta_subsection);
    $page .= " -t $rosetta_tabstops)" if ($rosetta_tabstops);
    $page .= " -m" if ($rosetta_agressive);
    print "<!-- Formatted with $rosetta_ver ($rosetta_contact) -->\n";
    print "<!-- Gatewayed with $man2html_ver ($man2html_contact) -->\n";
    # Rather than eval - system will print to stdout by default..
    print "<pre>\n" unless($man2html_url);
    for (`$page`) { print; }
    print "</pre>\n" unless($man2html_url);
    return;
  }
  print "<!-- Formatted with $man2html_ver ($man2html_contact) -->\n";
  if ($page =~ /[| ]/) {
    &format_man_page(`$page`);
  } elsif ($page eq '-') {
    open(MAN, '-');
  } else {
    open(MAN, $page) || die "Can't open '$page' for reading: $!";
  }
  &format_man_page(<MAN>);
}

sub format_man_page {
  for (@_) {
    if (/^\s*$/) {
      $blanks++;
      #if ($pre) { print "</pre>\n"; $pre = 0; }
      if (($. != 1) && ($blanks == 1)) {
        if (($pre) || ($section_pre)) {
          print "\n";
        } else {
          print "<p>\n";
        }
      }
      next;
    }
    #next if (!/^[A-Z]{2,}\(.*\).*/);
    if (/\ch/) { s/.\ch//g; }
    # Escape & < and >
    s/&/\&amp;/g;
    s/</\&lt;/g;
    s/>/\&gt;/g;
    #
    if (/^(\w+.*)\s*$/) {
      $label = $1;
      $next_action = '';
      if (/^[A-Z ]{2,}\s*$/) {
        if (($pre) || ($section_pre)) { print "</pre>\n"; }
        $pre = $section_pre = $section_fmt = 0;
        if (!$standard_indent) { $next_action = 'check_indent'; }
      }
      if ($label eq 'NAME') {
        $begtag = '<title>';
        $endtag = '</title>';
        $begtag2 = '<h1>';
        $endtag2 = '</h1>';
        $next_action = 'check_indent';
        next;
      }
      if ($label eq 'SYNOPSIS') {
        $section_fmt = 1;
      }
      if ($label eq 'SEE ALSO') {
        $next_action = 'create_links';
      }
      if (($label =~ /OPTIONS$/) || ($label eq 'FILES')) {
        $section_pre = 1;
        print "</pre>\n";
      } elsif (/^[A-Z ]+\s*$/) {
        print "</pre>\n" if (($pre) || ($section_pre));
        $section_pre = 0;
      }
      if (/^[A-Z ]+\s*$/) {
        print "<h2>$label</h2>\n";
        $blanks = 0;
        print "<pre>\n" if ($section_pre);
        next;
      }
      next;
    }
    if ($section_fmt) { print; $blanks = 0; next; }
    if ($next_action eq 'create_links') {
      # Parse see also looking for man page links.  Make it
      # call this program.  use '+' notation for spaces
      local($page);
      local($first) = 1;
      for $page (split(/,/)) {
        $page =~ tr/\x00-\x20//d; # Delete all control chars, spaces
        if ($page =~ /.+\(\d.*\).*$/) {
          $url_page = $page;
          $url_page =~ tr/()/[]/;
          print "," if (!$first);
          $first = 0;
          print "<a href=\"/cgi-bin/man2html?$url_page\">$page</a>\n";
        } else {
          print "," if (!$first);
          $first = 0;
          print "$page";
        }
      }
      next;
    }
    # This is to detect preformatted blocks.  I look at the first
    # line after header 'DESCRIPTION' and count the leading white
    # space as the "standard indent".  If I encounter a line with
    # a indent greater than the value of standard_indent then
    # surround it with <pre> and </pre>
    if ($next_action eq 'check_indent') {
      if (/^(\s+)\S+.*/) {
        $standard_indent = length($1);
        $next_action = '';
      }
    }
    #
    $before = length($_);
    $saved = $_;
    s/^\s+//; # Delete leading whitespace
    $after = length($_);
    s/\s+$//; # Delete trailing whitespace

    if ($begtag) {
      chop;
      print "$begtag$_$endtag\n";
      print "$begtag2$_$endtag2\n" if ($begtag2);
      $blanks = 0;
      $begtag2 = $endtag2 = $begtag = $endtag = '';
      next;
    }
    if ((!$section_fmt) && (!$section_pre) && ($standard_indent)) {
      if (($blanks == 1) && (!$pre) && ($after + $standard_indent) < $before) {
        $pre = 1;
        print "<pre>\n";
      } elsif (($pre) && ($after + $standard_indent) >= $before) {
        $pre = 0;
        print "</pre>\n";
      }
    }
    if (($section_pre) || ($pre)) {
      print "$saved";
      $blanks = 0;
      next;
    }
    # Handle word cont-
    # inuations
    if ($prefix) {
      print $prefix;
      $prefix = '';
    }
    if (/^(.+)\s+(\w+)\-\s*$/) {
      $prefix = $2;
      print "$1\n";
      $blanks = 0;
      next;
    }
    print;
    $blanks = 0;
  }
}

sub check_man_path {
  local($path) = shift(@_);
  return($path) if (($ndx = rindex($path,'/')) == -1); # No '/' in path
  local(*manpath) = shift(@_);
  local(*manregex) = shift(@_);
  # abort if string contains '..' as '../' or '..' or '/..', etc..
  &access_denied($path,'Path contains previous directory string ".."')
    if ($path =~ m!^/?([^/]+/)*..(/[^/]+)/?$!);

  local($ndx);
  local($remainder,$length);
  for (@manpath) {
    $length = length($_);
    if (substr($path,0,$length) eq $_) {
      if (substr($_,($length-1),1) eq '/') {
        # Man path is terminated with a '/', skip the '/'
        $remainder = substr($path,$length);
      } else {
        $remainder = substr($path,($length+1));
      }
      # Check the remaining path for things like '..'
      local($p,@p);
      @p = split('/',$remainder);
      for $p (0..($#p-1)) {
        # I should really remove the ../[^/]+/ reference and continue..
        &access_denied($path,'Path contains previous directory string ".."')
          if ($p[$p] eq '..');
      }
      # It's ok - return it as so
      return($path);
    }
  }
  if (@manregex) {
    local($regex);
    #local($matched) = 0;
    for $regex (@manregex) {
      #$matched = 1 if (m|$regex|);
      return($path) if ($path =~ m|$regex|);
    }
  }

  &access_denied($path,"Path doesn't match any known paths");
}

sub access_denied {
  local($path) = shift(@_);
  local($why) = shift(@_);
  $why = 'This path was not specified in the manpath list.'
    unless($why);
  print <<EOF;

An attempt was made to access the explicit path:<br>
$path
<p>
The request was refused because:<br>
<b>$why</b>
<p>
If you believe this request should be valid, please contact
$contact

EOF
  exit;
}

# Whence returns the path of a file (arg1), looking first in the
# directories supplied (args 2-n) and then using the PATH env variable.
sub whence {
  local($file) = shift(@_);
  local($_);

  for (@_,split(/:/, $ENV{'PATH'})) {
    return("$_/$file") if (-x "$_/$file");
  }
  die "Unable to find program '$file', required for $0";
  #return;
}

# EOF


