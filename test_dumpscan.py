from dumpscan import *

SampleFilename = "sample/svwiki-20140727-stub-meta-history.sample.xml.gz"

def test_sample_revision_count():
    assert 160 == len(list(parse_revisions(SampleFilename)))

def test_sample_page_titles():
    expected_titles = set([
        "Amager",
        "Abba (olika betydelser)",
    ])
    seen_titles = set()
    for revision in parse_revisions(SampleFilename):
        seen_titles.add(revision.page.title)
    assert seen_titles == expected_titles

def test_sample_frequent_contributors():
    from collections import Counter
    expected_most_common = set([
        ("Mainfoot", 8),
        ("VolkovBot", 7),
        ("E70", 7),
    ])
    counter = Counter()
    for revision in parse_revisions(SampleFilename):
        if revision.contributor.username:
            counter[revision.contributor.username] += 1
    most_common = set(counter.most_common(3))
    assert most_common == expected_most_common

def test_sample_revision_attributes():
    revision = parse_revisions(SampleFilename).next()
    assert revision.page.title == "Amager"
    assert revision.page.ns == 0
    assert revision.page.id == 1
    assert revision.id == 1
    assert revision.timestamp.year == 2001
    assert revision.contributor.username == "LinusTolke"
    assert revision.contributor.id == 0
    assert revision.comment == "*"
    assert revision.text.id == 1
    assert revision.text.bytes == 137
    assert revision.sha1 == "bgr2ap3ri2abor362xau00k4nasfqtj"
    assert revision.model == "wikitext"
    assert revision.format == "text/x-wiki"

def test_parse_datetime():
    rv = parse_datetime("2003-12-20T12:04:34Z")
    assert rv.year == 2003
    assert rv.month == 12
    assert rv.day == 20
    assert rv.hour == 12
    assert rv.minute == 4
    assert rv.second == 34
    
def test_parse_offset_datetime():
    rv = parse_datetime("2003-12-20T12:04:34+01:00")
    assert rv.year == 2003
    assert rv.month == 12
    assert rv.day == 20
    assert rv.hour == 11
    assert rv.minute == 4
    assert rv.second == 34
    
