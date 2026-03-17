# Bonfire Club — Neon Analyzer

Upload een klant bestand → AI analyseert uitvoerbaarheid → genereert lijntekening in seconden.

## Lokaal testen

```bash
npm install
ANTHROPIC_API_KEY=sk-ant-xxx npm start
# Open http://localhost:3000
```

## Deploy op Railway

1. Maak een nieuw project op railway.app
2. Kies "Deploy from GitHub repo" of gebruik Railway CLI:

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

3. Stel de environment variable in:
   - `ANTHROPIC_API_KEY` = jouw Anthropic API key

4. Railway geeft automatisch een publieke URL.

## Bestandsformaten

Ondersteund: PNG, JPG, WEBP
Voor SVG of PDF: converteer eerst naar PNG via een online tool.

## Wat de tool doet

1. Klant bestand uploaden
2. Claude Vision analyseert het design
3. Bepaalt automatisch: neon vs UV-print elementen
4. Genereert SVG lijntekening (bending schematic)
5. Adviseert producttype: neon tekst / cut-to-shape / UV-print + neon / etc.
6. Toont waarschuwingen bij technische problemen
7. SVG downloadbaar voor de fabrikant
