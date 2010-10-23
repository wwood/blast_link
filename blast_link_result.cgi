#!/usr/bin/perl -w

# A blast job is submitted to this script, and this script returns the blast
# result page with links. The actual code for making the links must be defined
# by the administrator in the subroutines below.



# Use this subroutine to change the alignment line into links. The first argument given
# to this routine is the first line of the sequence in the alignment. The second is
# the database searched against, eg 'test_na_db'
# eg. 
# "><a name = 654></a>Toxoplasma gondii | TGME49_112100 | Ca2+-ATPase"
# might return
# "><a href=/apiloc/gene/TGME49_112100>Toxoplasma gondii | TGME49_112100 | Ca2+-ATPase</a>"
sub replace_alignment_name_with_links {
  my ($name, $datalib, $hit_number) = @_;

  chomp $name;
  print "<input type='checkbox' name=alignment_seq_$hit_number id=checkbox_$hit_number value='$name'>";
  print "><a href='get_sequences.cgi?database=db/$datalib&hit_count=1&alignment_seq_1=$name'>$name</a>\n";
}


# Insert things at the beginning of the file.
# This is evn before the <html> tag, but eh,
# it works.
sub insert_at_beginning_of_alignments {
  print '<form action=get_sequences.cgi method=get>';
  print "\n\n";
}


# This routine is called after all the alignments have
# been printed. It is intended so that a 'select all' and
# 'get sequences button' might be inserted.
sub insert_after_alignments {
  my $number_of_hits = $_[0];
  my $datalib = $_[1];

  # Print javascript for select all button
  print <<END;
<script type=text/javascript>
function selectAll(){
END

  foreach $hit (1..$number_of_hits){
    print "document.getElementById('checkbox_$hit').checked = true;\n";
  }
  print <<END;
}
</script>
END

  # Print HTML form hidden inputs needed for "get selected sequences" button to work
  print "<input type=hidden name='hit_count' value=$number_of_hits />\n";
  print "<input type=hidden name='database' value=db/$datalib />\n";
  # Print select all button
  print "<input type=button onclick=\"javascript:selectAll()\" value='Select All' />";
  # Print get selected sequences button
  print "<input type=submit value='Get Selected Sequences'></form>\n";
}





use File::Temp qw/ tempfile /;

umask 0007;

# The CGI request is piped in through STDIN. This script needs
# to parse the CGI request, because the datalib parameter is
# required in the "replace_alignment_name_with_links" routine.
# However, it also needs to pipe the CGI request through STDIN
# to blast.REAL, so that the actual BLAST'ing can take place
#
# So the plan is to read STDIN into a file, then both parse that
# file for use here, and then pipe that file to blast.REAL

# Print header
print "Content-type: text/html\n\n";

# Copy STDIN into a file, and pipe it to blast.REAL
(undef, $cgi_file) = tempfile();
(undef, $out_file) = tempfile();
`export REQUEST_METHOD=POST; export BLASTDB=db; tee $cgi_file | ./blast.REAL >$out_file`;




# Parse the CGI file
open (CGI_FILE, $cgi_file) || die "Could not open cgi request file";

$datalib = undef;
# Manually parse the file
while (<CGI_FILE>){
  if (m/Content-Disposition: form-data; name="DATALIB"/){
    <CGI_FILE>; #skip blank line
    $datalib = <CGI_FILE>; #next line is the one we're after
    $datalib =~ s/\r//;
    $datalib =~ s/\n//;
  }
}



# Print the output from blast.REAL
open OUT, $out_file;
$hit_count = 0;
while(<OUT>){
  # eg. '><a name = 654></a>Toxoplasma gondii | TGME49_112100 | Ca2+-ATPase'
  if (m/(<a name \= .+?\>\<.a\>)(.+)/){
    # line contains an alignment description.
    $link = $1;
    $hit_name = $2;
    $hit_name =~ s/<\/a>//;

    # If this is the first alignment, insert extra bit
    if ($hit_count == 0){
      insert_at_beginning_of_alignments();
    }
    $hit_count += 1;

    # Insert thre new replacement text after
    # link from the description.
    print $link;
    replace_alignment_name_with_links($hit_name, $datalib, $hit_count);

  } elsif(m/<\/form>/) {
    # The default wwwblast appears to insert a late
    # ending to the form used for mouse over of the graphical
    # map. Unfortunately this plays havoc with other forms on
    # the page. So it is moved up in this elsif and the next.
    insert_after_alignments($hit_count, $datalib);
  } elsif (m/<input name=defline size=80 value="Mouse-over/) {
    # Add the extra </form> tag much closer to the top of the page
    print $_;
    print '</form>';
  } else {
    # normal line. Let it pass straight through to the user.
    print $_;
  }
}




