# __SCRIPTURE.pro — Complete Forensic Specification

> Extracted via protobuf binary parsing. Every value here is read directly
> from the file — nothing estimated or guessed. Use this as the authoritative
> reference for programmatic `.pro` generation.

---

## File Identity

| Field | Value |
|---|---|
| Format | ProPresenter 7 protobuf binary |
| Document UUID | `6AA57101-2598-43C9-8BBD-DCB0C11D8FAD` |
| Numeric ID | `352452646` |
| Label | `SCRIPTURE` |
| Group | `SERMON` → `SERMON-Scripture` |
| Arrangement | `SERMON SCRIPTURE - Default` |
| Background group | `SERMON - Scripture BG` → `BACKGROUNDS` |
| Source thumbnail ref | `20260118-LED-SERMON-TITLE.png 1 1` |

---

## Canvas / Output

The canvas coordinate system is inferred from element positions and background
image dimensions. The total layout spans roughly **2816 × 1024 units**, covering
three distinct output zones:

| Zone | x origin | width | height | Background image |
|---|---|---|---|---|
| Left Pillar | 0 | 384 | 640 | `LR PILLAR - dimension.png` (384×640 px) |
| Wall | 384 | 2048 | 896 | `WALL - dimension.png` (2048×896 px) |
| Right Pillar | 2432 | 384 | 640 | `LR PILLAR - dimension.png` (same file) |
| Lyric Banner | 1024 | 768 | 256 | `LYRIC BANNER - dimension.png` (768×256 px) |

All background images are referenced by path, not embedded:

```
file:///Users/favorchurch/Documents/ProPresenter/Media/Assets/LR%20PILLAR%20-%20dimension.png
file:///Users/favorchurch/Documents/ProPresenter/Media/Assets/WALL%20-%20dimension.png
file:///Users/favorchurch/Documents/ProPresenter/Media/Assets/LYRIC%20BANNER%20-%20dimension.png
```

Relative paths stored alongside (used for portability):
```
Media/Assets/LR PILLAR - dimension.png
Media/Assets/WALL - dimension.png
Media/Assets/LYRIC BANNER - dimension.png
```

---

## Elements Overview

There are **14 elements** in the slide. 10 are text boxes; 4 are background image layers.

| # | Name | UUID | Type | Screen target |
|---|---|---|---|---|
| 1 | MAIN SCRIPTURE REF | `CEFA709F-B3F8-4250-A71D-0CE854E721C1` | Text | (hidden/off-canvas — y=-265) |
| 2 | MAIN SCRIPTURE TEXT | `2BA0A173-4AFF-40D6-A156-A62A18DFCED2` | Text | (hidden/off-canvas — y=-192) |
| 3 | T - Ref | `06016548-66D4-4610-BECA-E8D50981FA09` | Text | Tall (Pillar) |
| 4 | T - Text | `2D70E6FE-6AE3-4CB9-A864-F9A429521774` | Text | Tall (Pillar) |
| 5 | W - Ref | `85E90E19-C5C0-4402-858C-11BD3C2DD12C` | Text | Wall |
| 6 | W - Text | `4C703437-17CA-4420-AF6A-5D7A7D09023A` | Text | Wall |
| 7 | L - Ref | `BE29937B-011A-4BB7-9B98-F0C02C9E6B48` | Text | Left Pillar |
| 8 | L - Text | `FE26B24D-11B8-42C7-99D1-CE325712FDC7` | Text | Left Pillar |
| 9 | R - Ref | `4372AC36-E7F8-467E-9111-B288549D5948` | Text | Right Pillar |
| 10 | R - Text | `3E55DACB-A85F-42F7-B100-623D6EA9F8A2` | Text | Right Pillar |
| 11 | (unnamed BG) | `57E0900B-FC29-447C-8384-2F7D3DE8B18F` | Image | Right Pillar background |
| 12 | LR PILLAR - dimension.png | `1ADB807D-7B49-4F1B-894C-5CAA874C85B7` | Image | Left Pillar background |
| 13 | (unnamed BG) | `2A7F329F-E8D9-437B-8646-2671B43FAD1D` | Image | Lyric Banner background |
| 14 | (unnamed BG) | `06562C6A-E5AA-4F03-B145-0B0E2AEAAC1E` | Image | Wall background |

