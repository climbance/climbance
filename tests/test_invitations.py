import pytest
from commands import connected, run_cli

from climb.log import Role, invitations_held, invite, invited, withdraw


def test_an_invited_email_is_matched_whatever_its_case(database):
    """A provider hands back an email in whatever case its account holds."""
    invite(database, "Solver@Example.com")

    assert invited(database, "solver@EXAMPLE.com")
    assert not invited(database, "other@example.com")


def test_inviting_an_email_twice_holds_one_invitation(database):
    invite(database, "solver@example.com")
    invite(database, "SOLVER@example.com")

    assert invitations_held(database) == [("solver@example.com", Role.LEARNER)]


def test_inviting_again_sets_the_role_either_way(database):
    """An author is invited as any user, and set back by inviting again."""
    invite(database, "solver@example.com")
    invite(database, "solver@example.com", Role.AUTHOR)
    assert invitations_held(database) == [("solver@example.com", Role.AUTHOR)]

    invite(database, "solver@example.com")
    assert invitations_held(database) == [("solver@example.com", Role.LEARNER)]


def test_a_withdrawn_invitation_lets_nobody_in(database):
    invite(database, "solver@example.com")

    assert withdraw(database, "Solver@example.com")
    assert not invited(database, "solver@example.com")
    assert not withdraw(database, "solver@example.com")


def test_the_terminal_invites_lists_and_withdraws(database, monkeypatch, capsys):
    connected(database, monkeypatch)

    run_cli(monkeypatch, "invite", "add", "Solver@Example.com")
    run_cli(monkeypatch, "invite", "add", "--author", "author@example.com")
    run_cli(monkeypatch, "invite", "list")
    run_cli(monkeypatch, "invite", "remove", "solver@example.com")
    run_cli(monkeypatch, "invite", "remove", "author@example.com")
    run_cli(monkeypatch, "invite", "list")

    assert capsys.readouterr().out.splitlines() == [
        "invited solver@example.com as learner",
        "invited author@example.com as author",
        "author@example.com  author",
        "solver@example.com  learner",
        "withdrew solver@example.com",
        "withdrew author@example.com",
        "no email is invited",
    ]


def test_withdrawing_an_email_never_invited_says_so(database, monkeypatch, capsys):
    connected(database, monkeypatch)

    with pytest.raises(SystemExit) as exit_info:
        run_cli(monkeypatch, "invite", "remove", "nobody@example.com")

    assert exit_info.value.code == 1
    assert "never invited" in capsys.readouterr().err
