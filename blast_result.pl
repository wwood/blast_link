#!/usr/bin/perl -w

# A blast job is submitted to this script, and this script returns the result.

#use File::Temp qw/ tempfile /;

umask 0007;

#getting the POST request, and dumping it into a temporary file
#($in_fh, $in_file) = tempfile(); #tempfiles in ruby make so much more sense.
open INPUT, '>/tmp/input';

#print INPUT "Content-type: text/html";
#print INPUT "";


#my $cgi = CGI->new or die "Error: Creation of CGI object failed, exiting.\n";
while(<STDIN>)
{
	print INPUT $_;
#print STDERR $_;
}

# pipeline the post request to the blast script, and record the result
# first write out the CGI request to a temporary file
#($out_fh, $out_file) = tempfile();
`/var/www/blast/blast.REAL </tmp/input >/tmp/output`;

print "Content-type: text/html\n\n";

open OUT, '/tmp/output';
while(<OUT>){
# eg. 
# ><a name = 654></a>Toxoplasma gondii | TGME49_112100 | Ca2+-ATPase
if (m/a name\= \d+\>\<.a\>(.+)\n/){
my $name = $1;
$name = m/.+?\| (.+?) \|/;
print '.><a href=/apiloc/gene/'.$1.'>'.$name."</a>\n";
} else {
print $_;
}
}