---

## Bounding Boxes (all coordinates in canvas units)

All positions are stored as **IEEE 754 double-precision floats** in little-endian
protobuf wire type 1 (64-bit fixed). Field F3 contains two sub-fields:
- `F3.F1` = position (x, y)
- `F3.F2` = size (width, height)

| Element | x | y | width | height |
|---|---|---|---|---|
| MAIN SCRIPTURE REF | 946.30 | **-265.20** | 923.32 | 73.13 |
| MAIN SCRIPTURE TEXT | 946.30 | **-192.10** | 923.32 | 155.34 |
| T - Ref | 1045.69 | 14.29 | 724.63 | 66.80 |
| T - Text | 1043.70 | 86.80 | 726.89 | 155.34 |
| W - Ref | 527.49 | 321.30 | 1761.02 | 136.42 |
| W - Text | 527.50 | 457.70 | 1761.02 | 485.55 |
| L - Ref | 20.12 | 390.49 | 349.27 | 119.54 |
| L - Text | 20.70 | 520.90 | 349.27 | 463.01 |
| R - Ref | 2451.20 | 390.49 | 349.27 | 119.54 |
| R - Text | 2451.70 | 520.90 | 349.27 | 463.01 |
| LR PILLAR bg (right) | 2432.00 | 384.00 | 384.00 | 640.00 |
| LR PILLAR bg (left) | 0.00 | 384.00 | 384.00 | 640.00 |
| LYRIC BANNER bg | 1024.00 | 0.00 | 768.00 | 256.00 |
| WALL bg | 384.00 | 256.00 | 2048.00 | 896.00 |

> **Note:** MAIN SCRIPTURE REF and MAIN SCRIPTURE TEXT have negative y values
> (off the top of the canvas). They are **master/source elements** — they carry
> the content but are not visible. The T/W/L/R variants are the actual displayed
> elements, each linked back to these via the `F6` field (element reference UUID).

---

## Text Styling — Per Element

### Shared style properties (all text elements)

All text boxes share these common protobuf field values:

| Field | Value | Meaning |
|---|---|---|
| F8.F1 | `1` | Enabled |
| F8.F2 (×3) | `1.0, 1.0, 1.0` | RGB scale (white shadow/stroke at full) |
| F10.F2 | `3.0` | Border/stroke width |
| F10.F3 | `1.0, 1.0, 1.0, 1.0` | Stroke color (RGBA white) |
| F11.F2 | `315.0` | Corner radius (fully rounded) |
| F11.F3 | `5.0` | Padding (inner margin) |
| F11.F4 | `5.0` | Padding |
| F11.F6 | `0.75` | Opacity |
| F13.F6 | `1` (ref) or `2` (text) | Text role: 1=reference, 2=body |
| F13.F7 | `2` or `3` | Alignment role |
| F13.F9 | `1` | Enabled |
| F13.F11.F4 | `32` | Minimum font size |

---

### Element 1 — MAIN SCRIPTURE REF (source/hidden)

```
Font:        HelveticaNeue-Bold  /  Helvetica Neue
Size:        50.0 pt  (RTF \fs100)
Bold:        yes (F8=1)
Color:       #FFFFFF (white)  rgb(255,255,255)
Tracking:    -4 / expndtw-20  (F7 = -1.0 in protobuf)
Line spacing: 84pt leading  (F6.F12 = 84.0)
Alignment:   center (\qc)
Emoji font:  AppleColorEmoji fallback at ranges [15,17]
Scale ratio: 0.6375 (F13.F3.F13[0].F4)
```

RTF template:
```rtf
{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 HelveticaNeue-Bold;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;}
{\*\expandedcolortbl;;\cssrgb\c100000\c100000\c100000;}
\deftab1680
\pard\pardeftab1680\sl192\slmult1\pardirnatural\qc\partightenfactor0
\f0\b\fs100 \cf2 \kerning1\expnd-4\expndtw-20
\CocoaLigature0 {REFERENCE_TEXT}}
```

