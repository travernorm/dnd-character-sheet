// OCR a book PDF with macOS's built-in Vision text recognition, one text file per page.
//
// Cleaner than the PDFs' own text layers (pdf_text.py), and the only way to read a scanned
// book with none. Writes packs/.text/<book-id>/p0001.txt ... in two-column reading order, plus
// dropped.txt listing the margin notes and sideways credits it left out. Needs macOS 13+, no installs.
//
// Usage: tools/extract/ocr_pdf.sh <book.pdf> <book-id> [first page] [last page]  (picks a working SDK)
import Foundation
import PDFKit
import Vision

let args = CommandLine.arguments
guard args.count >= 3 else {
    print("Usage: swift tools/extract/ocr_pdf.swift <book.pdf> <book-id> [first page] [last page]")
    exit(1)
}
guard let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    print("Couldn't open \(args[1])")
    exit(1)
}
let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
let out = root.appendingPathComponent("packs/.text/\(args[2])")
try? FileManager.default.createDirectory(at: out, withIntermediateDirectories: true)
let first = args.count > 3 ? Int(args[3])! : 1
let last = args.count > 4 ? Int(args[4])! : doc.pageCount

func render(_ page: PDFPage) -> CGImage? {
    let box = page.bounds(for: .mediaBox)
    let scale: CGFloat = 2.5  // about 180 dpi: enough for body text
    let w = Int(box.width * scale), h = Int(box.height * scale)
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    return ctx.makeImage()
}

var done = 0
var dropped: [String] = []  // margin notes left out, listed in dropped.txt to check the filter
for n in first...last {
    guard let page = doc.page(at: n - 1), let image = render(page) else { continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = true
    req.recognitionLanguages = ["en-US"]
    try? VNImageRequestHandler(cgImage: image, options: [:]).perform([req])
    var obs = (req.results ?? []).compactMap { o -> (CGRect, String)? in
        guard let t = o.topCandidates(1).first?.string else { return nil }
        return (o.boundingBox, t)
    }
    // Handwritten margin notes (Xanathar's and Volo's quotes) are sentences in taller boxes whose words
    // aren't in the PDF's own text layer: they're pictures, or a script font it stores as junk
    // ("W~c, l c, Cool"). Body text and tables are in that layer, if badly spaced.
    // Pages with no text layer at all (Bigby's) are kept whole.
    // Art credits printed sideways up the page edge ("SHAWN WOOD") would join whatever line they sit beside.
    dropped += obs.filter { $0.0.height > $0.0.width * 3 && $0.1.count > 3 }.map { String(format: "p%04d: ", n) + $0.1 }
    obs = obs.filter { !($0.0.height > $0.0.width * 3 && $0.1.count > 3) }
    let heights = obs.map { $0.0.height }.sorted()
    let box = page.bounds(for: .mediaBox)
    if !heights.isEmpty, let layer = page.string, layer.contains(where: { $0.isLetter }) {
        let body = heights[heights.count / 2]
        let notes = obs.filter { o in
            let letters = o.1.filter { $0.isLetter }.count, lower = o.1.filter { $0.isLowercase }.count
            guard o.1.split(separator: " ").count >= 3 && lower * 2 > letters && o.0.height > body * 1.25 else { return false }
            let r = CGRect(x: box.minX + o.0.minX * box.width, y: box.minY + o.0.minY * box.height,
                           width: o.0.width * box.width, height: o.0.height * box.height)
            let under = String((page.selection(for: r)?.string ?? "").lowercased().filter { $0.isLetter })
            let words = o.1.lowercased().split(whereSeparator: { !$0.isLetter }).filter { $0.count >= 4 }
            return !words.isEmpty && words.filter { under.contains($0) }.count * 10 < words.count * 4
        }
        dropped += notes.map { String(format: "p%04d: ", n) + $0.1 }
        obs = obs.filter { o in !notes.contains { $0.0 == o.0 } }
    }
    // Reading order: left column top to bottom, then right column. Lines wider than a column
    // (headings across the page) go with whichever column they start in. Boxes side by side in a
    // column (table cells, a stat block's STR DEX CON ... and their scores) are one line, left to right.
    func rows(_ col: [(CGRect, String)]) -> [String] {
        var out: [[(CGRect, String)]] = []
        for o in col.sorted(by: { $0.0.midY > $1.0.midY }) {
            if let row = out.last, let first = row.first, abs(first.0.midY - o.0.midY) < min(first.0.height, o.0.height) * 0.5 {
                out[out.count - 1].append(o)
            } else {
                out.append([o])
            }
        }
        return out.map { $0.sorted { $0.0.minX < $1.0.minX }.map { $0.1 }.joined(separator: " ") }
    }
    let text = (rows(obs.filter { $0.0.minX < 0.48 }) + rows(obs.filter { $0.0.minX >= 0.48 })).joined(separator: "\n")
    // Vision still reads the odd word as Cyrillic look-alikes ("ВАрНомет", dice as "3dб").
    let latin: [Character: Character] = ["А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T",
                                         "Х": "X", "І": "I", "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i", "м": "m", "т": "t", "н": "h", "к": "k", "в": "b", "п": "n", "б": "6"]
    let clean = String(text.map { latin[$0] ?? $0 })
    try? clean.write(to: out.appendingPathComponent(String(format: "p%04d.txt", n)), atomically: true, encoding: .utf8)
    done += 1
    if done % 20 == 0 { print("\(args[2]): \(done) pages"); fflush(stdout) }
}
try? dropped.joined(separator: "\n").write(to: out.appendingPathComponent("dropped.txt"), atomically: true, encoding: .utf8)
print("\(args[2]): \(dropped.count) margin-note and sideways lines left out (dropped.txt)")
print("\(args[2]): OCR'd \(done) pages -> packs/.text/\(args[2])")
