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
    booking = BookingConfirmation.model_validate(
        {"booking_number": "BK1", "transport_mode": "sea", "flight_number": "VN611"}
    )

    assert "air waybill / flight on a sea booking" in booking.warnings()


def test_transport_mode_is_restricted() -> None:
    with pytest.raises(ValidationError):
        BookingConfirmation.model_validate({"transport_mode": "space"})