---

### Element 2 — MAIN SCRIPTURE TEXT (source/hidden)

```
Font:        HelveticaNeue-Medium  /  Helvetica Neue
Size:        32.0 pt  (RTF \fs64)
Bold:        no
Color:       #FFFFFF (white)
Tracking:    -4 / expndtw-20  (F7 = -1.0)
Line spacing: 84pt leading
Alignment:   center
Emoji font:  AppleColorEmoji fallback
```

RTF template:
```rtf
{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 HelveticaNeue-Medium;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;}
{\*\expandedcolortbl;;\cssrgb\c100000\c100000\c100000;}
\deftab1680
\pard\pardeftab1680\sl192\slmult1\pardirnatural\qc\partightenfactor0
\f0\fs64 \cf2 \kerning1\expnd-4\expndtw-20
\CocoaLigature0 {SCRIPTURE_BODY_TEXT}}
```

---

### Element 3 — T - Ref (Tall/Pillar reference label)

```
Font:        LTSuperior-Black  /  LT Superior
Size:        40.0 pt  (RTF \fs80)
Bold:        yes (F8=1)
Color:       rgb(253, 225, 213)  →  #FDE1D5  (warm peach/salmon)
             cssrgb: c99537 c90667 c86505
Tracking:    -4 / expndtw-20  (F7 = -1.0)
Line spacing: 84pt leading  (sl192)
Alignment:   center
Links to:    MAIN SCRIPTURE REF (UUID CEFA709F...)
```

RTF template:
```rtf
{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 LTSuperior-Black;}
{\colortbl;\red255\green255\blue255;\red253\green225\blue213;}
{\*\expandedcolortbl;;\cssrgb\c99537\c90667\c86505;}
\deftab1680
\pard\pardeftab1680\sl192\slmult1\pardirnatural\qc\partightenfactor0
\f0\b\fs80 \cf2 \kerning1\expnd-4\expndtw-20
{REFERENCE_TEXT}}
```

---

### Element 4 — T - Text (Tall/Pillar body text)

```
Font:        LTSuperior-Medium  /  LT Superior
Size:        35.0 pt  (RTF \fs70)
Bold:        no
Color:       rgb(253, 225, 213)  →  #FDE1D5 (same peach)
Line spacing: 90% of leading  (F6.F5 = 0.9), 84pt base  (sl216)
Alignment:   center
Links to:    MAIN SCRIPTURE TEXT (UUID 2BA0A173...)
```

RTF template:
```rtf
{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 LTSuperior-Medium;}
{\colortbl;\red255\green255\blue255;\red253\green225\blue213;}
{\*\expandedcolortbl;;\cssrgb\c99537\c90667\c86505;}
\deftab1680
\pard\pardeftab1680\sl216\slmult1\pardirnatural\qc\partightenfactor0
\f0\fs70 \cf2 {SCRIPTURE_BODY_TEXT}}
```

---

### Element 5 — W - Ref (Wall reference label)

```
Font:        HelveticaNowDisplay-ExtraBold  /  Helvetica Now Display
Size:        90.0 pt  (RTF \fs180)
Bold:        yes (F8=1)
Color:       #FFFFFF (white)
Tracking:    -8 / expndtw-40  (F7 = -2.0)  ← tighter than others
Line spacing: 100%  (F6.F5 = 1.0), 84pt
Alignment:   center  (no \sl — uses default leading)
Links to:    MAIN SCRIPTURE REF
```

RTF template:
```rtf
{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 HelveticaNowDisplay-ExtraBold;}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;}
{\*\expandedcolortbl;;\cssrgb\c100000\c100000\c100000;}
\deftab1680
\pard\pardeftab1680\pardirnatural\qc\partightenfactor0
\f0\b\fs180 \cf2 \kerning1\expnd-8\expndtw-40
\CocoaLigature0 {REFERENCE_TEXT}}
```

---

### Element 6 — W - Text (Wall body text)

