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
}


def main() -> None:
    for relative, lines in SAMPLES.items():
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        doc = pymupdf.open()
        page = doc.new_page()
        y = 72
        for line in lines:
            page.insert_text((50, y), line, fontsize=10, fontname="cour")
            y += 15
        doc.save(target, garbage=4, deflate=True)
        doc.close()
        print(f"wrote {target.relative_to(ROOT.parents[2])} ({target.stat().st_size} B)")


if __name__ == "__main__":
    main()
