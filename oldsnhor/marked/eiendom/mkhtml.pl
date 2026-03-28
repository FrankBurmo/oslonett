# A perl module

package mkhtml;

sub eiendom
{
    my($file, $e) = @_;
    die("$file is not a HTML file name") unless $file =~ /\.html?$/;
    open(HTML, ">$file") or die "Can't open $file: $!";
    my $dir = $file;
    $dir =~ s,(.*)/.*,$1,;
    $dir = "." unless length $dir;

    my $title = $e->{title} || "No title";
    print HTML "<title>$title</title>\n";
    print HTML qq{<body background="../notar-bg.gif"><h1>$title</h1>\n};
    if (-f "$dir/img.gif") {
	print HTML qq{<img src="img.gif">\n};
    }
    print HTML "<p><font size=+2>\n";
    print HTML "$e->{eierform} $e->{type}";
    print HTML ", $e->{size} m²" if $e->{size};
    print HTML ", $e->{rooms} roms" if $e->{rooms};
    print HTML "\n\n<p>\n";
    if ($e->{address}) {
	print HTML "<b>Adresse:</b> $e->{address}, $e->{zipcode} $e->{place}<br>\n";
    }
    if ($e->{price}) {
	print HTML "<b>Prisantydning:</b> $e->{price}\n";
	if ($e->{takst}) {
	    print HTML " (Verditakst: $e->{takst})\n";
	}
	print HTML "<br>\n";
    }
    if ($e->{visning}) {
	print HTML "<b>Visning:</b> $e->{visning}<br>\n";
    }
    print HTML "</font>\n\n";

    print HTML "<p><font size=+1>$e->{text}</font>\n";

    @html = grep(!/index.html/, glob "$dir/*.html");
    if (@html) {
	print HTML "<p><ul>\n";
	foreach (@html) {
	    ($link = $_) =~ s,^\Q$dir/,,;
	    open(F, $_) or next;
	    $title = $link;
	    while (<F>) {
		if (/<title>(.+)<\/title>/i) {
		    $title = $1;
		    last;
		}
		last if /<body/;
	    }
	    close(<F>);
	    print HTML qq{<li><a href="$link">$title</a>\n};
	}
	print HTML "</ul>\n";
    }

    print HTML qq{<p><a href="../notar.html"><img src="../notar.gif"></a>\n};
    my $id = $dir;
    $id =~ s,^.*/,,;
    print HTML qq{<p><font size="-2"><a href="../edit.cgi?id=$id">[Admin]</a></font>\n};

    # print HTML "<pre>\n";
    # foreach (sort keys %{$e}) {
    #     next if $_ eq "title";
    # 	print HTML "$_: $e->{$_}\n";
    # }
    # print HTML "</pre>\n";
    print HTML "</body>\n";
    close(HTML);
    $file;
}

1;
