from decimal import Decimal

from docext.domain.invoice import Invoice


def test_invoice_all_null_is_valid() -> None:
    invoice = Invoice.model_validate({})

    assert invoice.invoice_number is None
    assert invoice.line_items == []


def test_invoice_warns_when_line_sum_differs_from_total() -> None:
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "line_items": [
                {"amount": {"amount": "60", "currency": "USD"}},
                {"amount": {"amount": "30", "currency": "USD"}},
            ],
            "total_amount": {"amount": "100", "currency": "USD"},
        }
    )

    warnings = invoice.warnings()

    assert any("differs from total_amount" in w for w in warnings)
    assert invoice.total_amount is not None
    assert invoice.total_amount.amount == Decimal("100")


def test_invoice_no_warning_when_consistent() -> None:
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "line_items": [{"amount": {"amount": "100.00", "currency": "USD"}}],
            "total_amount": {"amount": "100", "currency": "USD"},
        }
    )

    assert invoice.warnings() == []
