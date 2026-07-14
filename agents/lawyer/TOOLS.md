# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Related

- [Agent workspace](/concepts/agent-workspace)

## Google Drive

- Current contracts folder: `https://drive.google.com/drive/folders/17Fvp0lcmH-xczRpVX6UuqgzNKLfMg62F`
- Current clients subfolder: `https://drive.google.com/drive/folders/1eqeeXBMKbQEx0fm1jg61UZ2GHlBskz_5`
- Current Integramme Random Coffee folder: `https://drive.google.com/drive/folders/1dmyKRa2PAvsqRZiy5Br3HGXdUfedz1vW`
- Current Integramme Random Coffee contract: `https://docs.google.com/document/d/1CBAp1nTW2y_0Y8wvshe3IMWs-6MpKTCG/edit`
- Use this as the actual folder with contracts for Anton
- Do not use the old contracts folder `https://drive.google.com/drive/folders/1p4ar8UjP2I2xBbGC_L5F6-n6gV20lGSa` unless Anton explicitly asks for old/archive contracts
- When Anton asks for "папка с договорами", send the current contracts folder above

## Template Guard

- Templates folder: `https://drive.google.com/drive/folders/18W-0yJgA_KrxJBf9pqW-L4hDxWjJL0aZ`
- Before creating, revising, or releasing any legal document, fetch/check the current template fresh from Drive
- Check the template title, ID/link, modified date, and document type before using it
- Do not use old local copies, previously downloaded files, memory, or similar-looking templates
- If Anton says a template changed, find and use the new template file; do not fall back to the old template
- If the current template is unclear, stop and ask Anton/Aкс which exact file to use
- Always state the template source in the result
- Never generate the structure of a legal document from scratch when a matching template exists
- Every released document must be based on a copied template from the templates folder
- For ordinary invoice: use `Счет.docx`, ID `1MLBdyK_mxv2kpGpU4m8S3o3k_B4LCW1R`
- For invoice-offer: use `Счёт-оферта.docx`, ID `1Cr3I2bmeru6yG2yu4wGTvDp2bRDieHNq`
- For 100% prepayment specification: use `Спецификация 100%.docx`, ID `1NFugyFinQ9ZLNDNqWySBySurmE-oEUpA`
- For 50% prepayment specification: use `Спецификация 50%.docx`, ID `1SzHz9HNFrM8Nn43NK4cbN3w00rXwLtbu`
- For CRM/service contract: use `Договор CRM шаблон v1.docx`, ID `1pyLYVmpXNCRZuZgURS4r2yAP4JjmiVem`
- If Anton asks for `счёт`, do not use `Счёт-оферта.docx`
- If no matching template exists, stop and ask Anton through Aкс

## Numbering

- Do not start new contracts, specifications, or invoices from `001` by default
- Before releasing documents, check the register or the pinned latest number
- After the Integramme Random Coffee package on 2026-06-28, next numbers are: contracts from `ДОГ-059`, specifications from `СПЕ-231`, invoices from `СЧ-583`
- If the register is unavailable or the correct number is unclear, stop and ask Anton through Aкс instead of inventing a number

## Telegram Output Format

- When sending a ready document to Anton, send only one text line with document type, number, client, and date, and attach the `.docx` file
- Example: `Счёт-оферта СЧО-566 · Абдуллин · 2026-07-07`
- Do not add links, template metadata, status notes, or explanations in the final Telegram message unless Anton explicitly asks
