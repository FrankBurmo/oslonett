#!/local/bin/perl5

require 'lib.pl';

$butikk="intershop";

$cookiename = "kurvid";
$DATADIR = "/local/www/kurv/kunder";

%input = &getinput;

$input{id} = &getid;

# Make sure netscape client remembers cookie till next time
print "Set-Cookie: $cookiename=$input{id}; path=/\n";

#$DEBUG = 1;
if ($DEBUG) {
    print "Content-type: text/html\n\n";
    print "<pre>\n";
    print "$ENV{HTTP_COOKIE}\n";
}

open(KURV, ">>$DATADIR/kurv-$input{id}.data")
    || &error("Kunne ikke legge varen ned i kurven");
print KURV "$ENV{PATH_INFO} 1\n";
close KURV;

$sistebutikk = $1 if $ENV{PATH_INFO} =~ m,^/?([^/]+),;
if ( length $sistebutikk && 
     open(SISTEB, ">$DATADIR/kurv-$input{id}.sistebutikk") ) {
    print SISTEB $sistebutikk;
}


# $goto = $ENV{SERVER_URL};

$goto .= (length $input{'ref'})
    ? $input{'ref'} : "/kurv/vis.cgi?id=$input{id}";

# $goto = "/kurv/vis.cgi?id=$input{id}";

#print "Set-Cookie: $cookiename=$input{id}; path=/\n";


# $intercept=1;  # used for debugging of welcome message
&velkommen if $intercept;

print "Location: $goto\n\n";

exit 0;

