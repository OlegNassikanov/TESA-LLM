# Codebase Overview for New Contributors

This repository is an early-stage prototype for **TESA-LLM**: a token-efficient semantic abstraction protocol for LLM interactions.

## Repository Layout

- `README.md`: Conceptual overview, goals, and roadmap.
- `tesa.py`: Main Python implementation of marker dictionary compression, delta encoding, binary export, and motif interpretation.
- `tesa_motif.py`: Currently a duplicate of `tesa.py` (likely intended to evolve into a motif-focused module).
- `tesa_packer.c`: Minimal C helper that bit-packs two 14-bit marker IDs into one 32-bit integer.

## Core Components

### 1) `TESACompressor`
The central class maintains:

- A stable marker dictionary (`S1`, `S2`, ...)
- A temporary marker dictionary (`T1`, `T2`, ...)
- Reverse lookup map for phrase deduplication
- Frequency counters for simple pair-based optimization

Main methods:

- `add_to_dictionary(phrase)`: Assigns or reuses markers, with fuzzy reuse based on high string similarity.
- `compress(text)`: Tokenizes by whitespace, opportunistically uses frequent adjacent word pairs, then emits marker IDs encoded with type bits and optional delta coding.
- `decompress(compressed)`: Rebuilds absolute sequence from deltas and resolves IDs back to dictionary values.
- `to_json(compressed)`: JSON serialization helper.
- `to_binary(compressed)`: Binary packet serializer with version byte, count byte, payload, and CRC16.
- `pack_markers(marker1, marker2)`: Calls into C shared library for bit packing.

### 2) Motif Execution Helpers
The module includes a tiny execution model:

- `execute(action, duration)` prints an action
- `interpret_motif(motif)` iterates over note-like action dictionaries

This is a conceptual bridge between symbolic protocol tokens and an action sequence style inspired by musical motifs.

### 3) Native Bit Packing (`tesa_packer.c`)
`pack_markers` places the first marker in upper bits and second marker in lower 14 bits:

`((uint32_t)s1 << 14) | (s2 & 0x3FFF)`

This supports compact low-level representation for marker pairs.

## Notes for Contributors

- The repository is small and exploratory; expect rough edges and duplicated code.
- `tesa.py` and `tesa_motif.py` are currently identical; consolidating them is a practical first cleanup task.
- The Python code expects `./tesa_packer.so` at runtime, but only `tesa_packer.c` is tracked, so local build instructions should be added.
- `fuzzywuzzy` is required for fuzzy matching and should be listed in explicit dependency docs.

## Suggested Learning Path

1. Run through `TESACompressor.compress()` and `decompress()` with a short text to understand marker assignment and delta restoration.
2. Inspect binary export format in `to_binary()` and validate packet layout with a hex dump.
3. Build and load `tesa_packer.so`, then verify `pack_markers()` behavior against Python expectations.
4. Refactor duplicated modules and add tests for round-trip compression/decompression and CRC integrity.
