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


def test_invoice_warns_when_unit_price_is_actually_a_line_total() -> None:
    """Regression: a model copied a column total (1478.016) into unit_price."""
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "line_items": [
                {
                    "line_no": 1,
                    "quantity": {"value": "960", "unit": "PCS"},
                    "unit_price": {"amount": "1478.016", "currency": "USD"},
                    "amount": {"amount": "5443.008", "currency": "USD"},
                }
            ],
            "total_amount": {"amount": "5443.008", "currency": "USD"},
        }
    )

    assert any(w.startswith("line 1: quantity x unit_price") for w in invoice.warnings())


def test_invoice_tolerates_rounded_line_amounts() -> None:
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "line_items": [
                {
                    "quantity": {"value": "3"},
                    "unit_price": {"amount": "3.333", "currency": "USD"},
                    "amount": {"amount": "10.00", "currency": "USD"},
                }
            ],
        }
    )

    assert invoice.warnings() == []


def test_invoice_parses_price_components_and_shipment_fields() -> None:
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "shipped_per": "AIR FREIGHT",
            "total_packages": "4",
            "line_items": [
                {
                    "part_number": "8X-000A001",
                    "price_components": [
                        {"label": "processing fee", "unit_price": {"amount": "1.5"}},
                        {"label": "material", "unit_price": {"amount": "5.5"}},
                    ],
                }
            ],
        }
    )

    assert invoice.total_packages == 4
    assert [c.label for c in invoice.line_items[0].price_components] == [
        "processing fee",
        "material",
    ]
    assert invoice.line_items[0].part_number == "8X-000A001"
