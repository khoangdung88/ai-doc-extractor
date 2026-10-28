import pytest
from pydantic import ValidationError

from docext.domain.booking_confirmation import BookingConfirmation


def test_booking_warns_when_eta_before_etd() -> None:
    booking = BookingConfirmation.model_validate(
        {"booking_number": "BK1", "etd": "2026-01-10", "eta": "2026-01-05"}
    )

    assert "eta is before etd" in booking.warnings()


def test_booking_parses_containers_and_cutoffs() -> None:
    booking = BookingConfirmation.model_validate(
        {
            "booking_number": "BK1",
            "si_cutoff": "2026-01-08T12:00:00",
            "containers": [{"container_type": "40HC", "quantity": 2}],
        }
    )

    assert booking.containers[0].quantity == 2
    assert booking.si_cutoff is not None and booking.si_cutoff.hour == 12


def test_air_booking_identified_by_awb_does_not_warn_about_booking_number() -> None:
    booking = BookingConfirmation.model_validate(
        {
            "transport_mode": "air",
            "mawb_number": "738-12345678",
            "hawb_number": "620212000000",
            "flight_number": "VN611",
            "pieces": 4,
            "cargo_cutoff": "2026-10-02T22:00:00",
        }
    )

    assert booking.warnings() == []
    assert booking.pieces == 4


def test_booking_without_any_identifier_warns() -> None:
    assert "booking_number missing" in BookingConfirmation().warnings()


def test_air_booking_warns_on_bad_mawb_and_containers() -> None:
    booking = BookingConfirmation.model_validate(
        {
            "transport_mode": "air",
            "mawb_number": "73812345678",
            "containers": [{"container_type": "40HC", "quantity": 1}],
        }
    )

    warnings = booking.warnings()
    assert "mawb_number is not in NNN-NNNNNNNN format" in warnings
    assert "containers listed on an air booking" in warnings


def test_sea_booking_warns_on_air_fields() -> None:
    for air_field in ("flight_number", "mawb_number", "hawb_number"):
        booking = BookingConfirmation.model_validate(
            {"booking_number": "BK1", "transport_mode": "sea", air_field: "X1"}
        )

        assert "air waybill / flight on a sea booking" in booking.warnings(), air_field


def test_transport_mode_is_restricted() -> None:
    with pytest.raises(ValidationError):
        BookingConfirmation.model_validate({"transport_mode": "space"})


def test_booking_moves_mawb_shaped_hawb_and_uses_hawb_as_booking_number() -> None:
    """Real-world case: model put the MAWB into hawb_number and left booking_number empty."""
    booking = BookingConfirmation.model_validate(
        {"transport_mode": "air", "hawb_number": "738-08558561"}
    )
    assert booking.mawb_number == "738-08558561"
    assert booking.hawb_number is None
    assert booking.booking_number is None

    booking = BookingConfirmation.model_validate(
        {"transport_mode": "air", "booking_number": "738-08558561", "hawb_number": "620212646355"}
    )
    assert booking.mawb_number == "738-08558561"
    assert booking.booking_number == "620212646355"
    assert booking.warnings() == []


def test_booking_keeps_explicit_identifiers() -> None:
    booking = BookingConfirmation.model_validate(
        {"booking_number": "BKG1", "mawb_number": "738-00000000", "hawb_number": "738-11111111"}
    )

    assert booking.booking_number == "BKG1"
    assert booking.mawb_number == "738-00000000"
    assert booking.hawb_number == "738-11111111"


def test_sea_booking_number_shaped_like_mawb_is_kept() -> None:
    booking = BookingConfirmation.model_validate(
        {"transport_mode": "sea", "booking_number": "123-45678901"}
    )

    assert booking.booking_number == "123-45678901"
    assert booking.mawb_number is None
    assert booking.warnings() == []


def test_booking_number_duplicating_mawb_falls_back_to_hawb() -> None:
    booking = BookingConfirmation.model_validate(
        {
            "transport_mode": "air",
            "booking_number": "738-08558561",
            "mawb_number": "738-08558561",
            "hawb_number": "620212646355",
        }
    )

    assert booking.mawb_number == "738-08558561"
    assert booking.booking_number == "620212646355"
