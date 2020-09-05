# Markdown to HTML Parser

A simple parser from Markdown to HTML written in Python. This program came into
existence as a school project from Programming I, which is a course taught as
an introductory course on programming at Charles University in Prague. I took
the inspiration from http://markdownguide.org/ and I recommend writing your MD
code according to their recommendations, otherwise you may happen to encounter
some weird and unexpected behaviour.

## Features

First version of this program supports only basic HTML tags. List of all supported
MD and HTML tags can be found below.

* Headings (&#x3C;h1&#x3E;..&#x3C;h6&#x3E;)
* Paragraphs (&#x3C;p&#x3E;)
* Links (&#x3C;a href=""&#x3E;&#x3C;/a&#x3E;)
* Images (&#x3C;img src="" alt=""&#x3E;)
* Ordered & Unordered Lists (&#x3C;ul&#x3E; & &#x3C;ol&#x3E;)
* Blockquotes (&#x3C;blockquote&#x3E;)
* Code (&#x3C;code&#x3E;)
* Emphasise (&#x3C;strong&#x3E; & &#x3C;em&#x3E;)
* Strikethrough (&#x3C;del&#x3E;)

## Installation & Usage

1. Open Terminal.
2. Navigate into the folder where you want to clone this repository.
3. Clone this repository into your own computer.
4. Finally, run `python main.py` and follow instructions on screen.

## Author
Radovan Haluška, radovan.haluska1@gmail.com
