# Domain glossary — shipping & trade documents

Use these exact names in schemas, prompts, and code. Add terms here before using them.

## Documents
| Term | Meaning |
|---|---|
| **Commercial Invoice** | Seller → buyer bill for goods: parties, invoice no/date, line items (description, HS code, qty, unit price, amount), totals, currency, incoterm, payment terms. |
| **Packing List** | Lists how goods are packed: packages (cartons/pallets), marks & numbers, per-package contents, net/gross weight, dimensions/volume. Often mirrors invoice line items without prices. |
| **Booking Confirmation** | Carrier/forwarder confirms a shipment booking. Sea: booking no., vessel/voyage, POL/POD, ETD/ETA, container type/qty, cut-offs (SI, VGM, CY), depots. Air: MAWB/HAWB, flight, airports, cargo cut-off, terminal/warehouse, pieces/weight/volume. |
| Bill of Lading (B/L) | Transport contract & receipt (future doc type). |
| Certificate of Origin (CO) | Origin certification (future). |

## Parties
| Term | Meaning |
|---|---|
| `shipper` / `exporter` / `seller` | Party sending the goods (invoice: seller; booking: shipper). |
| `consignee` / `buyer` | Party receiving the goods. |
| `notify_party` | Party to notify on arrival. |
| `carrier` | Shipping line or airline operating the transport. `forwarder`: freight forwarder / agent arranging it (usually the issuer of a booking confirmation). |

## Shipping fields
| Abbrev | Full | Notes |
|---|---|---|
| `pol` | Port of Loading | Use UN/LOCODE when present (e.g. `VNSGN`), else name. |
| `pod` | Port of Discharge | |
| `etd` / `eta` | Estimated time of departure / arrival | ISO date, timezone unknown → date only. |
| `vessel`, `voyage` | Vessel name, voyage number | Sea only. |
| `transport_mode` | `sea`, `air`, `road`, `rail` | Derived from AWB/flight vs vessel/container vocabulary. |
| `mawb_number` / `hawb_number` | Master / House Air Waybill | MAWB is `NNN-NNNNNNNN` (airline prefix + 8 digits). HAWB is the forwarder's own number. |
| `flight_number` | Airline code + number, e.g. `VN611` | Flight line usually also carries date, `ORG-DST` IATA codes and times. |
| `cargo_cutoff` | Cargo / warehouse handover cut-off | Air bookings print a single cut-off; do not map it to SI/VGM/CY. |
| `terminal` | Handling terminal / warehouse where cargo is delivered | e.g. `NCTS / 01B1A02`. |
| `pieces` | Number of packages booked | From lines like `4 CTNS / 25.5 KGS / 0.25 CBM`. |
| `chargeable_weight` | Air-freight billing weight (max of gross and volumetric) | |
| `booking_reference` | Shipper's own reference quoted on the booking (invoice / PO / contract no.) | Never the booking number. |
| `container_type` | e.g. `20GP`, `40HC`, `40RF` | Normalise to ISO size/type codes. |
| `si_cutoff`, `vgm_cutoff`, `cy_cutoff` | Shipping instruction / verified gross mass / container yard cut-offs | |
| `incoterm` | FOB, CIF, EXW, DAP, … | 3-letter code + named place. |
| `hs_code` | Harmonised System code | Keep digits only, 6–10 chars. |
| `marks_and_numbers` | Shipping marks printed on packages | Free text. |
| `gross_weight` / `net_weight` | With unit (`KG`/`LB`). Gross includes packaging. |
| `volume` | `CBM` (m³) or `CFT`. | |

## Invoice fields
| Term | Meaning |
|---|---|
| `part_number` | Item / part / model code printed next to the line description. |
| `price_components` | Every priced column of a line when an invoice prints several (processing-trade invoices show e.g. a processing-fee column and a material-price column). `label` is the heading as printed. |
| `unit_price` / `amount` | The per-unit price and line total of the column that adds up to `total_amount`. `amount` must equal `quantity x unit_price` (checked, tolerance 0.5 %). |
| `amount_components` | Other printed totals besides `total_amount`, e.g. the processing-fee total that is actually payable. |
| `contract_number` | Sales / processing contract or PO number quoted on the invoice. |
| `shipped_per`, `shipment_date` | Transport as printed (`AIR FREIGHT`, vessel) and the ship-on-board date. |
| Processing trade (gia công) | Goods made from customer-supplied material; the invoice shows both the processing fee (payable) and the full material value (for customs). |

## Extraction semantics
- **Never infer** values not on the document (e.g. do not compute totals unless the document shows them;
  put computed checks in `warnings`).
- Multiple currencies on one document → capture per line; totals currency is the document currency.
- Line items keep document order.
