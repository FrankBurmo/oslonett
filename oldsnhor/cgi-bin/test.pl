#!/local/bin/perl

$input = &getinput;

print <<EOT;
Content-type: text/plain


Running 'env':
--------------
EOT
$a = `env`;
print "$a \n";

if ($ENV{REQUEST_METHOD} eq "POST" )
{

 print "STDIN ukodet: \n$data";
}



sub getinput {
# Return %input array, associating input names with input values
# Also builds global array @datanames, giving original order of input
# field names.
    local($i, $name, $value, @data, %input);

    if ($ENV{'REQUEST_METHOD'} eq "GET") {
        $data = $ENV{'QUERY_STRING'};
    } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
        read(STDIN, $data, $ENV{'CONTENT_LENGTH'});
    } else {
        return undef;
    }
return $data;
}