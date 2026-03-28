#!/local/bin/perl -w

%a = (1, "hei/.+\\[]()*?", 2, "\/\/", 3, "%&&||", 4, "hei");
print join(" ", %a), "\n";
&regexp_escape(@a{'1','2'});
print join(" ", %a), "\n";

exit;




sub regexp_escape {
    local ($i);

    foreach $i ( $[ .. $#_ ) {
	$_[$i] =~ s/([.*+?&|()\[\\\]])/\\$1/g;
    }
}
