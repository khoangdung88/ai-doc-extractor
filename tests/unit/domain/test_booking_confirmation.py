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
