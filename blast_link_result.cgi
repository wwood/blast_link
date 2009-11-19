#!/usr/bin/perl -w

# A blast job is submitted to this script, and this script returns the blast
# result page with links. The actual code for making the links must be defined
# by the administrator.



# Use this subroutine to change the alignment line into links. The only argument
# is the first line of the sequence in the alignment.
# eg. 
# ><a name = 654></a>Toxoplasma gondii | TGME49_112100 | Ca2+-ATPase
# returns 
# ><a href=/apiloc/gene/TGME49_112100>Toxoplasma gondii | TGME49_112100 | Ca2+-ATPase</a>
sub replace_alignment_name_with_links {
  my $name = $_[0];
  chomp $name;
  $name =~ m/.+?\| (.+?) \|/;
  print '><a href=\'/apiloc/gene/'.$1.'\'>'.$name."</a>\n";
}





use File::Temp qw/ tempfile /;

umask 0007;

# The CGI request is piped in through STDIN. If this script doesn't
# touch STDIN, then blast.REAL will receive it. Record the result
# of blast.REAL, and then it will be parsed afterwards to add links.
(undef, $out_file) = tempfile();
`export BLASTDB=db; ./blast.REAL >$out_file`;

# Proper header
print "Content-type: text/html\n\n";

open OUT, $out_file;
while(<OUT>){
  # eg. '><a name = 654></a>Toxoplasma gondii | TGME49_112100 | Ca2+-ATPase'
  if (m/(<a name \= \d+\>\<.a\>)(.+)/){
    # line contains an alignment description. Insert a link after the internal
    # link from the description.
    print $1;
    replace_alignment_name_with_links($2)
  } else {
    # normal line. Let it pass straight through to the user.
    print $_;
  }
}


