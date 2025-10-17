# デプロイ前チェックリスト

**作成日**: 2025年10月17日
**プロジェクト**: inheritance-calculator-web
**現在のステータス**: Phase 4 Week 7 完了

---

## 📊 実装状況サマリー

### ✅ 完了した機能

#### Phase 1: プロジェクトセットアップ（Week 1-2）
- ✅ Week 1: プロジェクト基盤構築
  - GitHub リポジトリ作成
  - Docker Compose 設定（PostgreSQL + Neo4j）
  - Frontend/Backend ディレクトリ構造
  - GitHub Actions CI/CD（backend-test, frontend-test, docker-build）

- ✅ Week 2: 認証・認可システム
  - FastAPI-Users + JWT 認証
  - ユーザー登録・ログイン・ログアウト
  - フロントエンド認証フロー（Login/Register ページ）
  - Zustand 認証状態管理
  - Token 管理（localStorage）

#### Phase 2: ケース管理機能（Week 3-4）
- ✅ Week 3-4: CRUD API + フロントエンド UI
  - Case, Person, PersonRelationship モデル（PostgreSQL）
  - Neo4j 統合サービス（家系図グラフ管理）
  - CRUD API エンドポイント（Cases, Persons, Relationships）
  - ダッシュボードページ（案件一覧）
  - 案件作成・詳細ページ
  - ユーザー所有権検証

#### Phase 3: 計算機能統合（Week 5-6）
- ✅ Week 5-6: inheritance-calculator-core 統合
  - CalculationService（Core ライブラリ統合）
  - 計算 API エンドポイント（`/api/cases/{id}/calculate`）
  - ASCII 家系図生成エンドポイント
  - フロントエンド計算結果表示ページ
  - 相続人テーブル表示（分数・パーセンテージ）
  - 計算根拠表示

#### Phase 4: 高度な機能（Week 7）
- ✅ Week 7: 家系図ビジュアルエディター
  - React Flow 統合
  - ドラッグ&ドロップ編集
  - インタラクティブノード・エッジ作成
  - 色分けされたノード（被相続人、配偶者、存命/死亡）
  - リアルタイム更新

---

## 🚧 未完了・オプショナル機能

### Phase 4 Week 8: AI対話インターフェース（オプショナル）
- [ ] Ollama 統合 API
- [ ] チャット UI 実装
- [ ] 自然言語からのエンティティ抽出
- [ ] プロンプトエンジニアリング

**判断**: オプショナル機能。MVP デプロイには不要。

---

## 🔧 デプロイ前に必要な作業

### 1. 環境変数・設定管理

#### バックエンド
- [ ] `.env.example` の整備
  ```bash
  # Production
  DEBUG=false
  SECRET_KEY=<strong-random-key>
  DATABASE_URL=<production-postgres-url>
  NEO4J_URI=<production-neo4j-uri>
  NEO4J_USER=neo4j
  NEO4J_PASSWORD=<secure-password>
  CORS_ORIGINS=https://yourdomain.com
  ```
- [ ] シークレットキーの安全な生成・管理
- [ ] 本番用 CORS 設定
- [ ] データベース接続文字列の環境変数化確認

#### フロントエンド
- [ ] `.env.production` 作成
  ```bash
  NEXT_PUBLIC_API_URL=https://api.yourdomain.com
  ```
- [ ] 本番 API URL 設定

### 2. データベース管理

#### Alembic マイグレーション（未実装）
- [ ] Alembic セットアップ
  ```bash
  cd backend
  uv add alembic
  alembic init alembic
  ```
- [ ] 初期マイグレーションスクリプト作成
  ```bash
  alembic revision --autogenerate -m "Initial migration"
  ```
- [ ] マイグレーション実行手順のドキュメント化
- [ ] ロールバック手順の準備

#### Neo4j 初期化
- [ ] Neo4j 制約・インデックス作成スクリプト
  ```cypher
  CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.person_id IS UNIQUE;
  CREATE INDEX person_case_id IF NOT EXISTS FOR (p:Person) ON (p.case_id);
  ```
- [ ] Neo4j 初期化を Docker Compose に統合

### 3. セキュリティ強化

#### 認証・認可
- [ ] JWT トークンの有効期限設定確認（現在: 30分）
- [ ] リフレッシュトークン機能の実装（オプショナル）
- [ ] パスワード強度要件の実装
  - 最低8文字
  - 英数字+記号
