import re as regex


class DataController:
    def __init__(self, file_name='./input.txt'):
        self.file_name = file_name
        self.link_references_regex = regex.compile(
            r'(\[[\S\s]+\])\:[\s]+\<?((http|https)\:\/\/'
            r'?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.[a-zA-Z]'
            r'{2,6}[a-zA-Z0-9\.\&\/\?\:@\-_=#]*)\>?'
        )
        self.first_level_tags = {
            '> ': '<blockquote>',
            '###### ': '<h6>',
            '##### ': '<h5>',
            '#### ': '<h4>',
            '### ': '<h3>',
            '## ': '<h2>',
            '# ': '<h1>',
            '- ': '<ul>',
            '* ': '<ul>',
            '+ ': '<ul>',
            '!OL!': '<ol>',
            '!CODE!': '<pre><code>'
        }
        self.second_level_tags = {
            '***': '<strong><em>',
            '**_': '<strong><em>',
            '*__': '<strong><em>',
            '___': '<strong><em>',
            '__*': '<strong><em>',
            '_**': '<strong><em>',
            '~~': '<del>',
            '**': '<strong>',
            '__': '<strong>',
            '*': '<em>',
            '_': '<em>',
            '`': '<code>'
        }
        self.used_second_level_tags = set()
        self.links = dict()

        with open(self.file_name, 'r') as input_file:
            self.source_file_contents = input_file.read()

        self.__remove_blank_line_duplicates()
        self.__convert_to_array()
        self.__process_link_references()

    def __remove_blank_line_duplicates(self):
        """
        Trim redundant whitespaces between blocks of text;
        Leave only one empty line between blocks of text;
        """

        source = regex.sub(r'\n\s*\n', '\n\n', self.source_file_contents)
        self.source_file_contents = source.strip()

    def __convert_to_array(self):
        """
        Convert the string representation of the source file
        into the array representation;
        Reverse the array, so that we can use .pop() method
        with time complexity O(1);
        """

        self.source_file_contents = list(
            reversed(self.source_file_contents.split('\n'))
        )

    def __process_link_references(self):
        """
        Process second part of a link, if 'Reference-Style Link' is used;
        'Reference-Style Link' may look like this:
            '[1]: <https://www.google.com>' or '[1]: https://www.google.com';
        """

        for index, line in enumerate(self.source_file_contents):
            if regex.search(self.link_references_regex, line):
                line = self.__extract_link_references(line)
                self.source_file_contents[index] = line

    def __extract_link_references(self, line):
        """
        Separate the key and the link part of the line;
        Create '<a href=""></a>' with the right link;
        Store the 'KEY: LINK' value in the dictionary;
        Remove that reference afterwards, by setting the line to '';

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        line : str
            Returns only an empty string, so that
            it won't end up in the resulting HTML code;
        """

        line = line.strip()
        matched_parts = regex.match(self.link_references_regex, line)
        key = matched_parts.group(1)
        link = matched_parts.group(2)
        tag = f'<a href="{link}">!INNERTEXT!</a>'
        self.links[key] = tag
        return ''

    def __split_into_chunks(self):
        """
        Split the whole file into smaller, processable chunks;
        Splitting occurs on '', so we basically process one block at the time;

        RETURNS
        -------
        new_data : list
            Contains newly parsed source file;
        """

        new_data = []
        while self.source_file_contents:
            chunk = []
            line = self.source_file_contents.pop()
            chunk.append(line)
            while True:
                if not self.source_file_contents:
                    break
                line = self.source_file_contents.pop()
                if line == '':
                    break
                chunk.append(line)
            if chunk == ['']:
                continue
            chunk = self.__process_chunk(chunk)
            new_data.append(chunk)
        return new_data

    def __process_chunk(self, chunk):
        """
        Process one chunk after another;
        All the heavy work is done here;
        Follow functions to learn more about what's happening;

        PARAMETERS
        ----------
        chunk : list
            Contains chunk of text which we'll be processing;

        RETURNS
        -------
        chunk : list
            Contains newly created chunk;
        """

        for index, line in enumerate(chunk):
            line = self.__process_trailing_whitespaces(line)
            line = self.__process_trailing_numbers(line)
            line = self.__process_inline_link_tag(line)
            line = self.__process_inline_link_tag(line, 'EmailOrWeb')
            line = self.__process_images(line)
            line = self.__inject_link_tags(line)
            chunk[index] = line

        chunk = self.__process_first_level_tags(chunk)

        for index, line in enumerate(chunk):
            line = self.__unlabel_line(line)
            line = self.__process_second_level_tags(line)
            line = self.__correct_tags(line)
            chunk[index] = line

        return chunk

    def __process_trailing_whitespaces(self, line):
        """
        Take care of trailing whitespaces by either removing them
        or by creating a place for '<code>' tag;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        spaces, tabs = self.__count_whitespaces(line)
        spaces, line = self.__convert_tabs_to_spaces(spaces, tabs, line)
        if spaces < 4:
            line = line.strip()
        else:
            line = self.__create_special_tag_marking(line, '!CODE!', 4)
        return line

    def __process_trailing_numbers(self, line):
        """
        Take care of trailing numbers by creating a place for '<ol>' tag;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        if regex.match(r'^[1-9]+\.\ ', line):
            line = self.__create_special_tag_marking(line, '!OL!', 3)
        return line

    def __process_images(self, line):
        """
        Process MD image tag;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        return self.__process_inline_link_tag(line, 'Image')

    def __process_inline_link_tag(self, line, type_of_link='Inline'):
        """
        Handle both Images and Inline Links, depending on value
        in 'type_of_link' variable;
        Extract important parts from the given line, like URI,
        email addresses, source file paths and AltText;
        Build up the appropriate HTML tag with given data;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;
        type_of_link : str
            Contains what type of data we'll be processing;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        if type_of_link == 'Inline':
            regex_patterns = [
                regex.compile(
                    r'(\[[\S\s]+\])\ *\(((http|https)\:\/\/'
                    r'?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.[a-zA-Z]'
                    r'{2,6}[a-zA-Z0-9\.\&\/\?\:@\-_=#]*)\)'
                )
            ]
        elif type_of_link == 'Image':
            regex_patterns = [
                regex.compile(r'\!\[([\S\s]*)\]\(([\S\s]*)\)')
            ]
        else:
            regex_patterns = [
                regex.compile(
                    r'\<((http|https)\:\/\/?[a-zA-Z0-9\.\/\?\:@\-_=#]'
                    r'+\.[a-zA-Z]{2,6}[a-zA-Z0-9\.\&\/\?\:@\-_=#]*)\>'
                ),
                regex.compile(
                    r'\<(\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+)\>'
                )
            ]

        for regex_pattern in regex_patterns:
            if regex.search(regex_pattern, line):
                matched_parts = regex.search(regex_pattern, line)
                if type_of_link == 'Inline':
                    inner_text = matched_parts.group(1).strip('[').strip(']')
                    link = matched_parts.group(2)
                    tag = f'<a href="{link}">{inner_text}</a>'
                elif type_of_link == 'Image':
                    alt_text = matched_parts.group(1)
                    source = matched_parts.group(2)
                    tag = f'<img src="{source}" alt="{alt_text}">'
                else:
                    link = matched_parts.group(1)
                    tag = f'<a href="{link}">{link}</a>'
                line = regex.sub(regex_pattern, tag, line)
        return line

    def __inject_link_tags(self, line):
        """
        Handle the correct replacement of MD link tag with HTML link tag;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        if regex.search(r'(\[[\S\s]+\])[ ]*(\[[\S\s]+\])*', line):
            for key in self.links:
                if key in line:
                    line = self.__inject_link_text(line, key).strip()
        return line

    def __inject_link_text(self, line, key):
        """
        Inject the correct link text between the opening and closing link tag;
        Replace MD Tag with HTML Tag;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;
        key : str
            Contains text reference to the link;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        key_index = line.find(key)
        start_point = key_index - 1
        while True:
            if line[start_point] == '[':
                break
            start_point -= 1
        substring = line[start_point:]
        end_point = substring.find(']')
        inner_link_text = substring[1:end_point]
        end_point = key_index + len(key) + 1
        tag = line[start_point:end_point]
        self.links[key] = self.links[key].replace(
            '!INNERTEXT!', inner_link_text
        )
        line = line.replace(tag, self.links[key])
        return line

    def __process_first_level_tags(self, chunk):
        """
        Process all of first level MD tags and replaces it by HTML tags;

        PARAMETERS
        ----------
        chunk : list
            Contains currently processed chunk;

        RETURNS
        -------
        chunk : list
            Contains newly created chunk;
        """

        for tag in self.first_level_tags:
            if self.__is_matching(chunk, tag):
                chunk = self.__label_chunk(
                    self.__convert_first_level_tags(chunk, tag)
                )
        if not self.__is_labeled(chunk):
            chunk = self.__process_unlabeled_chunk(chunk)

        return chunk

    def __process_second_level_tags(self, line):
        """
        Process all of second level MD tags and replaces it by HTML tags;

        PARAMETERS
        ----------
        line : str
            Contains currently processed line;

        RETURNS
        -------
        line : str
            Contains newly created line;
        """

        for tag in self.second_level_tags:
            if tag in line:
                how_many = line.count(tag)
                if how_many % 2 != 0:
                    continue
                self.used_second_level_tags.add(self.second_level_tags[tag])
                line = line.replace(tag, self.second_level_tags[tag])
        return line

    def __process_unlabeled_chunk(self, chunk):
        """
        Process the chunk which was previously not labeled;
        This essentially encloses the unlabeled chunk in '<p>' tag;
        Also label the chunk, just for the sake of consistency;

        PARAMETERS
        ----------
        chunk : list
            Contains currently processed chunk;

        RETURNS
        -------
        chunk : list
            Contains newly created chunk;
        """

        for index, line in enumerate(chunk):
            line = line + '<br>'
            chunk[index] = line

        chunk[0] = '<p>' + chunk[0]
        chunk[-1] = chunk[-1] + '</p>'
        chunk = self.__label_chunk(chunk)
        return chunk

    def __correct_tags(self, line):
        """
        Correct all faulty HTML tags after the '__replace_nth_occurence()';

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        for tag in self.used_second_level_tags:
            line = self.__replace_nth_occurence(
                line, tag, self.__create_closing_html_tag(tag)
            )
        return line

    def __replace_nth_occurence(self, line, tag, replacement):
        """
        Replace every second occurrence of given tag;
        Due to the reason that '__process_second_level_tags' method
        encloses every MD formatted text only in opening tags,
        we have to correct every second occurrence of the given tag;
        It finds the first occurrence of the tag and from index of the
        first occurrence, it then finds the second occurrence, which then
        replaces by the correct tag;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;
        tag : str
            Contains the tag which we'll be replacing;
        replacement : str
            Contains the closing tag, which will be inserted
            in the position of 'tag' parameter;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        find = line.find(tag)
        is_found = find != -1
        while is_found:
            find = line.find(tag, find + len(tag))
            if find == -1:
                break
            line = line[:find] + replacement + line[find + len(tag):]
            find = line.find(tag, find + len(tag))
            is_found = find != -1

        return line

    def __is_matching(self, chunk, tag):
        """
        Check if the right tag is present in the chunk;

        PARAMETERS
        ----------
        chunk : list
            Contains currently processed chunk;
        tag : str
            Contains currently tested tag;

        RETURNS
        -------
        value : bool
            Contains whether the chunk contains the right tag or not;
        """

        return all(elem[0:len(tag)] == tag for elem in chunk)

    def __convert_first_level_tags(self, chunk, tag):
        """
        Convert the first level MD tags into the HTML tags;
        First, the MD tag removal occurs, after which the
        HTML tag replacement takes place;
        For example: '# Heading Level 1' will be replaced by
        '<h1>Heading Level 1</h1>';

        PARAMETERS
        ----------
        chunk : list
            Contains currently processed chunk;
        tag : str
            Contains currently processed tag;

        RETURNS
        -------
        chunk : list
            Contains newly created chunk;
        """

        html_tag = self.first_level_tags[tag]
        if html_tag == '<blockquote>':
            for index, line in enumerate(chunk):
                line = line + '<br>'
                chunk[index] = line

        chunk = list(map(lambda elem: elem[len(tag):], chunk))
        if html_tag in ('<ul>', '<ol>'):
            chunk = [
                self.__enclose_in_html_tag(elem, '<li>') for elem in chunk
            ]
        chunk[0] = html_tag + chunk[0]
        chunk[-1] = chunk[-1] + self.__create_closing_html_tag(html_tag)
        return chunk

    def __enclose_in_html_tag(self, elem, tag):
        """
        Enclose the element in the opening and closing HTML tag;
        For example: 'Some random text.' will be enclosed in
        '<OpeningTag>Some random text.<ClosingTag>';

        PARAMETERS
        ----------
        elem : str
            Contains the element which will be enclosed in HTML tag;
        tag : str
            Contains currently processed tag;

        RETURNS
        -------
        elem : str
            Contains newly created element enclosed in HTML tag;
        """

        return tag + elem.strip() + self.__create_closing_html_tag(tag)

    def __create_closing_html_tag(self, tag):
        """
        Create a closing HTML tag from an opening HTML tag;
        If the opening tag is composite then tag switching also occurs;
        For example: '<pre><code>' will be replaced by '</code></pre>';

        PARAMETERS
        ----------
        tag : str
            Contains currently processed tag;

        RETURNS
        -------
        tag : str
            Contains newly created closing tag;
        """

        tag = tag.replace('<', '</')
        if tag.count('<') > 1:
            tag = tag.split('>')
            tag = tag[1] + '>' + tag[0] + '>'
        return tag

    def __label_chunk(self, chunk):
        """
        Label tag where the tag replacement has already occured, in order to
        be able to determine which chunk will be rendered as a paragraph;

        PARAMETERS
        ----------
        chunk : list
            Contains currently processed chunk;

        RETURNS
        -------
        chunk : list
            Contains newly created chunk;
        """

        chunk[0] = '!*!' + chunk[0]
        return chunk

    def __unlabel_line(self, line):
        """
        Unlabel the given line;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        if line[0:3] == '!*!':
            line = line[3:]
        return line

    def __is_labeled(self, chunk):
        """
        Check if the chunk was labeled or not, in order to be able
        to determine which chunk will be rendered as a paragraph;

        PARAMETERS
        ----------
        chunk : list
            Contains currently processed chunk;

        RETURNS
        -------
        value: bool
        """

        if chunk[0][0:3] == '!*!':
            return True
        return False

    def __count_whitespaces(self, line):
        """
        Count trailing whitespaces for a further processing;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        spaces, tabs : int, int
            Contains number of spaces or tabs, respectively;
        """

        spaces, tabs = 0, 0

        for char in line:
            if char == ' ':
                spaces += 1
            elif char == '\t':
                tabs += 1
            else:
                break

        return spaces, tabs

    def __convert_tabs_to_spaces(self, spaces, tabs, line):
        """
        Convert tabs to spaces;
        One tab is considered as 4 spaces;

        PARAMETERS
        ----------
        spaces, tabs : int, int
            Contains number of spaces or tabs, respectively;
        line : str
            Contains text which we'll be processing;

        RETURNS
        -------
        spaces : int
            Contains number of spaces;
        line : str
            Contains text which was processed;
        """

        line = line.replace('\t', '    ')
        spaces += tabs * 4
        return spaces, line

    def __create_special_tag_marking(self, line, marking, start_point):
        """
        Create a special tag marking for a further processing;

        PARAMETERS
        ----------
        line : str
            Contains text which we'll be processing;
        marking : str
            Contains a string which will be used as a special marking;
        start_point : int
            Contains how many characters should be replaced in an original line

        RETURNS
        -------
        line : str
            Contains text which was processed;
        """

        line = marking + line[start_point:]
        return line

    def convert_md_to_html(self):
        with open(self.file_name, 'w') as input_file:
            for chunk in self.__split_into_chunks():
                for line in chunk:
                    input_file.write(line + '\n')
