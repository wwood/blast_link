#!/usr/bin/perl -w

# 

open IN, "<blast.html";

print "Content-type: text/html\n\n";

while(<IN>){
my $in = $_;
#print STDERR $in;
if(m/<FORM ACTION/){
  print '<FORM ACTION="blast_link_result.cgi" METHOD = POST NAME="MainBlastForm" ENCTYPE= "multipart/form-data">';
  print "\n";
} else {
  print $_;
}
}






