#!/local/bin/perl5

$SPOOL = "/home/frogner/a/oea/ft/spool";
$DEBUG = 0;

$N_CRLF = "\015\012";
$N_CRLFLF = "\015\012\012";
$N_STX = "\002";
$N_CRLFEXT = "\015\012\003";
$N_CRCRCRCRLF = "\015\015\015\015\012";

@mapchar = (
   0x00,		#    000 000 x00
   0x01,		#    001 001 x01
   0x02,		#    002 002 x02
   0x03,		#    003 003 x03
   0x04,		#    004 004 x04
   0x05,		#    005 005 x05
   0x06,		#    006 006 x06
   0x07,		#    007 007 x07
   0x08,		#    010 008 x08
   0x09,		#    011 009 x09
   0x0a,		#    012 010 x0a
   0x0b,		#    013 011 x0b
   0x0c,		#    014 012 x0c
   0x0d,		#    015 013 x0d
   0x0e,		#    016 014 x0e
   0x0f,		#    017 015 x0f
   0x10,		#    020 016 x10
   0x11,		#    021 017 x11
   0x12,		#    022 018 x12
   0x13,		#    023 019 x13
   0x14,		#    024 020 x14
   0x15,		#    025 021 x15
   0x16,		#    026 022 x16
   0x17,		#    027 023 x17
   0x18,		#    030 024 x18
   0x19,		#    031 025 x19
   0x1a,		#    032 026 x1a
   0x1b,		#    033 027 x1b
   0x1c,		#    034 028 x1c
   0x1d,		#    035 029 x1d
   0x1e,		#    036 030 x1e
   0x1f,		#    037 031 x1f
   0x20,		#    040 032 x20
   0x21,		# !  041 033 x21
   0x22,		# "  042 034 x22 "
   0x23,		# #  043 035 x23
   0xa4,		# $  044 036 x24
   0x25,		# %  045 037 x25
   0x26,		# &  046 038 x26
   0x27,		# '  047 039 x27 '
   0x28,		# (  050 040 x28
   0x29,		# )  051 041 x29
   0x2a,		# *  052 042 x2a
   0x2b,		# +  053 043 x2b
   0x2c,		# ,  054 044 x2c
   0x2d,		# -  055 045 x2d
   0x2e,		# .  056 046 x2e
   0x2f,		# /  057 047 x2f
   0x30,		# 0  060 048 x30
   0x31,		# 1  061 049 x31
   0x32,		# 2  062 050 x32
   0x33,		# 3  063 051 x33
   0x34,		# 4  064 052 x34
   0x35,		# 5  065 053 x35
   0x36,		# 6  066 054 x36
   0x37,		# 7  067 055 x37
   0x38,		# 8  070 056 x38
   0x39,		# 9  071 057 x39
   0x3a,		# :  072 058 x3a
   0x3b,		# ;  073 059 x3b
   0x3c,		# <  074 060 x3c
   0x3d,		# =  075 061 x3d
   0x3e,		# >  076 062 x3e
   0x3f,		# ?  077 063 x3f
   0x40,		# @  100 064 x40
   0x41,		# A  101 065 x41
   0x42,		# B  102 066 x42
   0x43,		# C  103 067 x43
   0x44,		# D  104 068 x44
   0x45,		# E  105 069 x45
   0x46,		# F  106 070 x46
   0x47,		# G  107 071 x47
   0x48,		# H  110 072 x48
   0x49,		# I  111 073 x49
   0x4a,		# J  112 074 x4a
   0x4b,		# K  113 075 x4b
   0x4c,		# L  114 076 x4c
   0x4d,		# M  115 077 x4d
   0x4e,		# N  116 078 x4e
   0x4f,		# O  117 079 x4f
   0x50,		# P  120 080 x50
   0x51,		# Q  121 081 x51
   0x52,		# R  122 082 x52
   0x53,		# S  123 083 x53
   0x54,		# T  124 084 x54
   0x55,		# U  125 085 x55
   0x56,		# V  126 086 x56
   0x57,		# W  127 087 x57
   0x58,		# X  130 088 x58
   0x59,		# Y  131 089 x59
   0x5a,		# Z  132 090 x5a
   0x5b,		# [  133 091 x5b
   0x5c,		# \  134 092 x5c
   0x5d,		# ]  135 093 x5d
   0x5e,		# ^  136 094 x5e
   0x5f,		# _  137 095 x5f
   0x60,		# `  140 096 x60 `
   0x61,		# a  141 097 x61
   0x62,		# b  142 098 x62
   0x63,		# c  143 099 x63
   0x64,		# d  144 100 x64
   0x65,		# e  145 101 x65
   0x66,		# f  146 102 x66
   0x67,		# g  147 103 x67
   0x68,		# h  150 104 x68
   0x69,		# i  151 105 x69
   0x6a,		# j  152 106 x6a
   0x6b,		# k  153 107 x6b
   0x6c,		# l  154 108 x6c
   0x6d,		# m  155 109 x6d
   0x6e,		# n  156 110 x6e
   0x6f,		# o  157 111 x6f
   0x70,		# p  160 112 x70
   0x71,		# q  161 113 x71
   0x72,		# r  162 114 x72
   0x73,		# s  163 115 x73
   0x74,		# t  164 116 x74
   0x75,		# u  165 117 x75
   0x76,		# v  166 118 x76
   0x77,		# w  167 119 x77
   0x78,		# x  170 120 x78
   0x79,		# y  171 121 x79
   0x7a,		# z  172 122 x7a
   0x7b,		# {  173 123 x7b
   0x7c,		# |  174 124 x7c
   0x7d,		# }  175 125 x7d
   0x7e,		# ~  176 126 x7e
   0x7f,		#    177 127 x7f
   0x80,		#    200 128 x80 N_QL
   0x81,		#    201 129 x81 N_QC
   0x82,		#    202 130 x82 N_QR
   0x83,		#    203 131 x83 N_QM
   0x84,		#    204 132 x84 N_TL Tab venstresentrert kolonne
   0x85,		#    205 133 x85 N_TC Tab midtsentrert kolonne
   0x86,		#    206 134 x86 N_TR Tab h|yresentrert kolonne
   0x87,		#    207 135 x87 splittkode 1 for resultattabel
   0x88,		#    210 136 x88 splittkode 2 for stillingstabell
   0x89,		#    211 137 x89
   0x8a,		#    212 138 x8a
   0x8b,		#    213 139 x8b
   0x8c,		#    214 140 x8c
   0x8d,		#    215 141 x8d
   0x8e,		#    216 142 x8e
   0x8f,		#    217 143 x8f
   0x90,		#    220 144 x90 N_OV
   0x91,		#    221 145 x91
   0x92,		#    222 146 x92 N_ING
   0x93,		#    223 147 x93 N_FO
   0x94,		#    224 148 x94 N_TE
   0x95,		#    225 149 x95 N_SLT slutt tabell
   0x96,		#    226 150 x96 N_UT
   0x97,		#    227 151 x97
   0x98,		#    230 152 x98 N_INF
   0x99,		#    231 153 x99 N_RED
   0x9a,		#    232 154 x9a N_STK Start kommando-tegn
   0x9b,		#    233 155 x9b
   0x20,		#    234 156 x9c N_TH Thin-space
   0x20,		#    235 157 x9d N_EN EN-space
   0x101,	#M	#    236 158 x9e "  " N_EM EM-space
   0x9f,		#    237 159 x9f Slutt kommando-tegn
   0xa0,		#    240 160 xa0 Start tabell-linje
   0xa1,		#    241 161 xa1
   0xa2,		#    242 162 xa2
   0xa3,		#    243 163 xa3
   0x24,		#    244 164 xa4 dollartegn
   0xa5,		#    245 165 xa5
   0xe5,		#    246 166 xa6 norsk/dansk aa
   0xa7,		#    247 167 xa7 paragraf
   0xc5,		#    250 168 xa8
   0x60,		#    251 169 xa9
   0x101,	#M	#    252 170 xaa ``
   0xab,		#    253 171 xab g}s|yne begynner
   0xad,		#    254 172 xac
   0x7c,		#    255 173 xad
   0xad,		#    256 174 xae
   0x7c,		#    257 175 xaf
   0xb0,		#    260 176 xb0
   0xb1,		#    261 177 xb1
   0xb2,		#    262 178 xb2 2-tall i superscript
   0xb3,		#    263 179 xb3 3-tall i superscript
   0xd7,		#    264 180 xb4
   0xb5,		#    265 181 xb5
   0xb6,		#    266 182 xb6
   0xb7,		#    267 183 xb7
   0xf7,		#    270 184 xb8
   0x27,		#    271 185 xb9
   0x101,	#M	#    272 186 xba ''
   0xbb,		#    273 187 xbb g}se|yne slutter
   0xbc,		#    274 188 xbc
   0xbd,		#    275 189 xbd
   0xbe,		#    276 190 xbe
   0xbf,		#    277 191 xbf
   0xc0,		#    300 192 xc0
   0x100,		#    301 193 xc1 aksent grave	KOMBTEGN A E a e
   0x100,		#    302 194 xc2 aksent egu	KOMBTEGN A E a e
   0x100,		#    303 195 xc3 circumflex	KOMBTEGN O o
   0x100,		#    304 196 xc4 tilde		KOMBTEGN N n
   0x100,		#    305 197 xc5 aksent macron	KOMBTEGN O o
   0xc6,		#    306 198 xc6 aksent breve (har ikke)
   0xc7,		#    307 199 xc7
   0x100,		#    310 200 xc8 umlaut (ae)	KOMBTEGN A O U a o u
   0x100,		#    311 201 xc9 cedille	KOMBTEGN C c
   0x100,		#    312 202 xca ring,		KOMBTEGN A a
   0xb8,		#    313 203 xcb
   0x5f,		#    314 204 xcc
   0x22,		#    315 205 xcd
   0x2c,		#    316 206 xce
   0xcf,		#    317 207 xcf
   0x2d,		#    320 208 xd0 tankestrek
   0xb9,		#    321 209 xd1
   0xae,		#    322 210 xd2 registrert varemerke
   0xa9,		#    323 211 xd3 copyright
   0x101,	#M	#    324 212 xd4 (TM)
   0xd5,		#    325 213 xd5
   0xd6,		#    326 214 xd6
   0xd7,		#    327 215 xd7
   0xd8,		#    330 216 xd8
   0xd9,		#    331 217 xd9
   0xda,		#    332 218 xda
   0xdb,		#    333 219 xdb
   0x101,	#M	#    334 220 xdc 1/8
   0x101,	#M	#    335 221 xdd 3/8
   0x101,	#M	#    336 222 xde 5/8
   0x101,	#M	#    337 223 xdf 7/8
   0xe0,		#    340 224 xe0
   0xc6,		#    341 225 xe1
   0xd0,		#    342 226 xe2
   0x61,		#    343 227 xe3
   0x48,		#    344 228 xe4
   0x4e,		#    345 229 xe5
   0x101,	#M	#    346 230 xe6 IJ
   0x101,	#M	#    347 231 xe7 L· (el-dott)
   0x4c,		#    350 232 xe8
   0xd8,		#    351 233 xe9
   0x101,	#M	#    352 234 xea OE (fransk OE)
   0xb0,		#    353 235 xeb
   0xde,		#    354 236 xec
   0x54,		#    355 237 xed
   0x4e,		#    356 238 xee
   0x6e,		#    357 239 xef
   0x4b,		#    360 240 xf0
   0xe6,		#    361 241 xf1 norsk/dansk ae
   0x64,		#    362 242 xf2
   0xf0,		#    363 243 xf3
   0x69,		#    364 244 xf4
   0x49,		#    365 245 xf5
   0x101,	#M	#    366 246 xf6 ij
   0x101,	#M	#    367 247 xf7 l· (el-dott)
   0x6c,		#    370 248 xf8
   0xf8,		#    371 249 xf9 norsk/dansk oe
   0x101,	#M	#    372 250 xfa oe (fransk oe)
   0xdf,		#    373 251 xfb
   0xfe,		#    374 252 xfc
   0x74,		#    375 253 xfd
   0x64,		#    376 254 xfe
   0xff			#    377 255 xff
);

