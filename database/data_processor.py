# database/data_processor.py

from decimal import Decimal

class DataProcessor:
    def process_order_row(self, row):
        # Erstmal Basiswerte vorbereiten
        gesamt_netto = float(row.GesamtNetto) if isinstance(row.GesamtNetto, Decimal) else row.GesamtNetto
        porto = abs(float(row.Porto) if isinstance(row.Porto, Decimal) else row.Porto)
        umsatz_netto = gesamt_netto - porto

        # Werte ggf. ins Negative drehen
        if row.Belegart != "Auftragsbestätigung":
            gesamt_netto *= -1
            porto *= -1
            umsatz_netto *= -1

        # Convert row data to a dictionary directly in JSON-compatible format
        return {
            "Datum": row.Datum.isoformat() if row.Datum else None,
            "Auftragsnr": str(row.Auftragsnr),
            "Kdnr": int(row.Kdnr[1:]) if row.Kdnr else 0,
            "Kunde": row.Kunde,
            "UnserZeichen": row.UnserZeichen,
            "Vertreter": int(row.Vertreter[1:]) if row.Vertreter else 0,
            "Kennung": row.Kennung,
            "GesamtNetto": gesamt_netto,
            "Porto": porto,
            "UmsatzNetto": umsatz_netto
        }