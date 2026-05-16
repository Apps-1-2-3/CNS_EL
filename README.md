# StegoVault v2 — Secure Steganographic Analysis System

A full-stack secure communication tool combining **AES-128-CBC + HMAC-SHA256 +
PBKDF2** encryption with **adaptive LSB steganography** and **key-seeded
randomized embedding**, plus a complete analysis framework: PSNR / MSE / SSIM
imperceptibility metrics, RGB histogram comparison, security layer report,
and pixel-level difference visualization.

## Stack

- **Backend**: Python 3 · Flask · Pillow · NumPy · scikit-image · PyCryptodome
- **Frontend**: React 18 · TypeScript · Vite · Tailwind CSS · Recharts · lucide-react

## Project structure

```
stego-app/
├── backend/
│   ├── app.py              # Flask API
│   ├── encryption.py       # AES-128-CBC + HMAC-SHA256 + PBKDF2
│   ├── embedding.py        # Adaptive LSB + key-seeded permutation
│   ├── extraction.py       # Inverse extraction
│   ├── metrics.py          # PSNR / MSE / SSIM (scikit-image)
│   ├── histogram.py        # RGB histograms + diff map
│   ├── analysis.py         # Security layer report
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── components/     # Encode/Decode/Metrics/Histogram/Security/Visualizer
    │   └── lib/api.ts
    └── package.json
```

## Run locally

### 1. Backend (port 5000)

```bash
cd stego-app/backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m backend.app   # or:  cd .. && python -m backend.app
```

The Flask server starts on `http://localhost:5000`.

### 2. Frontend (port 5173)

```bash
cd stego-app/frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api/*` to the backend automatically.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/health` | — | status |
| POST | `/api/capacity` | `image` (file) | `capacity_bits`, `capacity_bytes` |
| POST | `/api/encode` | `image`, `message`, `password` | stego PNG (b64), stats, metrics, security |
| POST | `/api/decode` | `image`, `password` | `message` or 401 on wrong key |
| POST | `/api/metrics` | `original`, `stego` | PSNR / MSE / SSIM + modification stats |
| POST | `/api/histogram` | `original`, `stego` | RGB histograms (256 bins) |
| POST | `/api/difference-map` | `original`, `stego` | diff map PNG (b64) |
| POST | `/api/security-analysis` | `image`, `password`, `payload_bytes` | layer + entropy report |

## Security architecture

```
Plaintext
  └─► PBKDF2-SHA256 (200,000 iters, 16 B salt)  →  derive AES key + HMAC key
        └─► AES-128-CBC (random 16 B IV)         →  ciphertext
              └─► HMAC-SHA256 over salt||iv||ct  →  authentication tag
                    └─► Adaptive LSB embedding   →  rank pixels by 3×3 local variance
                          └─► Key-seeded PRNG    →  randomize embedding order
                                └─► Stego image (visually identical, PSNR > 60 dB typical)
```

Wrong-key extraction fails at the **HMAC verification** step before any plaintext is exposed.

## Image quality interpretation

| Metric | Excellent | Good | Moderate | Poor |
|--------|-----------|------|----------|------|
| PSNR | > 50 dB | > 40 dB | > 30 dB | ≤ 30 dB |
| MSE  | < 1 | < 5 | < 20 | ≥ 20 |
| SSIM | > 0.99 | > 0.95 | > 0.85 | ≤ 0.85 |

## Notes

- Use **PNG** or **BMP** cover images. JPEG re-compresses and destroys LSBs.
- Capacity ≈ `width × height × 3` bits (minus 32-bit length header).
- The embedding ranking is computed on the LSB-masked grayscale image, so it is
  stable before and after embedding — extraction reproduces the same pixel order
  without storing any side information.
