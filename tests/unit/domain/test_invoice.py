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


def test_invoice_reconciles_unit_price_from_matching_price_component() -> None:
    """Real-world case: the model pasted the processing-fee total into unit_price."""
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "line_items": [
                {
                    "line_no": 1,
                    "quantity": {"value": "960", "unit": "PCS"},
                    "unit_price": {"amount": "1478.016", "currency": "USD"},
                    "amount": {"amount": "5443.008", "currency": "USD"},
                    "price_components": [
                        {
                            "label": "PROCESSING FEE",
                            "unit_price": {"amount": "1.5396", "currency": "USD"},
                            "amount": {"amount": "1478.016", "currency": "USD"},
                        },
                        {
                            "label": "MOTOR PRICE",
                            "unit_price": {"amount": "5.6698", "currency": "USD"},
                            "amount": {"amount": "5443.008", "currency": "USD"},
                        },
                    ],
                }
            ],
            "total_amount": {"amount": "5443.008", "currency": "USD"},
        }
    )

    line = invoice.line_items[0]
    assert line.unit_price is not None and line.unit_price.amount == Decimal("5.6698")
    assert line.amount is not None and line.amount.amount == Decimal("5443.008")
    assert invoice.warnings() == []


def test_invoice_reconciliation_falls_back_to_total_amount_match() -> None:
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "line_items": [
                {
                    "quantity": {"value": "10"},
                    "unit_price": {"amount": "999", "currency": "USD"},
                    "price_components": [
                        {"label": "fee", "unit_price": {"amount": "1"}, "amount": {"amount": "10"}},
                        {
                            "label": "goods",
                            "unit_price": {"amount": "4"},
                            "amount": {"amount": "40"},
                        },
                    ],
                }
            ],
            "total_amount": {"amount": "40", "currency": "USD"},
        }
    )

    line = invoice.line_items[0]
    assert line.unit_price is not None and line.unit_price.amount == Decimal("4")
    assert line.amount is not None and line.amount.amount == Decimal("40")


def test_invoice_reconciliation_leaves_consistent_or_componentless_lines_alone() -> None:
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "line_items": [
                {
                    "quantity": {"value": "2"},
                    "unit_price": {"amount": "5"},
                    "amount": {"amount": "10"},
                    "price_components": [
                        {"label": "x", "unit_price": {"amount": "1"}, "amount": {"amount": "2"}}
                    ],
                },
                {
                    "quantity": {"value": "2"},
                    "unit_price": {"amount": "7"},
                    "amount": {"amount": "99"},
                },
            ],
        }
    )

    assert invoice.line_items[0].unit_price is not None
    assert invoice.line_items[0].unit_price.amount == Decimal("5")
    assert invoice.line_items[1].amount is not None
    assert invoice.line_items[1].amount.amount == Decimal("99")
    assert len(invoice.warnings()) == 1


def test_hs_code_keeps_digits_and_rejects_implausible_values() -> None:
    items = Invoice.model_validate(
        {
            "line_items": [
                {"hs_code": "9401.61"},
                {"hs_code": "960"},
                {"hs_code": "HS 8501.10.00"},
                {"hs_code": None},
            ]
        }
    ).line_items

    assert [i.hs_code for i in items] == ["940161", None, "85011000", None]


def test_invoice_reconciliation_does_not_guess_when_no_component_matches_a_total() -> None:
    invoice = Invoice.model_validate(
        {
            "invoice_number": "INV-1",
            "line_items": [
                {
                    "line_no": 1,
                    "quantity": {"value": "10"},
                    "unit_price": {"amount": "999"},
                    "amount": {"amount": "50"},
                    "price_components": [
                        {"label": "a", "unit_price": {"amount": "1"}, "amount": {"amount": "10"}},
                        {"label": "b", "unit_price": {"amount": "4"}, "amount": {"amount": "40"}},
                    ],
                }
            ],
            "total_amount": {"amount": "70"},
        }
    )

    line = invoice.line_items[0]
    assert line.unit_price is not None and line.unit_price.amount == Decimal("999")
    assert line.amount is not None and line.amount.amount == Decimal("50")
    assert any(w.startswith("line 1: quantity x unit_price") for w in invoice.warnings())
