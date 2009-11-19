#!/usr/bin/perl -w

# A blast job is submitted to this script, and this script returns the result.

use CGI;
use File::Temp qw/ tempfile /

umask 0007;

#getting the POST request, and dumping it into a temporary file                                                                                                                                   
($in_fh, $in_file) = tempfile(); #tempfiles in ruby make so much more sense.
while(<>)
{
	print $in_fh, $_;
}

# pipeline the post request to the blast script, and record the result
# first write out the CGI request to a temporary file
($out_fh, $out_file) = tempfile();
`blast.REAL <$in_file >$out_file`

