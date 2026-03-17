const express = require('express');
const multer = require('multer');
const Anthropic = require('@anthropic-ai/sdk');
const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');

const app = express();
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 20 * 1024 * 1024 }
});

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

app.use(express.static(path.join(__dirname, '../public')));

const ANALYSIS_PROMPT = `Je bent een technisch expert in LED neon sign productie voor Bonfire Club, een Belgisch/Nederlands bedrijf.

Analyseer dit design en maak een volledige feasibility beoordeling.

Neon productie regels die je moet kennen:
- Minimale lijndikte voor neon buis: 8mm (op schaal van het teken)
- Neon buis kan NIET kruisen — elk kruispunt = apart segment
- Gesloten vlakken (volledig omsloten) zijn niet uitvoerbaar als neon
- Minimum letterhoogte voor neon: ~4cm
- Vloeiende curves werken beter dan scherpe hoeken
- Gevulde vlakken, gradients, 3D effecten, schaduwen → altijd UV-print

Productietypes die je kunt adviseren:
1. "Neon tekst" — alleen tekst als neon, geen backing print
2. "Neon tekst + omlijning" — tekst met een frame/border in neon
3. "Cut-to-letter" — backing per letter uitgesneden, neon erop
4. "Cut-to-shape" — backing in vorm van logo, neon contouren
5. "UV-print + neon omlijning" — logo geprint op acryl, neon contouren eroverheen
6. "Alleen UV-print" — te complex voor neon, alleen print mogelijk
7. "Niet uitvoerbaar" — te fijn, te complex, niet te vereenvoudigen

Genereer ook een SVG lijntekening — dit is de "bending schematic" die naar de fabrikant gaat.
De SVG heeft viewBox="0 0 500 350".
Teken ALLEEN de elementen die neon worden: stroke="#ffffff" stroke-width="2.5" fill="none"
Gebruik ook labels: kleine tekst die aangeeft wat elk segment is (bv "segment A", "segment B")
Schaal proportioneel met 30px padding rondom.

Geef antwoord ALLEEN als raw JSON, geen markdown, geen uitleg erbuiten:
{
  "uitvoerbaar": true,
  "verdict": "korte één-zin beoordeling",
  "product_type": "één van de 7 types hierboven",
  "backing": "bijv. Cut-to-shape transparant acryl",
  "uv_print_nodig": true,
  "complexiteit": "Laag / Gemiddeld / Hoog",
  "neon_segmenten": 3,
  "neon_elementen": ["beschrijving van elk neon element"],
  "uv_elementen": ["beschrijving van elk UV-print element"],
  "waarschuwingen": ["eventuele technische waarschuwingen"],
  "aanbevelingen": ["concrete suggesties voor de klant of productieteam"],
  "samenvatting": "2-3 zinnen uitleg voor intern gebruik bij Bonfire Club",
  "svg": "<svg viewBox='0 0 500 350' xmlns='http://www.w3.org/2000/svg'>[volledige SVG inhoud inclusief zwarte achtergrond rect en alle neon paden/tekst]</svg>"
}`;

app.post('/api/analyze', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Geen bestand ontvangen' });
  }

  const base64 = req.file.buffer.toString('base64');
  const mediaType = req.file.mimetype || 'image/png';

  const supportedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  if (!supportedTypes.includes(mediaType)) {
    return res.status(400).json({
      error: 'Bestandstype niet ondersteund. Gebruik PNG, JPG of WebP. Voor SVG/PDF: converteer eerst naar PNG.'
    });
  }

  try {
    const message = await anthropic.messages.create({
      model: 'claude-opus-4-5',
      max_tokens: 3000,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image',
            source: { type: 'base64', media_type: mediaType, data: base64 }
          },
          { type: 'text', text: ANALYSIS_PROMPT }
        ]
      }]
    });

    const raw = message.content[0].text;
    let parsed;

    try {
      parsed = JSON.parse(raw.replace(/```json|```/g, '').trim());
    } catch {
      return res.status(500).json({ error: 'AI gaf ongeldig antwoord terug', raw });
    }

    res.json(parsed);
  } catch (err) {
    console.error('Anthropic API error:', err);
    res.status(500).json({ error: 'API fout: ' + err.message });
  }
});

app.get('/health', (req, res) => res.json({ status: 'ok', service: 'bonfire-neon-analyzer' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Bonfire Neon Analyzer draait op poort ${PORT}`);
});

// Quote PDF generator endpoint
app.post('/api/quote', upload.fields([
  { name: 'mockup1', maxCount: 1 },
  { name: 'mockup2', maxCount: 1 }
]), async (req, res) => {
  const tmpFiles = [];
  try {
    const body = req.body;
    const files = req.files || {};

    let mockup1Path = null;
    let mockup2Path = null;

    if (files.mockup1 && files.mockup1[0]) {
      mockup1Path = require('path').join(require('os').tmpdir(), `bfc_m1_${Date.now()}.jpg`);
      require('fs').writeFileSync(mockup1Path, files.mockup1[0].buffer);
      tmpFiles.push(mockup1Path);
    }
    if (files.mockup2 && files.mockup2[0]) {
      mockup2Path = require('path').join(require('os').tmpdir(), `bfc_m2_${Date.now()}.jpg`);
      require('fs').writeFileSync(mockup2Path, files.mockup2[0].buffer);
      tmpFiles.push(mockup2Path);
    }

    const data = { ...body, mockup1: mockup1Path, mockup2: mockup2Path };
    const dataPath = require('path').join(require('os').tmpdir(), `bfc_data_${Date.now()}.json`);
    const outPath = require('path').join(require('os').tmpdir(), `bfc_quote_${Date.now()}.pdf`);
    require('fs').writeFileSync(dataPath, JSON.stringify(data));
    tmpFiles.push(dataPath, outPath);

    require('child_process').execSync(
      `python3 "${require('path').join(__dirname, 'generate_pdf.py')}" "${dataPath}" "${outPath}"`,
      { timeout: 30000 }
    );

    if (!require('fs').existsSync(outPath)) throw new Error('PDF niet aangemaakt');

    const pdfBuf = require('fs').readFileSync(outPath);
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename="BFC_Offerte.pdf"');
    res.setHeader('X-Quote-Number', data.quote_number || 'BF001');
    res.send(pdfBuf);

  } catch (err) {
    console.error('Quote PDF error:', err.message);
    res.status(500).json({ error: err.message });
  } finally {
    tmpFiles.forEach(f => { try { require('fs').unlinkSync(f); } catch {} });
  }
});