%multichar = (
   0x9e, "  ",
   0xaa, "``",
   0xba, "''",
   0xd4, "(TM)",
   0xdc, "1/8",
   0xdd, "3/8",
   0xde, "5/8",
   0xdf, "7/8",
   0xe6, "IJ",
   0xe7, "L\267",
   0xea, "OE",
   0xf6, "ij",
   0xf7, "l\267",
   0xfa, "oe"
);

%compchar = (
   "\301A", "\300",
   "\301E", "\310",
   "\301a", "\340",
   "\301e", "\350",
   "\306A", "\300",
   "\306E", "\310",
   "\306a", "\340",
   "\306e", "\350",
   "\302A", "\301",
   "\302E", "\311",
   "\302a", "\341",
   "\302e", "\351",
   "\303O", "\324",
   "\303o", "\364",
   "\304N", "\321",
   "\304n", "\361",
   "\310A", "\304",
   "\310O", "\326",
   "\310U", "\334",
   "\310a", "\344",
   "\310o", "\366",
   "\310u", "\374",
   "\311C", "\307",
   "\311c", "\347",
   "\312A", "\305",
   "\312a", "\345"
);
# Read a character and convert
sub getcc {
    local($c, $r);

    $c = getc(F);
    $r = @mapchar[ord($c)];
    if ($r == 0) {
	return '';
    } elsif ($r == 0x100) {	# Composed character
	$cc = getc(F);
	return $compchar{$c.$cc};
    } elsif ($r == 0x101) {	# Char -> string
	return $multichar{ord($c)};
    } else {
	return chr($r);
    }
}

