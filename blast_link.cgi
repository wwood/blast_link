#!/usr/bin/perl -w

# 

print "Content-type: text/html\n\n";

unless (open IN, "<blast.html") {
print "Could not find (or did not have sufficient permissions to open) blast.html. Has NCBI wwwblast (available from ftp://ftp.ncbi.nih.gov/blast/executables/release/LATEST/) been downloaded and extracted into the same directory as blast_link? (i.e. blast.html and blast_link.cgi should end up being in the same directory)";
exit;
}



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






