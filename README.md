## Folder Structure


scripture-builder/
├── app.py                  ← Flask routes
├── launch.py               ← macOS menu bar app
├── sermon_parser.py        ← docx → raw scripture entries
├── formatter.py            ← NEW: raw entries → formatted slide payloads
├── generator.py            ← builds the .pro binary (currently stub)
├── proto/                  ← protobuf definitions & compiled files
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js

---

## Complete ProPres Layout
Complete forensic specification of default ProPres scripture layout, dimensions, styling, settings can be found in [scripture-pro-spec.md](./scripture-pro-spec.md)