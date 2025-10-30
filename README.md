# Graph API SharePoint Access Demo

SharePointサイトにアクセスし、ファイルの一覧を取得するStreamlitアプリケーションのサンプルです。

## 機能

- Microsoft Graph APIを使用したSharePointサイトへのアクセス
- ファイルとフォルダの一覧表示
- 2つの認証モード:
  - **Azure Easy Auth**: Azure App Serviceへのデプロイ時
  - **MSAL**: ローカル開発時

## 必要な環境

- Python 3.8以上
- Azure ADアプリケーション登録
- SharePointサイトへのアクセス権限

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/suzukiyuhsuke/graph-api-access-demo.git
cd graph-api-access-demo
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、必要な値を設定します:

```bash
cp .env.example .env
```

`.env`ファイルの内容を編集:

```env
# Azure AD Application Settings
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
TENANT_ID=your-tenant-id

# SharePoint Site Settings
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
```

### 4. Azure ADアプリケーションの登録

1. [Azure Portal](https://portal.azure.com)にアクセス
2. Azure Active Directory > アプリの登録 > 新規登録
3. アプリケーション名を入力
4. サポートされているアカウントの種類を選択
5. リダイレクトURI（Web）: `http://localhost:8501`（ローカル開発用）
6. 登録後、以下の情報を取得:
   - アプリケーション（クライアント）ID
   - ディレクトリ（テナント）ID
7. 証明書とシークレット > 新しいクライアントシークレット を作成
8. APIのアクセス許可 > アクセス許可の追加 > Microsoft Graph > 委任されたアクセス許可:
   - `Sites.Read.All` または `Sites.ReadWrite.All`
   - `Files.Read.All` または `Files.ReadWrite.All`
9. 管理者の同意を付与

## ローカルでの実行

```bash
streamlit run app.py
```

ブラウザが自動的に開きます（通常は`http://localhost:8501`）。

### 使用方法（ローカル）

1. サイドバーの「Sign In with Microsoft」ボタンをクリック
2. ブラウザウィンドウが開き、Microsoftアカウントでサインイン
3. SharePointサイトのURLを入力
4. オプションでフォルダパスを指定
5. 「Fetch Files」ボタンをクリックしてファイル一覧を取得

## Azureへのデプロイ

### 前提条件

- Azure App Serviceの作成
- Easy Authの設定

### デプロイ手順

#### 1. Azure App Serviceの作成

```bash
# リソースグループの作成
az group create --name myResourceGroup --location japaneast

# App Serviceプランの作成
az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1 --is-linux

# Webアプリの作成（Python 3.11）
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name mySharePointApp --runtime "PYTHON:3.11"
```

#### 2. Easy Authの設定

1. Azure Portal > App Service > 認証
2. ID プロバイダーを追加 > Microsoft
3. 新しいアプリ登録を作成するか、既存のものを使用
4. 認証されていないアクセス: ログインを必須にする
5. トークンストア: 有効化
6. APIのアクセス許可で以下を追加:
   - `Sites.Read.All`
   - `Files.Read.All`

#### 3. アプリケーション設定の追加

Azure Portal > App Service > 構成 > アプリケーション設定:

```
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
WEBSITE_AUTH_ENABLED=True
```

#### 4. デプロイ

**方法1: Azure CLI**

```bash
# zipファイルを作成
zip -r app.zip . -x "*.git*" -x "*__pycache__*" -x "*.venv*" -x "*.env"

# デプロイ
az webapp deployment source config-zip --resource-group myResourceGroup --name mySharePointApp --src app.zip
```

**方法2: GitHub Actions**

`.github/workflows/azure-deploy.yml`を作成:

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v2
        with:
          app-name: 'mySharePointApp'
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

#### 5. スタートアップコマンドの設定

Azure Portal > App Service > 構成 > 全般設定 > スタートアップコマンド:

```bash
python -m streamlit run app.py --server.port=8000 --server.address=0.0.0.0
```

## プロジェクト構成

```
graph-api-access-demo/
├── app.py                      # メインアプリケーション
├── requirements.txt            # 依存パッケージ
├── .env.example               # 環境変数のテンプレート
├── .gitignore                 # Git除外設定
├── README.md                  # このファイル
├── auth/                      # 認証モジュール
│   ├── __init__.py
│   ├── azure_auth.py          # Azure Easy Auth
│   └── msal_auth.py           # MSALローカル認証
└── graph/                     # Graph APIクライアント
    ├── __init__.py
    └── sharepoint_client.py   # SharePointクライアント
```

## トラブルシューティング

### ローカル開発

**エラー: CLIENT_ID and TENANT_ID must be set**
- `.env`ファイルが存在し、正しく設定されているか確認
- 環境変数が正しく読み込まれているか確認

**認証エラー**
- Azure ADアプリケーションのリダイレクトURIが正しく設定されているか確認
- APIのアクセス許可が正しく設定され、管理者の同意が付与されているか確認

**SharePointアクセスエラー**
- SharePointサイトのURLが正しいか確認
- ユーザーがSharePointサイトへのアクセス権限を持っているか確認

### Azure デプロイ

**Easy Authが動作しない**
- トークンストアが有効化されているか確認
- 認証設定で「ログインを必須にする」が選択されているか確認

**ファイルが表示されない**
- App ServiceのマネージドIDまたはEasy Authアプリの権限を確認
- `Sites.Read.All`と`Files.Read.All`の権限が付与されているか確認

## セキュリティに関する注意

- `.env`ファイルは絶対にGitにコミットしないでください
- クライアントシークレットは安全に管理してください
- 本番環境では、Azure Key Vaultの使用を推奨します
- 最小限の権限の原則に従ってAPI権限を設定してください

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 参考資料

- [Microsoft Graph API ドキュメント](https://learn.microsoft.com/ja-jp/graph/)
- [Streamlit ドキュメント](https://docs.streamlit.io/)
- [MSAL Python ドキュメント](https://msal-python.readthedocs.io/)
- [Azure App Service Easy Auth](https://learn.microsoft.com/ja-jp/azure/app-service/overview-authentication-authorization)