#!/bin/bash
# Copies all files needed for the Colab notebook to a local staging folder.
# Then you drag that folder to Google Drive.

DEST="${HOME}/Desktop/YBF-FlipEval"
SRC_DATA="/Users/gonet/Documents/AI-Egitmek/ybf_toy/data"
SRC_FLIP="/Users/gonet/Documents/YBF-1/raw/AIEgitim-flip-cekirdek-v1.json"

mkdir -p "${DEST}/results"

# Flip seed
cp "${SRC_FLIP}" "${DEST}/flip.json"

# Per-axis v2 scorer prompts
cp "${SRC_DATA}/ybf_reality_v2_scorer_prompt.txt"  "${DEST}/"
cp "${SRC_DATA}/ybf_dignity_v2_scorer_prompt.txt"  "${DEST}/"
cp "${SRC_DATA}/ybf_respect_v2_scorer_prompt.txt"  "${DEST}/"
cp "${SRC_DATA}/ybf_boundary_scorer_prompt.txt"    "${DEST}/"
cp "${SRC_DATA}/ybf_freedom_v2_scorer_prompt.txt"  "${DEST}/"

echo "✓ Done. Upload this folder to Google Drive:"
echo "  ${DEST}"
echo ""
echo "Contents:"
ls -lh "${DEST}"
