# Inheritance Calculator Web

日本の民法に基づく相続計算のWebアプリケーション

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 概要

`inheritance-calculator-web`は、コマンドライン操作に抵抗があるユーザーのための直感的なWebインターフェースを提供します。

**主な機能**:
- 🌐 **Webブラウザで利用可能**: インストール不要
- 👥 **ユーザー認証**: 個人のケースを安全に管理
- 📊 **ビジュアル家系図エディター**: ドラッグ&ドロップで編集
- 📈 **リアルタイム計算**: 入力と同時に結果を表示
- 📱 **レスポンシブデザイン**: PC・タブレット・スマホ対応
- 💾 **ケース管理**: 複数の相続ケースを保存・管理

## アーキテクチャ

```
┌─────────────────────────────────────────┐
│          Next.js Frontend               │
│  (React + Tailwind CSS + shadcn/ui)    │
└───────────────┬─────────────────────────┘
                │ REST API
                ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│  ┌───────────────────────────────────┐  │
│  │ inheritance-calculator-core       │  │
│  └───────────────────────────────────┘  │
└─────┬──────────────────────────┬────────┘
      │                          │
┌─────▼──────┐            ┌──────▼────┐
│ PostgreSQL │            │   Neo4j   │
│  (Cases)   │            │  (Graph)  │
└────────────┘            └───────────┘
```

## 技術スタック

### バックエンド
- **FastAPI**: モダンなPython Webフレームワーク
- **PostgreSQL**: メインデータベース
- **Neo4j**: 家系図データ（グラフDB）
- **SQLAlchemy**: ORM
- **Pydantic**: データバリデーション
- **inheritance-calculator-core**: コアビジネスロジック

### フロントエンド
- **Next.js 14**: React フレームワーク
- **TypeScript**: 型安全性
- **Tailwind CSS**: ユーティリティファーストCSS
- **shadcn/ui**: UIコンポーネント
- **TanStack Query**: データフェッチング
- **Zustand**: 状態管理

## クイックスタート

### 前提条件

- Docker & Docker Compose
- Node.js 18+
- Python 3.12+
- uv (Python パッケージマネージャー)

### インストール

```bash
# リポジトリクローン
git clone https://github.com/kazumasakawahara/inheritance-calculator-web.git
cd inheritance-calculator-web

# 環境変数設定
cp .env.example .env
# .env を編集

# Dockerコンテナ起動（PostgreSQL + Neo4j）
docker-compose up -d

# バックエンドセットアップ
cd backend
uv sync
uv run alembic upgrade head

# フロントエンドセットアップ
cd ../frontend
npm install

# 開発サーバー起動
# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### アクセス

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

## 開発

### ディレクトリ構造

```
inheritance-calculator-web/
├── backend/              # FastAPI バックエンド
│   ├── app/
│   │   ├── api/         # APIエンドポイント
│   │   ├── models/      # SQLAlchemyモデル
│   │   ├── schemas/     # Pydanticスキーマ
│   │   ├── services/    # ビジネスロジック
│   │   └── main.py      # エントリーポイント
│   └── tests/           # バックエンドテスト
├── frontend/            # Next.js フロントエンド
│   ├── app/            # App Router
│   ├── components/     # Reactコンポーネント
│   ├── lib/            # ユーティリティ
│   └── hooks/          # カスタムフック
├── docker/             # Docker設定
└── docs/               # ドキュメント
```

### テスト

```bash
# バックエンドテスト
cd backend
uv run pytest

# フロントエンドテスト
cd frontend
npm test
```

## ライセンス

MIT License

---

**関連プロジェクト**:
- [inheritance-calculator-core](https://github.com/kazumasakawahara/inheritance-calculator-core) - コアライブラリ
- [inheritance-calculator](https://github.com/kazumasakawahara/inheritance-calculator) - CLIアプリケーション

**バージョン**: 0.1.0 (開発中)
