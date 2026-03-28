#!/local/bin/perl
#
# htmltree	traverse a subtree in the filesystem, produce HTML-document
#		presenting the titles of directories and files in the subtree.
#		The displayed title of a file is the string from the <title>
#		tag (if present) in HTML documents, otherwise the unix
#		filename. For a directory the title is the title of the
#		index.htm(l) files (if present) in the directory.
#
# Warning:	Symbolic links are followed. The program keeps track of
#	 	inodes that are visited and will never be caught in a
#		filesystem loop. Yet, when following symbolic links, the
#		order of appaerance of directories can deviate from the
#		actual filesystem appearance (as shown by e.g. ls(1).
#
#		The script reads parameters from unix command line or HTML
#		forms (methods "POST" or "GET"). Possible options are:
#
#			dir=<directory name of root of subtree>
#			maxlevel=<max. search depth in subtree>
#			icons=<any string except "0" to include icons>
#			notfiles=<perl regexp>
#			files=<perl regexp>
#			  Files whose names match "files" and not "notfiles"
#			  are displayed
#			showdir=<"links", "nolinks" or "0"/not present>
#			  Directories without the file index.htm(l) can be
#			  discarded, shown as texts (unix directory name)
#			  or as links. (If your server is configured to not
#			  showing index of directories, do not use "links".)
#			header=<filename containing HTML header>
#			footer=<filename containing HTML footer>
#
#		Command line options may be preceeded by a '-'.
#
# Author: kgn@oslonett.no, July 1995

$ENV{'PATH'} = '/local/bin:/bin/:usr/bin';
$ENV{'LC_CTYPE'} = 'iso_8859_1'; # Help file(1) identify _all_ text files

$indent		= '  ';		# Used when producing <pre>-text
$bufsiz		= 1024;
$wwwroot	= '/local/www';

# default option(s) are set here
%option		= ('maxlevel',	15,
		   'notfiles',	'\.bak$|\~$|\.map$|\.cgi$|^\.',
		   'header',	'/home/frogner/www2/cgi-src/htmltree/HEADER',
		   'footer',	'/home/frogner/www2/cgi-src/htmltree/FOOTER' );

# To select an icon the file(1) program is run. The output is matched
# against each key of %icons and the corresponding value names the icon
# Because the %icons array is scanned in hash index order, conflicting
# keys will result in unpredictable icon selection.
%icons		= ("directory",	"menu.gif",
		   "text",	"text.gif",
		   "html",	"text.gif",
		   "executable","binary.gif",
		   "audio",	"sound.gif",
		   "jpeg",	"image.gif",
		   "tiff",	"image.gif",
		   "gif",	"image.gif",
		   "ppm",	"image.gif" );
$icondir	= "/mc-icons";
$defaulticon	= "$icondir/unknown.gif";

# The program can read its options either from the unix command line
# or from a FORM. If the environment variable REQUEST_METHOD is true
# (defined and non zero) we assume input via FORM.
if ($ENV{'REQUEST_METHOD'}) {
    print "Content-type: text/html\n\n";
    %option = &getforminput(%option);
} else {
    %option = &getarginput(%option);
} 

