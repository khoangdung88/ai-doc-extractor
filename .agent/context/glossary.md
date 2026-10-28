# Domain glossary — shipping & trade documents

Use these exact names in schemas, prompts, and code. Add terms here before using them.

## Documents
| Term | Meaning |
|---|---|
| **Commercial Invoice** | Seller → buyer bill for goods: parties, invoice no/date, line items (description, HS code, qty, unit price, amount), totals, currency, incoterm, payment terms. |
| **Packing List** | Lists how goods are packed: packages (cartons/pallets), marks & numbers, per-package contents, net/gross weight, dimensions/volume. Often mirrors invoice line items without prices. |
| **Booking Confirmation** | Carrier/forwarder confirms a shipment booking: booking no., vessel/voyage, POL/POD, ETD/ETA, container type/qty, cut-off times (SI, VGM, CY), shipper, pickup/return depots. |
| Bill of Lading (B/L) | Transport contract & receipt (future doc type). |
| Certificate of Origin (CO) | Origin certification (future). |

## Parties
| Term | Meaning |
|---|---|
| `shipper` / `exporter` / `seller` | Party sending the goods (invoice: seller; booking: shipper). |
| `consignee` / `buyer` | Party receiving the goods. |
| `notify_party` | Party to notify on arrival. |
| `carrier` | Shipping line. `forwarder`: freight forwarder arranging transport. |

## Shipping fields
| Abbrev | Full | Notes |
|---|---|---|
| `pol` | Port of Loading | Use UN/LOCODE when present (e.g. `VNSGN`), else name. |
| `pod` | Port of Discharge | |
| `etd` / `eta` | Estimated time of departure / arrival | ISO date, timezone unknown → date only. |
| `vessel`, `voyage` | Vessel name, voyage number | |
| `container_type` | e.g. `20GP`, `40HC`, `40RF` | Normalise to ISO size/type codes. |
| `si_cutoff`, `vgm_cutoff`, `cy_cutoff` | Shipping instruction / verified gross mass / container yard cut-offs | |
| `incoterm` | FOB, CIF, EXW, DAP, … | 3-letter code + named place. |
| `hs_code` | Harmonised System code | Keep digits only, 6–10 chars. |
| `marks_and_numbers` | Shipping marks printed on packages | Free text. |
| `gross_weight` / `net_weight` | With unit (`KG`/`LB`). Gross includes packaging. |
| `volume` | `CBM` (m³) or `CFT`. | |

## Extraction semantics
- **Never infer** values not on the document (e.g. do not compute totals unless the document shows them;
  put computed checks in `warnings`).
- Multiple currencies on one document → capture per line; totals currency is the document currency.
- Line items keep document order.
