#! /bin/csh -f

foreach file ( `ls -1 *.html`)
sed -e "s/94043-1100//" $file
end
