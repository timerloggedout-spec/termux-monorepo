Receipts Vault — an AI NAS Skill for Track 01 Workflow
UGREEN Hackathon 2026 · Project Proposal

1. Problem. Receipts scatter across camera rolls, email inboxes, and paper drawers. When a warranty claim, return, or tax question arrives, the one receipt that matters cannot be found, and a month of spending cannot be reconstructed.

2. User. Any household or small team whose NAS already holds family photos and documents, and who loses hours to "do you still have the receipt for…?" moments.

3. What it does. Receipts Vault watches an inbox folder on the NAS. Each new photo, scan, or PDF is read, filed once into a year/month/category vault, and indexed with vendor, date, total, currency, and category extracted.

4. Organize files. Originals are copied — never edited — into a sortable layout with human-readable names (date, vendor, total, short hash). A fixed twelve-category taxonomy keeps filing consistent across months and years.

5. Find information. Questions are answered from the index, never from memory: what a purchase cost, which receipts exceed a threshold, whether proof of purchase exists — each answer cites the record and its file path.

6. Automate tasks. A monthly close bundles the month's receipts with per-category totals and flags anomalies. Warranty dates derived from purchase records trigger a reminder thirty days before lapse, receipt attached.

7. Integrity. Every file is identified by its SHA-256. Duplicates are detected by hash and filed once; near-duplicates are cross-linked, never deleted. A copy enters the vault only after its hash verifies against the original.

8. Trust. Facts are quoted, not improved: totals are never rounded or converted, each extracted field carries a read/inferred/unread confidence, and uncertain extractions stop for user confirmation before filing. Corrections keep the prior value on record.

9. Privacy. Everything runs locally on UGOS; nothing leaves the device. Sharing an export always asks first, names exactly what would be shared, and redacts payment digits by default.

10. This round. The Round 1 package specifies the complete workflow — intake, extraction schema, confirm gate, filing, retrieval, and the three automations — as a SKILL.md package built fresh in-window, ready for the Round 2 live test.
