"""
Excel Agent — Extracts patient data from uploaded Excel files.
Uses openpyxl to read .xlsx/.xls and fuzzy column matching to find fields.
"""

import logging
from io import BytesIO
from typing import Any

import openpyxl

from app.utils.date_parser import parse_date
from app.utils.excel_validator import match_columns, validate_mapping
from app.utils.phone_formatter import normalize_phone

logger = logging.getLogger("careremind.agents.excel")


# Standardized row format shared across all agents
ExtractedRow = dict[str, Any]  # {name, phone, visit_date, next_visit_date}


class ExcelAgent:
    """Reads an Excel file and extracts patient rows."""

    async def extract(self, file_bytes: bytes) -> dict:
        """
        Parse an Excel file and return extracted rows.

        Returns:
            {
                "rows": [ExtractedRow, ...],
                "total_rows": int,
                "skipped": int,
                "errors": [str, ...],
            }
        """
        try:
            wb = openpyxl.load_workbook(BytesIO(file_bytes), read_only=True)
        except Exception as e:
            logger.error("Failed to open Excel file: %s", e)
            return {"rows": [], "total_rows": 0, "skipped": 0, "errors": [f"Cannot read Excel file: {e}"]}

        sheet = wb.active
        if sheet is None:
            return {"rows": [], "total_rows": 0, "skipped": 0, "errors": ["No active sheet found"]}

        rows_iter = sheet.iter_rows(values_only=True)

        # ── Find header row ──────────────────────────────────
        header_row = None
        for row in rows_iter:
            # Skip completely empty rows
            if not any(cell is not None for cell in row):
                continue
            header_row = [str(cell).strip() if cell else "" for cell in row]
            break

        if not header_row:
            return {"rows": [], "total_rows": 0, "skipped": 0, "errors": ["No header row found"]}

        # ── Map columns ──────────────────────────────────────
        mapping = match_columns(header_row)
        is_valid, missing = validate_mapping(mapping)

        if not is_valid:
            return {
                "rows": [],
                "total_rows": 0,
                "skipped": 0,
                "errors": [f"Missing required columns: {', '.join(missing)}. Found headers: {header_row}"],
            }

        logger.info("Column mapping: %s", mapping)

        # ── Extract data rows ────────────────────────────────
        extracted: list[ExtractedRow] = []
        skipped = 0
        errors: list[str] = []
        row_num = 1  # header was row 0

        for row in rows_iter:
            row_num += 1
            cells = list(row)

            # Skip empty rows
            if not any(cell is not None for cell in cells):
                continue

            # Extract fields using column mapping
            raw_name = cells[mapping["name"]] if mapping["name"] is not None and mapping["name"] < len(cells) else None
            raw_phone = cells[mapping["phone"]] if mapping["phone"] is not None and mapping["phone"] < len(cells) else None

            # Name is required
            if not raw_name:
                skipped += 1
                continue

            name = str(raw_name).strip()
            if not name:
                skipped += 1
                continue

            # Phone is required
            if not raw_phone:
                skipped += 1
                errors.append(f"Row {row_num}: missing phone for '{name}'")
                continue

            phone = normalize_phone(str(raw_phone))
            if not phone:
                skipped += 1
                errors.append(f"Row {row_num}: invalid phone '{raw_phone}' for '{name}'")
                continue

            # Dates are optional
            raw_visit = cells[mapping["visit_date"]] if mapping.get("visit_date") is not None and mapping["visit_date"] < len(cells) else None
            raw_next = cells[mapping["next_visit_date"]] if mapping.get("next_visit_date") is not None and mapping["next_visit_date"] < len(cells) else None

            extracted.append({
                "name": name,
                "phone": phone,
                "visit_date": parse_date(raw_visit),
                "next_visit_date": parse_date(raw_next),
            })

        wb.close()

        logger.info(
            "Excel extraction: %d rows extracted, %d skipped, %d errors",
            len(extracted), skipped, len(errors),
        )

        return {
            "rows": extracted,
            "total_rows": len(extracted) + skipped,
            "skipped": skipped,
            "errors": errors,
        }