# Read $num characters and return them
sub rstr {
    local($num) = @_;
    local($s);

    while($num--) {
	$s .= getc(F);
    }
    return $s;
}

# Read a string, compare with argument, 0 if it matches, 1 if it don't
sub expect {
    local($s) = @_;
    local($c, @s);

    @s = split(//, $s);
    while($_ = shift(@s)) {
	$c = getc(F);
	if ($_ ne $c) {
	    printf STDERR "expected '$_' got '$c'\n";
	    return 1;
	}
    }
    return 0;
}

# Read until we have a string matching $s, return what was before $s
sub readto {
    local($s) = @_;
    local($l, $r);

    $l = &rstr(length($s));
    while($l ne $s && !eof(F)) {
	$r .= substr($l, 0, 1);
	$l = substr($l, 1) . &getcc;
    }
    return $r;
}

sub tconv {
    local($c, $r);
    $c = &getcc;
    while(!eof(F)) {
	$r .= $c;
	$c = &getcc;
    }
    return $r;
}

sub dofile {
    local($file) = @_;
    open(F, $file) || return;
    print "Reading $file\n" if $DEBUG;
    $N_linetype = &rstr(3);
    print "linetype: $N_linetype\n" if $DEBUG;
    $N_serialnum = &rstr(4);
    print "serialnum: $N_serialnum\n" if $DEBUG;
    &expect(" ");
    $N_priority = getc(F);
    print "priority: $N_priority\n" if $DEBUG;
    &expect(" ");
    $N_type = &rstr(3);
    print "type: $N_type\n" if $DEBUG;
    &expect(" ");
    $N_length = &rstr(5);	# Throw this
    print "length: $N_length\n" if $DEBUG;
    &expect(" ");
    $N_subtype = &rstr(3);
    print "subtype: $N_subtype\n" if $DEBUG;
    &expect(" ");
    $N_information = &readto($N_CRLF);
    print "information: $N_information\n" if $DEBUG;
    $N_keyword = &readto($N_CRLFLF);
    print "keyword: $N_keyword\n" if $DEBUG;
    &expect($N_STX);
    $N_message = &tconv(F);
#    $N_message =~ /.*\n(\d{0,8}\s{1,3}?\w{1,5}\s{1,3}\d{1,5})/;
#    $N_date = $1;
#    print "Date: $1\n" if $DEBUG;
    print "message: $N_message\n" if $DEBUG;
    close(F);
    &putt_inn_din_rutine_her;
#    &dumpdata if !$DEBUG;
}

sub dumpdata {
    print "linetype: $N_linetype\n";
    print "serialnum: $N_serialnum\n";
    print "priority: $N_priority\n";
    print "type: $N_type\n";
    print "length: $N_length\n";
    print "subtype: $N_subtype\n";
    print "information: $N_information\n";
    print "keyword: $N_keyword\n";
#    print "date: $N_date\n";
    print "message: $N_message\n";
}


opendir(DIR, "$SPOOL") || die "no $SPOOL";
while(1) {
    while($_ = readdir DIR) {
	&dofile($SPOOL.'/'.$_) if /^\d{10}$/;
#	unlink($SPOOL.'/'.$_);
    }
    rewinddir DIR;
    sleep 60;
}
# just to be polite
closedir(DIR);
print "1 == 0, I think I retire\n";
exit 17;
