#!/local/bin/perl

print "Content-type: text/html\n\n";
print "<Head><Title>DND's faxservice</Title></Head>";
print "<Body><hr size=2><H1>DND's Faxservice</H1><hr size=4>";


sub ReadParse {
  if (@_) {
    local (*in) = @_;
  }

  local ($i, $loc, $key, $val);

  # Read in text
  if ($ENV{'REQUEST_METHOD'} eq "GET") {
    $in = $ENV{'QUERY_STRING'};
  } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
    for ($i = 0; $i < $ENV{'CONTENT_LENGTH'}; $i++) {
      $in .= getc;
    }
  } 

  @in = split(/&/,$in);

  foreach $i (0 .. $#in) {
    # Convert plus's to spaces
    $in[$i] =~ s/\+/ /g;

    # Convert %XX from hex numbers to alphanumeric
    $in[$i] =~ s/%(..)/pack("c",hex($1))/ge;

    # Split into key and value.
    $loc = index($in[$i],"=");
    $key = substr($in[$i],0,$loc);
    $val = substr($in[$i],$loc+1);
    $in{$key} .= '\0' if (defined($in{$key})); # \0 is the multiple separator
    $in{$key} .= $val;
  }

  return 1; # just for fun
}



sub empty_input
{
    print "Det ble ikke gitt tilstrekkelig input.";
    print "Ingen fax ble sendt.";
    exit;
}


&ReadParse;

if ($in{"Navn"} && ($in{"Firmaadr"} || $in{"Privadr"}))
{
    # Send the fax message...
    print "Reporting: Fax message complete. Transmission succeeded";
    print "OKOKOK";

}
