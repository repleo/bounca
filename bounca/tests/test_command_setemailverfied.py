from django.core.management import call_command


def test_command_setemailverified(db):
    # This command needs to be dropped, in favor of having a conditional
    # constraint.
    call_command("account_unsetmultipleprimaryemails")
