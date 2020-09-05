# Description of the algorithm used

In the creation of the algorithm, I have taken the inspiration from the
'Divide and Conquer' algoritms. Altough, this project does not tackle
any problem associated with sorting, I would still go with this title.

The main idea of this algorithm is to divided the whole text into several,
more processable chunks of text. Each chunk of the text is then processed
separately, therefore the structure of the original text is preserved.
After each of the chunks is processed, I glue them back together and
prepare for the output. Before I describe how the processing of each chunk
looks like, I need to shed some light on how I categorized the MD tags.
I divided them into two separate categories. The first one being the
'first_level_tags' which are basically tags which occur solely at the
beginning of the line. On the other hand, 'second_level_tags' occur mainly
within the line itself, i.e. inside the 'first_level_tags'.

Now, to the processing itself. Due to the fact, that 'code' and 'ol' MD
tags are hard to detect and replace along with other 'first_level_tags',
I had to first detect them separately and mark them. The marking is necessary,
in order to be able to replace them, along with other tags. I used separate
detection and replacement for the links and images as well. These tags are
unique each time and their appearance cannot be foreseen. For this reason,
I have used Regular Expressions to parse the whole MD link/image tag and
replace with the corresponding HTML tag. After the successful detection
and marking, I proceed with the replacing. All of the 'first_level_tags' are
replaced with the HTML tags. Now, I replace the 'second_level_tags' and finally
only the correction of compound tags happens. Correction is necessary, in order
to create the right closing tag. E.g. '\<pre>\<code>\' has the following
format '\</pre>\</code>' after the replacements, which is wrong. So the
correction basically swap the two closing tags to achieve '\</code>\</pre>'
format.

# Program flow

I divided the program into 3 separate modules. Each modules is responsible
for one of the tasks:

   * Getting the input from the user.
   * Processing the user's input.
   * Printing the formatted text to the output.

The most difficult and confusing part of the program is the middle one.
Therefore, I will describe the main structure and flow of the program.

| The 'DataController' receives data from the 'InputController'.
| Advanced preparation of the raw data occurs here.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Removing blank lines duplicates.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Converting into an array.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parsing link references.
| Splitting into the chunks.
| Chunk processing.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Preprocessing.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Processing 'code' and 'ol' tags.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Processing 'a' and 'img' tags.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Processing 'first_level_tags'.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Processing 'second_level_tags'.
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Correction
| Serve the formatted data to the 'OutputController'.

The individual methods descriptions are incorporated into the Python code in the
form of DocComments.
