from jordan_qh.omega import UniversalDifferentialsDraft


def test_universal_differentials_draft_records_representing_property() -> None:
    draft = UniversalDifferentialsDraft("J", "A")

    assert "Omega_{J/A}" in draft.represents()
    assert draft.status == "definition pending"
