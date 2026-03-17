#!/usr/bin/env python3
import sys, json
sys.path.insert(0, '/app/src')

try:
    from pdf_generator import generate_quote_pdf
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pdf_generator import generate_quote_pdf

if len(sys.argv) < 3:
    print("Usage: generate_pdf.py <data.json> <output.pdf>", file=sys.stderr)
    sys.exit(1)

data_path = sys.argv[1]
out_path = sys.argv[2]

with open(data_path, 'r') as f:
    data = json.load(f)

buf, quote_num = generate_quote_pdf(data)

with open(out_path, 'wb') as f:
    f.write(buf.read())

print(f"PDF generated: {quote_num}", file=sys.stderr)