- [ ] レート制限（Rate Limiting）
  - ログイン試行回数制限
  - API リクエスト制限
- [ ] HTTPS 強制（本番環境）

#### データ保護
- [ ] SQL インジェクション対策確認（SQLAlchemy 使用で対策済み）
- [ ] XSS 対策確認（React 使用で対策済み）
- [ ] CSRF 対策（SameSite Cookie）

### 4. パフォーマンス最適化

#### バックエンド
- [ ] データベースクエリの最適化
  - N+1 問題の確認
  - インデックスの追加
- [ ] ペジネーション実装（案件一覧）
  ```python
  @router.get("/", response_model=PaginatedCaseList)
  async def list_cases(skip: int = 0, limit: int = 20):
      # ...
  ```
- [ ] キャッシング戦略（Redis オプショナル）
- [ ] Neo4j クエリの最適化

#### フロントエンド
- [ ] 画像最適化（Next.js Image コンポーネント使用）
- [ ] コード分割確認（Next.js 自動対応）
- [ ] TanStack Query によるキャッシング確認
- [ ] Lighthouse スコア確認（目標: 90+）

### 5. エラーハンドリング・ロギング

#### バックエンド
- [ ] 構造化ロギング実装
  ```python
  import structlog
  logger = structlog.get_logger()
  ```
- [ ] エラートラッキング（Sentry 統合オプショナル）
- [ ] ヘルスチェックエンドポイントの充実
  ```python
  @app.get("/health/ready")
  async def readiness_check():
      # DB接続確認
      # Neo4j接続確認
      return {"status": "ready"}
  ```

#### フロントエンド
- [ ] エラーバウンダリ実装（React Error Boundary）
- [ ] グローバルエラーハンドラー
- [ ] ユーザーフレンドリーなエラーメッセージ

### 6. テスト

#### バックエンドテスト
- [ ] ユニットテストカバレッジ向上（目標: 80%+）
- [ ] 統合テスト追加
  - 認証フロー
  - CRUD 操作
  - 計算ロジック
- [ ] E2E テスト（オプショナル）

#### フロントエンドテスト
- [ ] コンポーネント単体テスト（Jest + Testing Library）
- [ ] E2E テスト（Playwright または Cypress）

### 7. ドキュメント

- [ ] README.md の充実
  - プロジェクト概要
  - ローカル開発環境セットアップ
  - デプロイ手順
- [ ] API ドキュメント（FastAPI 自動生成で対応済み）
- [ ] ユーザーマニュアル作成
- [ ] 運用手順書
  - デプロイ手順
  - バックアップ・リストア手順
  - トラブルシューティング

### 8. Docker・デプロイ設定

#### Dockerfile 最適化
- [ ] マルチステージビルドの実装
  ```dockerfile
  # Backend Dockerfile
  FROM python:3.12-slim AS builder
  RUN pip install uv
  COPY . .
  RUN uv sync --no-dev

  FROM python:3.12-slim
  COPY --from=builder /app/.venv /app/.venv
  CMD ["/app/.venv/bin/uvicorn", "app.main:app"]
  ```

- [ ] Frontend Dockerfile 最適化
  ```dockerfile
  FROM node:20-alpine AS builder
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  FROM node:20-alpine
  COPY --from=builder /app/.next ./.next
  CMD ["npm", "start"]
  ```

#### Docker Compose 本番設定
- [ ] `docker-compose.prod.yml` 作成
- [ ] リバースプロキシ設定（Nginx または Traefik）
- [ ] SSL/TLS 証明書設定（Let's Encrypt）
- [ ] ヘルスチェック設定

### 9. 監視・運用

- [ ] ログ集約（オプショナル: ELK Stack, Loki）
- [ ] メトリクス収集（オプショナル: Prometheus + Grafana）
- [ ] アラート設定
  - サーバーダウン
  - エラー率上昇
  - レスポンス時間劣化
- [ ] バックアップ戦略
  - PostgreSQL 定期バックアップ
  - Neo4j 定期バックアップ

### 10. ブランチ戦略・CI/CD

- [ ] 本番ブランチ（`production`）作成
- [ ] 開発ブランチ（`develop`）作成
- [ ] GitHub Actions ワークフロー調整
  - `develop` → ステージング環境
  - `main` → 本番環境
