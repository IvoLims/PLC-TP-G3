# Trabalho Prático 1

## BibTex format

### Entries

A BibTeX entry consists of the **type**, a **citation-key** and a number of **tags** which define various characteristics of the specific BibTeX entry[^format].

Type
  : word after @

We have a total of 17 entry types, where 14 specify the type of publication and 3 have use specific to BibTex.

Entries used are not case sensitive^[https://tex.stackexchange.com/questions/163687/is-there-a-preferred-capitalization-style-for-reference-types-in-bibtex-biblatex].

The documentation says BibTeX-files may contain four different types of entries: @string, @preamble, @comment and Entries (e.g. @article, @book, etc)[^format]. This may make ambigous the difference between type of entry and entry type. Just assume 4 types of entry and 17 entry types, where 14 belong to one type of entry (which is named entry).

Note that:

@string
  : defines abbreviations which can later be used in a tag.

@preamble
  : defines how special text should be formatted.

@comment
  : for comments not taken in regard by BibTeX.

Entries
  : each declares a single reference to a type of publication.

There are 14 types of publication^[https://www.bibtex.com/e/entry-types/], that is, 14 entries of the type entry:

```txt
@article
@book
@booklet
@conference
@conference
@inbook
@incollection
@inproceedings
@manual
@mastersthesis
@misc
@phdthesis
@proceedings
@techreport
@unpublished
```

Citation-key
  : First word after {

Tag
  : A BibTeX tag is specified by its **name followed by an equals-sign and the content**. The tag's name **is not case-sensitive**. The **content needs to be enclosed by either curly braces or quotation-marks**. Which form of enclosure is used is depending on the user's taste, and both can be applied together in a single BibTeX entry, but there is one difference between those two methods: **When quotation-marks are used, string concatenation using # is possible, but not when braces are used.**[^format]

[^format]: http://www.bibtex.org/Format/