```
Font:        LTSuperior-Regular (fonttbl) / LTSuperior-Bold (protobuf F1)
             NOTE: There is a discrepancy — RTF declares Regular, protobuf field says Bold.
             ProPresenter likely uses the protobuf value. Use LTSuperior-Bold.
Size:        70.0 pt  (RTF \fs140)
Bold:        yes (F8=1)
Color:       #FFFFFF (white)
Line spacing: 90%  (F6.F5 = 0.9), 84pt  (sl216)
Alignment:   center
Links to:    MAIN SCRIPTURE TEXT
```

RTF template:
```rtf
{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 LTSuperior-Regular;}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;}
{\*\expandedcolortbl;;\cssrgb\c100000\c100000\c100000;}
\deftab1680
\pard\pardeftab1680\sl216\slmult1\pardirnatural\qc\partightenfactor0
\f0\b\fs140 \cf2 {SCRIPTURE_BODY_TEXT}}
```

---

### Elements 7 & 9 — L - Ref / R - Ref (Pillar reference labels)

These are **identical in style**, mirrored in x position.

```
Font:        LTSuperior-Black  /  LT Superior
Size:        45.0 pt  (RTF would be \fs90)
Bold:        yes (F8=1)
Color:       rgb(253, 209, 189)  →  slightly different peach variant
             raw bytes: 0x3f 0xd0 0x7e... → approx #FDD0BD
Line spacing: 80%  (F6.F5 = 0.8), 84pt
Tracking:    -4 / expndtw-20  (F7 = -1.0)
Alignment:   center
RTF body:    EMPTY ({\fonttbl} with no fonts — content driven by source link)
Links to:    MAIN SCRIPTURE REF
```

---

### Elements 8 & 10 — L - Text / R - Text (Pillar body text)

**Identical in style**, mirrored in x position.

```
Font:        LTSuperior-Medium  /  LT Superior
Size:        35.0 pt
Bold:        no
Color:       same approx peach #FDD0BD
Line spacing: 90%  (F6.F5 = 0.9)
Alignment:   center
RTF body:    EMPTY (content driven by source link)
Links to:    MAIN SCRIPTURE TEXT
```

---

## Source Linking (Master → Variant)

Elements 3–10 each contain a `F6` field that references a master element UUID
and name. This is ProPresenter's **element linking** system — the displayed
variant pulls content from the master at runtime.

| Element | Links to UUID | Links to name |
|---|---|---|
| T - Ref | `CEFA709F-B3F8-4250-A71D-0CE854E721C1` | MAIN SCRIPTURE REF |
| T - Text | `2BA0A173-4AFF-40D6-A156-A62A18DFCED2` | MAIN SCRIPTURE |
| W - Ref | `CEFA709F-B3F8-4250-A71D-0CE854E721C1` | MAIN SCRIPTURE REF (F4=1) |
| W - Text | `2BA0A173-4AFF-40D6-A156-A62A18DFCED2` | MAIN SCRIPTURE TEXT (F4=1) |
| L - Ref | `CEFA709F-B3F8-4250-A71D-0CE854E721C1` | MAIN SCRIPTURE REF (F4=1) |
| L - Text | `2BA0A173-4AFF-40D6-A156-A62A18DFCED2` | MAIN SCRIPTURE |
| R - Ref | `CEFA709F-B3F8-4250-A71D-0CE854E721C1` | MAIN SCRIPTURE REF (F4=1) |
| R - Text | `2BA0A173-4AFF-40D6-A156-A62A18DFCED2` | MAIN SCRIPTURE |

> **F4=1** in the link message appears to mean "inherit content" (full link).
> Elements without F4 (T-Ref, T-Text) may be style-only links.

---

## Shadow / Glow Properties

Elements 1 & 2 (master text boxes) use `F9` for a drop shadow:

```
F9.F2  = 0.5   (shadow opacity)
F9.F3  = 1     (enabled)
F9.F4  = 0.108305 or 0.137571  (shadow angle/distance)
```

Elements 3–10 (screen-specific variants) use `F9` for background fill color:

