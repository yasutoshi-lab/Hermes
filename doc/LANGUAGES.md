# 言語別ドキュメント / Language-Specific Documentation

Hermesのドキュメントは日本語と英語の両方で提供されています。
Hermes documentation is available in both Japanese and English.

## 利用可能な言語 / Available Languages

- **日本語 (Japanese)**: `*_JA.md` ファイル
- **English**: `*_EN.md` ファイル

## ドキュメント構造 / Documentation Structure

### プロジェクトルート / Project Root
- `README.md` - 日本語版
- `README_EN.md` - English version

### doc/ ディレクトリ
- `doc/README_JA.md` - 日本語版インデックス
- `doc/README_EN.md` - English index

### コマンドドキュメント / Command Documentation
Located in `doc/command/`:
- `init_JA.md` / `init_EN.md`
- `run_JA.md` / `run_EN.md`
- `task_JA.md` / `task_EN.md`
- `queue_JA.md` / `queue_EN.md`
- `history_JA.md` / `history_EN.md`
- `log_JA.md` / `log_EN.md`
- `debug_JA.md` / `debug_EN.md`
- `README_JA.md` / `README_EN.md` - Command index

### 依存関係ドキュメント / Dependencies Documentation
Located in `doc/dependencies/`:
- `ollama_JA.md` / `ollama_EN.md`
- `browser-use_JA.md` / `browser-use_EN.md`
- `container-use_JA.md` / `container-use_EN.md`
- `README_JA.md` / `README_EN.md` - Dependencies index

### テストドキュメント / Test Documentation
Located in `doc/test/`:
- `README_JA.md` / `README_EN.md`

## クイックアクセス / Quick Access

### 日本語ユーザー向け / For Japanese Users
```bash
# プロジェクト概要
cat README.md

# ドキュメントインデックス
cat doc/README_JA.md

# コマンドリファレンス
cat doc/command/README_JA.md
cat doc/command/run_JA.md

# 依存関係セットアップ
cat doc/dependencies/README_JA.md
cat doc/dependencies/ollama_JA.md
```

### For English Users
```bash
# Project overview
cat README_EN.md

# Documentation index
cat doc/README_EN.md

# Command reference
cat doc/command/README_EN.md
cat doc/command/run_EN.md

# Dependencies setup
cat doc/dependencies/README_EN.md
cat doc/dependencies/ollama_EN.md
```

## ファイル命名規則 / File Naming Convention

- `*_JA.md` - 日本語版ドキュメント (Japanese version)
- `*_EN.md` - 英語版ドキュメント (English version)
- `*.md` (サフィックスなし) - デフォルトで日本語版

## 翻訳方針 / Translation Policy

### 日本語版に保持される要素 / Elements Preserved in Japanese
- すべてのコマンド、コードブロック
- ファイルパス、URL
- 技術用語（Docker、Ollama等）
- コマンドラインフラグ

### What's Preserved in English
- All commands and code blocks
- File paths and URLs
- Technical terms (Docker, Ollama, etc.)
- Command-line flags

## 貢献 / Contributing

新しいドキュメントを追加する際は、日本語版と英語版の両方を作成してください。
When adding new documentation, please create both Japanese and English versions.

ファイル命名規則：
File naming convention:
- Japanese: `filename_JA.md`
- English: `filename_EN.md`