chdir $wwwroot || &error(qq#Could not access the directory "$wwwroot"#);

# The subtree root must not have leading or trailing '/'.
$option{'dir'} =~ s#^/+##;
$option{'dir'} =~ s#/+$##;
$option{'dir'} =~ s#/+#/#g; # Multiple '/'s are translated into one '/'.
# If no directory is given, use '.'
$option{'dir'} = '.' unless $option{'dir'};

&printheader($option{'dir'});
&dosearch($option{'dir'});	# Recursively search the subtree
&printfooter;

exit 0;



sub dosearch {
# This subroutine recursively traverses the subtre of the filesystem
# whose root is passed as a parameter. For each level directories and
# files are shown according to the specified options.
    local($dir) = $_[0];
    local($file, %dir, $inode, @allfiles, $title);

# We store inode numbers that are visited. If the inode has already
# been visited, the subroutine returns. The script will never be trapped
# in a filesystem loop
    $inode = (stat("$dir"))[1];
    return if ($seen{$inode}++);

# Find the title of the "index.htm(l)" file in this directory 
    $title = &title("$dir/index.html") || &title("$dir/index.htm");

# Unless title is defined or directories without "index.htm(l)"
# are specified to be shown, this directory should be skipped.
    return unless ($option{'showdir'} || $title);

# Print info about the directory we just entered
    printf("%s%s%s\n",
	   $indent x $level, &icon($dir), $title || &dirlink("$dir"));

    $level++;

# If the search level is too deep, return.
    if ($level >= $option{'maxlevel'}) {
	$level--;
	return;
    }

# All filenames and directories in $dir is read into @allfiles
    opendir(DIR, "$dir") || return;
    @allfiles = readdir(DIR);
    closedir(DIR);


# All files should be displayed before any subdirectories. 
    foreach $file ( sort @allfiles ) {
	next unless ($option{'files'} && $file =~ /$option{'files'}/o);
	next if ($option{'notfiles'} && $file =~ /$option{'notfiles'}/o);
	next if -d "$dir/$file";
	next if $file =~ /^index.html?$/i; # ...has been visited already

	printf("%s%s%s\n", $indent x $level, &icon("$dir/$file"),
	       &title("$dir/$file") || &filelink($dir, $file))
	    if ( -r  _ );
    }

    foreach $file ( sort @allfiles ) {
# Do not recurse into directories starting with . (including '.' and '..')
	next if $file =~ /^\./;
	next unless -d "$dir/$file"; # Skip anything but directories...
	&dosearch("$dir/$file") if ( -r _ && -x _); # ...that can be accessed
    }
    $level--;
}



sub icon {
# The file type of the parameter is found with the file(1) program
# The type is matched against keys from the %icons array and an <img>
# tag referring to a suitable icon is returned.
    local($file) = $_[0];
    local($src, $key, $value);
    return unless $option{'icons'};

    $_ = `/usr/bin/file -L $file`;
    s/^$file:\s*//;
    $src = $defaulticon;
    foreach $key ( keys %icons ) {
	if (/$key/i) {
	    $src = "$icondir/$icons{$key}";
	    last;
	}
    }
    return qq#<img align="absbottom" alt="" src="$src" border="0"> #;
}


sub htmlescape {
# Escapes all HTML code in the parameter by replacing '<', '&' and '>' by "&lt;",
# "&amp;" and "&gt;" respectively.
    local($text) = $_[0];

    $text =~ s/&/&amp;/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    return $text;
}
    

sub title {
# Opens the file specified by the first parameter and searches the first
# $bufsiz bytes for a <title> tag and end tag. The title text is returned
# if present, otherwise an undefined vlue
    local($filename) = $_[0];
    local($title, %FILE);
    local($_);

    open(FILE, "$filename") || return;
    read(FILE, $_, $bufsiz);
    s/\s+/ /g;
    ($title) = m#<title>([^<]*)</title>#i;
    close(FILE);

    $filename = &htmlescape($filename);
    $title = &htmlescape($title);
    return qq#<a href="/$filename">$title</a># if $title;
    return undef;
}



sub filelink {
    local($dir, $file) = @_;

    return sprintf(qq#<a href="/%s">%s</a>#, 
		   &htmlescape("$dir/$file"), &htmlescape($file));
}


sub dirlink{
# The parameter specifies a directory name. If the relevant option is 
# set, the subroutine returns the name with a surrounding anchor tag
# (<a...>dirname</a>) - otherwise the name itself is returned.
    local($dir) = $_[0];

    $dir = &htmlescape("/" . $dir);
    ($option{'showdir'} =~ /^link/i) ? qq#<a href="$dir/">$dir/</a># : "$dir/";
}



sub getforminput {
# Data from HTML FORM (method GET or POST) is read and added to the
# keys/values of the associative array which is the parameter.
    local(%option) = @_;
    local($name, $value, $data, @data);

    if ($ENV{'REQUEST_METHOD'} eq "GET") {
        $data = $ENV{'QUERY_STRING'};
    } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
        read(STDIN, $data, $ENV{'CONTENT_LENGTH'});
    } else {
	&error("CGI-script accessed with unknown access method: $ENV{'REQUEST_METHOD'}");
    }

    # Data is split at all occurances of '&'.
    @data = split(/&/, $data);

    for $entry ( @data ) {

	# Translate '+' to SPC
        $entry =~ tr/+/ /;

        # Anything left of the first '=' is field name, the rest is field value
        ($name, $value) = split(/=/, $entry, 2);

	# Occurances of %<hexcode> is translated to the corresponding character
        $name =~ s/%(..)/pack("c",hex($1))/ge;
        $value =~ s/%(..)/pack("c",hex($1))/ge;

        $option{$name} = $value;
    }
    %option;                     # return the associative array
}



sub getarginput {
# Reads in options from @ARGV. New key/value pairs are added to the
# associative array given as a parameter
    local(%option) = @_;
    local($name, $value, $par);

    foreach $par (@ARGV) {
	# Anything left of the first '=' is field name, the rest is field value
        ($name, $value) = split(/=/, $par, 2);
	$name =~ s/^-//;	# Command line options may have a leading '-'.
        $option{$name} = $value;
    }
    %option;
}



sub printheader {
# Attempts to read the file named by $option{'header'}. If successful,
# all occurencies of _SERVERNAME_ and _DIR_ in the file are replaced
# by the name of the machine running the script and the directory given
# as a parameter respectively. If the file could not be read, a standard
# HTML-header is returned. The file should contain the tags <html>
#  <head> <title> </title> </html> <body> <h1> </h1>.
    local($dir) = $_[0];

    if (open(HEADER, $option{'header'})) {
	while (<HEADER>) {
	    s/_SERVERNAME_/$ENV{'SERVER_NAME'}/g;
	    s/_DIR_/$dir/g;
	    print;
	}
	close(HEADER);
	print "<pre>\n";
	return;
    }
    print <<EOT;
<html>
<head>
 <title>Contents of http://$ENV{'SERVER_NAME'}/$dir</title>
</head>
<body>
<h1>Contents of http://$ENV{'SERVER_NAME'}/$dir</h1>
<pre>
EOT
}


sub printfooter {
# Attempts to read and output the file named by $option{'footer'}. If
# unsuccessful, a standard footer is printed. The footer file should
# contain the tags </body> </html>.
    if (open(FOOTER, $option{'footer'})) {
	print "</pre>\n";
	while (<FOOTER>) {
	    print;
	}
	close(FOOTER);
	return;
    }
    print <<EOT;
</pre>
</body>
</html>
EOT
}
