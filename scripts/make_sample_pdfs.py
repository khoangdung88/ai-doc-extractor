"""Generate synthetic sample PDFs into tests/fixtures/documents/.

Run: uv run python scripts/make_sample_pdfs.py
"""

from __future__ import annotations

from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "documents"

SAMPLES: dict[str, list[str]] = {
    "invoice/synthetic_invoice_01.pdf": [
        "COMMERCIAL INVOICE",
        "Invoice No.: INV-2026-0001            Date: 2026-03-02",
        "Seller: ACME EXPORT CO., LTD, 1 Example Road, Ho Chi Minh City, Vietnam",
        "Buyer: SAMPLE IMPORTS GMBH, 2 Beispielstrasse, 20095 Hamburg, Germany",
        "Incoterm: FOB HO CHI MINH            Payment: T/T 30 days",
        "Port of Loading: HO CHI MINH (VNSGN)  Port of Discharge: HAMBURG (DEHAM)",
        "No  Description      HS Code   Qty      Unit Price   Amount (USD)",
        "1   Wooden chairs    940161    100 PCS  25.00        2,500.00",
        "2   Wooden tables    940360    20 PCS   150.00       3,000.00",
        "TOTAL: USD 5,500.00",
    ],
    "invoice/synthetic_processing_invoice_01.pdf": [
        "INVOICE",
        "Invoice No: SAMPLE-PI-0001        Date: 2026-03-02",
        "Seller: EXAMPLE PRECISION VIETNAM CO., LTD, Lot 1, Example Ind. Park, Hanoi, Vietnam",
        "Sold to: EXAMPLE PRECISION INC., 1-2-3 Example-cho, Nagano, Japan",
        "Shipped to: SAMPLE ELECTRONICS (THAILAND) CO., LTD, 99 Example Estate, Chonburi, Thailand",
        "Processing Contract No: PC-2017-01    Payment term: T/T 30 days after invoice",
        "Delivery term: FOB HANOI    Shipped per: AIR FREIGHT    Ship on board: 2026-03-03",
        "No  Description  Part No     Qty (PCS)  Unit price (USD)  Amount (USD)  Unit price (USD)",
        "                                        (processing fee)  (payment)     (material)",
        "    Total (USD) (payment & no payment)",
        "1   Micro motor  8X-000A001  960        1.5000            1,440.00      5.5000",
        "    5,280.00",
        "TOTAL                                   960               1,440.00      5,280.00",
        "TOTAL INVOICE AMOUNT: USD 5,280.00",
        "Total packages: 4 Cartons   Net weight: 9.7 KG   Gross weight: 25.5 KG",
        "Country of origin: Vietnam",
    ],
    "packing_list/synthetic_packing_list_01.pdf": [
        "PACKING LIST",
        "P/L No.: PL-2026-0001   Invoice No.: INV-2026-0001   Date: 2026-03-02",
        "Shipper: ACME EXPORT CO., LTD        Consignee: SAMPLE IMPORTS GMBH",
        "Vessel/Voyage: EXAMPLE VESSEL / 012W  Container: MSKU1234567",
        "Marks: SAMPLE / HAMBURG / C/NO. 1-30",
        "Pkg No   Description     Qty      N.W. (KG)  G.W. (KG)  Meas (cm)",
        "CTN 1-20 Wooden chairs   100 PCS  800.0      900.0      60x60x90",
        "CTN 21-30 Wooden tables  20 PCS   600.0      680.0      120x80x75",
        "TOTAL: 30 CTNS   N.W. 1,400.0 KG   G.W. 1,580.0 KG   10.5 CBM",
    ],
    "booking_confirmation/synthetic_booking_01.pdf": [
        "BOOKING CONFIRMATION",
        "Booking No.: BKG123456789        Date: 2026-02-20",
        "Carrier: EXAMPLE LINE            Shipper: ACME EXPORT CO., LTD",
        "Vessel/Voyage: EXAMPLE VESSEL / 012W",
        "POL: HO CHI MINH (VNSGN)   POD: HAMBURG (DEHAM)   ETD: 2026-03-05   ETA: 2026-04-10",
        "Equipment: 2 x 40HC         Commodity: WOODEN FURNITURE",
        "SI Cut-off: 2026-03-02 12:00   VGM Cut-off: 2026-03-03 12:00",
        "CY Cut-off: 2026-03-03 18:00",
        "Pickup depot: CAT LAI DEPOT   Return: CAT LAI TERMINAL",
    ],
    "booking_confirmation/synthetic_air_booking_01.pdf": [
        "BOOKING CONFIRMATION - AIR EXPORT",
        "Issued by: EXAMPLE FORWARDING (VIETNAM) CO., LTD        Date: 2026-02-20",
        "Shipper: ACME EXPORT CO., LTD",
        "Consignee: SAMPLE IMPORTS (THAILAND) CO., LTD",
        "Shipper Ref: INV-2026-0001",
        "MAWB No: 123-45678901        HAWB No: 987654321012",
        "Flight details: XY123   2026-03-05   SGN-BKK   09:30 - 11:10",
        "Airport of destination: BKK",
        "Quantity: 4 CTNS / 25.5 KGS / 0.25 CBM    Chargeable weight: 42.0 KG",
        "Cargo cut-off time: 22:00 2026-03-04",
        "Terminal: EXAMPLE CARGO TERMINAL   Warehouse: 01A",
        "Remark: Please present this booking confirmation at the terminal.",
    ],
}

# Multi-page files mixing document types (auto-detection spec 0004). Values are page lists;
# single-type pages are reused from SAMPLES so text never drifts.
MULTI_PAGE: dict[str, list[list[str]]] = {
    "combined/synthetic_combined_01.pdf": [
        SAMPLES["invoice/synthetic_invoice_01.pdf"],
        SAMPLES["packing_list/synthetic_packing_list_01.pdf"],
        [
            "COVER LETTER",
            "Dear Sir/Madam,",
            "Please find enclosed the commercial invoice and packing list for the",
            "above-mentioned shipment. Do not hesitate to contact us for any question.",
            "Best regards, ACME EXPORT CO., LTD",
        ],
    ],
}


def _write_pdf(target: Path, pages: list[list[str]]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open()
    for lines in pages:
        page = doc.new_page()
        y = 72
        for line in lines:
            page.insert_text((50, y), line, fontsize=10, fontname="cour")
            y += 15
    doc.save(target, garbage=4, deflate=True)
    doc.close()
    print(f"wrote {target.relative_to(ROOT.parents[2])} ({target.stat().st_size} B)")


def main() -> None:
    for relative, lines in SAMPLES.items():
        _write_pdf(ROOT / relative, [lines])
    for relative, pages in MULTI_PAGE.items():
        _write_pdf(ROOT / relative, pages)


if __name__ == "__main__":
    main()
