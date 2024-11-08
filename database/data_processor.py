# database/data_processor.py

from decimal import Decimal

class DataProcessor:
    def process_order_row(self, row):
        # Convert row data to a dictionary directly in JSON-compatible format
        return {
            "Datum": row.Datum.isoformat() if row.Datum else None,
            "Auftragsnr": str(row.Auftragsnr),
            "Kdnr": int(row.Kdnr[1:]) if row.Kdnr else 0,
            "Kunde": row.Kunde,
            "UnserZeichen": row.UnserZeichen,
            "Vertreter": int(row.Vertreter[1:]) if row.Vertreter else 0,
            "Kennung": row.Kennung,
            "GesamtNetto": float(row.GesamtNetto) if isinstance(row.GesamtNetto, Decimal) else row.GesamtNetto,
            "Porto": abs(float(row.Porto) if isinstance(row.Porto, Decimal) else row.Porto),
            "UmsatzNetto": float(row.GesamtNetto - abs(row.Porto))
        }