- [ ] 自動デプロイパイプライン設定

---

## 🎯 MVP デプロイに必要な最小限の作業（優先度順）

### 🔴 Critical（必須）

1. **環境変数管理**
   - [ ] `.env.example` 整備
   - [ ] 本番用シークレットキー生成
   - [ ] 本番 CORS 設定

2. **データベースマイグレーション**
   - [ ] Alembic セットアップ
   - [ ] 初期マイグレーション作成

3. **セキュリティ基本対応**
   - [ ] HTTPS 設定
   - [ ] パスワード強度要件
   - [ ] レート制限（最低限ログインのみ）

4. **本番 Dockerfile 作成**
   - [ ] Backend Dockerfile 最適化
   - [ ] Frontend Dockerfile 最適化
   - [ ] docker-compose.prod.yml

5. **ヘルスチェック**
   - [ ] `/health/ready` エンドポイント実装

### 🟡 Important（推奨）

6. **エラーハンドリング改善**
   - [ ] グローバルエラーハンドラー
   - [ ] ユーザーフレンドリーなエラーメッセージ

7. **ロギング**
   - [ ] 構造化ロギング実装
   - [ ] ログレベル設定

8. **パフォーマンス**
   - [ ] ペジネーション実装
   - [ ] Neo4j インデックス作成

9. **ドキュメント**
   - [ ] README.md 充実
   - [ ] デプロイ手順書

### 🟢 Nice to Have（オプショナル）

10. **監視・運用**
    - [ ] Sentry 統合
    - [ ] メトリクス収集

11. **テスト強化**
    - [ ] E2E テスト
    - [ ] カバレッジ向上

---

## 📝 デプロイ先候補

### オプション 1: VPS（推奨）
- **プラットフォーム**: DigitalOcean, Linode, Vultr
- **構成**: Docker Compose + Nginx
- **コスト**: $10-20/月
- **メリット**: フルコントロール、コスト効率
- **デメリット**: 運用負荷

### オプション 2: PaaS
- **プラットフォーム**: Render, Railway, Fly.io
- **構成**: 自動デプロイ
- **コスト**: $15-30/月
- **メリット**: 簡単デプロイ、自動スケール
- **デメリット**: コスト高、カスタマイズ制限

### オプション 3: クラウド（本格運用向け）
- **プラットフォーム**: AWS, GCP, Azure
- **構成**: ECS/CloudRun + RDS + Managed Neo4j
- **コスト**: $50+/月
- **メリット**: スケーラビリティ、可用性
- **デメリット**: 複雑、コスト高

---

## ✅ 次のアクションアイテム

### 今すぐ実施すべきこと（今日〜3日以内）

1. Alembic セットアップとマイグレーション作成
2. 環境変数整備（`.env.example`, 本番設定）
3. 本番用 Dockerfile 作成
4. ヘルスチェックエンドポイント実装
5. HTTPS/セキュリティ基本設定

### 1週間以内

6. レート制限実装
7. エラーハンドリング改善
8. ペジネーション実装
9. README.md とデプロイ手順書作成
10. テストデプロイ（ステージング環境）

### 2週間以内（本番デプロイ）

11. 本番デプロイ実施
12. 監視設定
13. バックアップ設定
14. ドメイン・SSL 設定

---

## 📊 完成度スコア

| カテゴリ | 完成度 | 備考 |
|---------|--------|------|
| **コア機能** | 95% | AI対話以外完了 |
| **セキュリティ** | 60% | 基本実装済み、強化必要 |
| **パフォーマンス** | 70% | 最適化の余地あり |
| **テスト** | 40% | CI設定済み、カバレッジ要向上 |
| **ドキュメント** | 50% | 基本あり、充実必要 |
| **デプロイ準備** | 30% | Dockerfile・環境設定必要 |

**総合完成度**: **65%**（MVP デプロイ可能レベルまで残り35%）

---

## 🎯 結論

**MVP デプロイまでの推定作業時間**: 2-3日（Critical項目のみ）
**推奨作業時間**: 1週間（Important項目含む）

主要機能は完成しており、デプロイ準備（環境設定、セキュリティ、Dockerfile）を整備すれば、ステージング環境でのテスト運用が可能です。