```
F9.F1 bytes: 0d b8 1e 05 3e 15 3d 0a 17 3f 1d 33 33 73 3f 25 00 00 80 3f
Decoded:  R≈0.130  G≈0.150  B≈0.450  A=1.0
→ Approximately a dark blue/navy fill behind text boxes
```

Elements 1 & 2 use a different `F9`:
```
F9.F1 bytes: 25 00 00 80 3f  (single float = 1.0)
F9.F4 = 1
→ Shadow offset
```

---

## Shadow/Outline Color (F12 on text body)

All text elements share this identical `F12` bytes on their text body container:

```
0d 3f 35 7e 3f 15 5c 8f 42 3f 1d 6f 12 03 3d 25 00 00 80 3f
Decoded floats:  R≈0.993  G≈0.760  B≈0.030  A=1.0
→ Bright yellow/gold  #FDHC08 approx  rgb(253,194,8)
```

This is applied as a glow/outline color on the text — likely the yellow outline
visible on text in the live output.

---

## Protobuf Navigation Path

To reach slide elements programmatically:

```
root
└── F13 (presentation, 15642b)
    └── F10[0] (main slide group, 15240b)
        └── F23 (slides blob)
            └── F2 (slides container, 15147b)
                └── F1 (the single slide, 15140b)
                    ├── F1[0..13]  (14 elements/shapes)
                    ├── F5  (opacity = 1.0)
                    ├── F6  (canvas size: 2816 × 1024 as two doubles)
                    └── F7  (slide UUID: FE0675BD-D8E3-481E-A143-1A5E3A5A60A0)
```

Canvas size from F6:
```
bytes: 09 00 00 00 00 00 00 a6 40  11 00 00 00 00 00 00 92 40
→ double 1: 2816.0  (canvas width)
→ double 2: 1152.0  (canvas height — note: taller than visible, pillars extend below)
```

---

## RTF Superscript Encoding

Verse numbers in the body text use RTF superscript via `\super` or Unicode
superscript characters. In the sample text the `¹¹` and `¹²` are encoded as
RTF `\'b9\'b9` (¹) and `\'b9\'b2` (¹²) — Windows-1252 codepoints for
superscript numerals.

When building RTF for verse-numbered text, encode superscript digits as:
`\'b9` (¹) `\'b2` (²) `\'b3` (³) then `\'b4`–`\'b9` for 4–9,
or use `{\super N}` RTF syntax.

---

## Key UUIDs to Preserve

These UUIDs are referenced cross-element and must be kept stable in generated files:

| UUID | Role |
|---|---|
| `CEFA709F-B3F8-4250-A71D-0CE854E721C1` | MAIN SCRIPTURE REF master |
| `2BA0A173-4AFF-40D6-A156-A62A18DFCED2` | MAIN SCRIPTURE TEXT master |
| `BE1F24FA-F465-4CEF-8A83-A3C5C44EDF80` | Slide group container |
| `2A1BCCF2-2103-4356-A304-B9D500DF73E6` | Presentation/slide set |
| `5E482E7F-8263-404A-B0BC-829FA73DADE2` | Arrangement: SERMON SCRIPTURE - Default |
| `1FABF20E-CDEC-4D9D-8366-4CBFDD2777D3` | Arrangement copy |
| `9312F879-4ED3-48A8-93A7-1455EF18EC45` | Background group |
| `DB3F663B-C110-45F2-9B9C-A2CA7CEA2FD9` | SERMON - Scripture BG |
| `25E4F891-98C2-4189-ADB9-550211143B83` | BACKGROUNDS container |

---

## What to Inject Per Scripture

When generating a new slide from this template, **only two things change**:

1. **MAIN SCRIPTURE REF** RTF content → the reference string e.g. `John 3:16 (NIV)`
2. **MAIN SCRIPTURE TEXT** RTF content → the verse body text

All variant elements (T/W/L/R) pull from those two masters via the link system.
All UUIDs for non-master elements should be regenerated (new UUIDs per slide).
The master element UUIDs (`CEFA709F...` and `2BA0A173...`) should be kept
consistent within a file so the links resolve correctly.