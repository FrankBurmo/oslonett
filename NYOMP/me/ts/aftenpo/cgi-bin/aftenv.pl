#!/usr/bin/perl

require "formlib.pl";
require "escape.pl";

&GetPostArgs;

print "Content-type: text/html

";

# Hent inn tittelannonse
########################
if($in{format} eq "tittel") {
	open (INN, "../annonse/ann_kalk/resultat.hea") || print "** FEIL!";
	while (<INN>) { print $_; }
	close (INN);	

	open (INN, "../annonse/ann_kalk/tittelan.htm") || print
"** FEIL!";
	while (<INN>) { print $_; }
	close (INN);	
	exit;
}


# Hent inn toppen
#################
open (INN, "../annonse/ann_kalk/head.htm") || print "** FEIL!";
while (<INN>) { print $_; }
close (INN);


# printer ut 1 av 6 websider-skjemaer
#####################################
if($in{utgave} eq "morgen") {
	if($in{format} eq "andre") {
		open (INN, "../annonse/ann_kalk/m_andre.htm") || print "**
FEIL!"; }
	elsif($in{format} eq "helside") {
		open (INN, "../annonse/ann_kalk/m_helsid.htm") || print "**
FEIL!"; }
	elsif($in{format} eq "dobbel") {
		open (INN, "../annonse/ann_kalk/m_dobsid.htm") || print
"** FEIL!"; } }
elsif($in{utgave} eq "aften") {
	if($in{format} eq "andre") {
		open (INN, "../annonse/ann_kalk/a_andre.htm") || print "**
FEIL!"; }
	elsif($in{format} eq "helside") {
		open (INN, "../annonse/ann_kalk/a_helsid.htm") || print "**
FEIL!"; }
	elsif($in{format} eq "dobbel") {
		open (INN, "../annonse/ann_kalk/a_dobsid.htm") || print
"** FEIL!"; } }
while (<INN>) { print $_; }
close (INN);


# Hent inn bunnen
#################
# open (INN, "../annonse/ann_kalk/tail.html") || print "** FEIL!";
# while (<INN>) { print $_; }
# close (INN);




