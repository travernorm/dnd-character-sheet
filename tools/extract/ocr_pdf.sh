#!/bin/bash
# OCR a book PDF (see ocr_pdf.swift). Command Line Tools sometimes ship a Swift compiler that
# doesn't match the newest SDK, so this tries the installed SDKs until one compiles.
# Usage: tools/extract/ocr_pdf.sh <book.pdf> <book-id> [first page] [last page]
HERE="$(cd "$(dirname "$0")" && pwd)"
if swift "$HERE/ocr_pdf.swift" "$@" 2>/dev/null; then exit 0; fi
for sdk in $(ls -dr /Library/Developer/CommandLineTools/SDKs/MacOSX*.*.sdk /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX*.sdk 2>/dev/null); do
  if SDKROOT="$sdk" swift "$HERE/ocr_pdf.swift" "$@" 2>/dev/null; then exit 0; fi
done
echo "Couldn't run Swift with any installed SDK. Install or update Xcode's Command Line Tools." >&2
exit 1
