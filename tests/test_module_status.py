from climb.knowledge.authoring.status import Written, markdown, topics


def course(root):
    (root / "concepts" / "t").mkdir(parents=True)
    (root / "banks" / "t").mkdir(parents=True)
    (root / "course.toml").write_text('[[topic]]\nslug = "t"\ntitle = "Topic"\nsubs = ["a", "b"]\n')
    (root / "concepts" / "t" / "a.toml").write_text(
        '[[concept]]\nid = "c0"\nlevel = 0\n\n[[concept]]\nid = "c1"\nlevel = 1\n'
    )
    (root / "banks" / "t" / "a.toml").write_text(
        '[[q]]\nid = "q1"\nconcept = "c0"\n\n[[q]]\nid = "q2"\nconcept = "c0"\n\n'
        '[[q]]\nid = "q3"\nconcept = "c1"\n'
    )
    return root


def test_a_level_counts_the_concepts_at_it_and_their_questions(tmp_path):
    """A subtopic is written at a level when its concept file holds a concept
    there, and a question counts at its concept's level."""
    [topic] = topics(course(tmp_path))

    assert [s.levels for s in topic.subtopics] == [{0: Written(1, 2), 1: Written(1, 1)}, {}]
    assert (topic.done(0), topic.done(1), topic.done(2)) == (1, 1, 0)


def test_the_page_tallies_each_level_of_a_topic(tmp_path):
    """The tally STATUS.md shows per level, and a dash where nothing is
    written."""
    page = markdown("m", topics(course(tmp_path)))

    assert "L0 1 of 2, L1 1 of 2, L2 0 of 2, L3 0 of 2" in page
    assert "| a | 1 / 2 | 1 / 1 | — | — |" in page
    assert "| b | — | — | — | — |" in page


def test_a_level_recorded_as_empty_counts_as_written(tmp_path):
    """A subtopic with nothing at a level keeps no topic from being finished."""
    root = course(tmp_path)
    (root / "concepts" / "t" / "b.toml").write_text(
        '[[empty]]\nlevel = 3\nreason = "Nothing at this depth."\n'
    )
    [topic] = topics(root)

    assert topic.subtopics[1].levels == {3: Written(0, 0, "Nothing at this depth.")}
    assert topic.done(3) == 1
    assert "| b | — | — | — | empty |" in markdown("m", [topic])
