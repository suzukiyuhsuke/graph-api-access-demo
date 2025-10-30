# アーキテクチャ / Architecture

## システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
        ┌────────────────────────────────┐
        │   Environment Detection        │
        │   (Azure / Local)              │
        └────────────────┬───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ↓                               ↓
┌─────────────────┐           ┌─────────────────┐
│  Azure Easy Auth│           │  MSAL Library   │
│  (Production)   │           │  (Development)  │
└────────┬────────┘           └────────┬────────┘
         │                              │
         └──────────────┬───────────────┘
                        │
                        ↓
              ┌──────────────────┐
              │  Access Token    │
              └────────┬─────────┘
                       │
                       ↓
            ┌────────────────────┐
            │  Streamlit App     │
            │  (app.py)          │
            └──────────┬─────────┘
                       │
                       ↓
            ┌────────────────────┐
            │  SharePoint Client │
            │  (Graph API)       │
            └──────────┬─────────┘
                       │
                       ↓
         ┌─────────────────────────┐
         │  Microsoft Graph API    │
         │  (graph.microsoft.com)  │
         └────────────┬────────────┘
                      │
                      ↓
         ┌─────────────────────────┐
         │  SharePoint Online      │
         │  (Files & Folders)      │
         └─────────────────────────┘
```

## モジュール構成

### 1. アプリケーション層 (`app.py`)

**責任**:
- ユーザーインターフェースの提供
- 環境検出（Azure vs ローカル）
- 認証フローの制御
- ファイル一覧の表示

**主要機能**:
- `is_running_on_azure()`: 実行環境を判定
- `get_access_token()`: 環境に応じた認証方法を選択
- `display_file_list()`: ファイル一覧を表示
- `main()`: メインアプリケーションロジック

### 2. 認証層 (`auth/`)

#### 2.1 Azure Easy Auth (`auth/azure_auth.py`)

**責任**:
- Azure App ServiceのEasy Authからトークンを取得
- ユーザー情報の取得

**主要機能**:
- `get_azure_easyauth_token()`: Easy Authヘッダーからトークンを取得
- `get_user_info_from_easyauth()`: ユーザー情報を取得

**動作フロー**:
```
1. Easy Authが自動的に認証を処理
2. アプリケーションはHTTPヘッダーからトークンを取得
   - X-MS-TOKEN-AAD-ACCESS-TOKEN
3. トークンを返却
```

#### 2.2 MSAL認証 (`auth/msal_auth.py`)

**責任**:
- ローカル開発時の対話型認証
- トークンのキャッシュ管理

**主要機能**:
- `init_msal_app()`: MSAL PublicClientApplicationの初期化
- `get_msal_token()`: 対話型認証でトークンを取得
- `get_msal_token_with_client_secret()`: クライアントシークレットでトークンを取得

**動作フロー**:
```
1. ユーザーが「Sign In」ボタンをクリック
2. MSALがブラウザウィンドウを開く
3. ユーザーがMicrosoftアカウントでサインイン
4. 認証完了後、トークンを取得
5. トークンをセッションステートに保存
```

### 3. Graph API層 (`graph/`)

#### 3.1 SharePointクライアント (`graph/sharepoint_client.py`)

**責任**:
- Microsoft Graph APIとの通信
- SharePointサイトへのアクセス
- ファイルとフォルダの操作

**主要機能**:
- `get_site_id_by_url()`: SharePointサイトのIDを取得
- `list_files()`: ファイルとフォルダの一覧を取得
- `get_file_content()`: ファイルの内容をダウンロード
- `search_files()`: ファイルを検索

**Graph APIエンドポイント**:
```
- サイト取得: GET /sites/{hostname}:{site-path}
- ファイル一覧: GET /sites/{site-id}/drive/root/children
- フォルダ内一覧: GET /sites/{site-id}/drive/root:/{path}:/children
- ファイル検索: GET /sites/{site-id}/drive/root/search(q='{query}')
- ファイル取得: GET /sites/{site-id}/drive/root:/{path}:/content
```

## 認証フロー

### ローカル環境（MSAL）

```
┌──────────┐      ┌──────────────┐      ┌──────────────┐      ┌────────────┐
│  User    │─────>│  Streamlit   │─────>│    MSAL      │─────>│  Azure AD  │
│          │      │     App      │      │   Library    │      │            │
└──────────┘      └──────┬───────┘      └──────┬───────┘      └─────┬──────┘
                         │                     │                     │
                         │  1. Sign In Click   │                     │
                         │────────────────────>│                     │
                         │                     │  2. Open Browser    │
                         │                     │────────────────────>│
                         │                     │                     │
                         │                     │  3. User Sign In    │
                         │                     │<────────────────────│
                         │                     │                     │
                         │  4. Access Token    │  4. Return Token    │
                         │<────────────────────│<────────────────────│
                         │                     │                     │
                         │  5. Call Graph API  │                     │
                         │────────────────────────────────────────────>
                         │                                           Graph API
```

### Azure環境（Easy Auth）

```
┌──────────┐      ┌──────────────┐      ┌──────────────┐      ┌────────────┐
│  User    │─────>│  Easy Auth   │─────>│  Streamlit   │─────>│ Graph API  │
│          │      │  (App Svc)   │      │     App      │      │            │
└──────────┘      └──────┬───────┘      └──────┬───────┘      └────────────┘
                         │                     │
                         │  1. HTTP Request    │
                         │────────────────────>│
                         │                     │
                         │  2. No Token        │
                         │     Redirect to AD  │
                         │<────────────────────│
                         │                     │
                         │  3. Sign In         │
                         │  at Azure AD        │
                         │                     │
                         │  4. Token in Header │
                         │────────────────────>│
                         │                     │
                         │                     │  5. Call Graph API
                         │                     │───────────────────>
```

## データフロー

### ファイル一覧取得の流れ

```
1. User Input
   ↓
   SharePoint Site URL: https://tenant.sharepoint.com/sites/mysite
   Folder Path: Documents/Project
   ↓

2. SharePointClient.get_site_id_by_url()
   ↓
   GET https://graph.microsoft.com/v1.0/sites/tenant.sharepoint.com:/sites/mysite
   ↓
   Response: { "id": "tenant.sharepoint.com,abc123,def456" }
   ↓

3. SharePointClient.list_files()
   ↓
   GET https://graph.microsoft.com/v1.0/sites/{site-id}/drive/root:/Documents/Project:/children
   ↓
   Response: {
     "value": [
       {
         "id": "file-id-1",
         "name": "document.docx",
         "size": 12345,
         "lastModifiedDateTime": "2025-10-30T12:00:00Z",
         "webUrl": "https://..."
       },
       ...
     ]
   }
   ↓

4. Format and Display
   ↓
   📄 document.docx
   Size: 12.05 KB
   Modified: 2025-10-30
```

## セキュリティアーキテクチャ

### 1. トークン管理

- **ローカル**: Streamlitのセッションステートに保存
- **Azure**: Easy Authが管理、HTTPヘッダーで提供
- **有効期限**: MSALが自動的にキャッシュと更新を管理

### 2. アクセス制御

```
Azure AD
  ↓ (認証)
User Principal
  ↓ (権限チェック)
Graph API
  ↓ (アクセス許可)
SharePoint Site
  ↓ (サイト権限)
Files & Folders
```

### 3. 最小権限の原則

必要な権限のみを要求：
- `Sites.Read.All`: SharePointサイトの読み取り
- `Files.Read.All`: ファイルの読み取り

## デプロイアーキテクチャ

### Azure App Service

```
┌─────────────────────────────────────────────┐
│           Azure App Service                 │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │       Easy Auth Middleware         │    │
│  └──────────────┬─────────────────────┘    │
│                 │                           │
│  ┌──────────────▼─────────────────────┐    │
│  │     Python 3.11 Runtime            │    │
│  │                                     │    │
│  │  ┌──────────────────────────────┐  │    │
│  │  │   Streamlit Application      │  │    │
│  │  │   (app.py)                   │  │    │
│  │  └──────────────────────────────┘  │    │
│  │                                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Environment Variables:                     │
│  - SHAREPOINT_SITE_URL                     │
│  - WEBSITE_AUTH_ENABLED=True               │
└─────────────────────────────────────────────┘
         │
         │ HTTPS
         ↓
   ┌─────────────────┐
   │  Microsoft      │
   │  Graph API      │
   └─────────────────┘
```

### CI/CD パイプライン

```
GitHub Repository
  ↓
  Push to main branch
  ↓
GitHub Actions
  ↓
  1. Checkout code
  2. Setup Python 3.11
  3. Install dependencies
  4. Deploy to Azure
  ↓
Azure App Service
```

## 拡張性

### 追加可能な機能

1. **ファイルアップロード**
   - `SharePointClient.upload_file()`を追加
   - Graph API: `PUT /sites/{site-id}/drive/root:/{path}:/content`

2. **ファイルダウンロード**
   - `SharePointClient.download_file()`を実装
   - Streamlitのダウンロードボタンを追加

3. **フォルダ作成**
   - `SharePointClient.create_folder()`を追加
   - Graph API: `POST /sites/{site-id}/drive/root/children`

4. **ファイル検索機能**
   - 既存の`search_files()`を活用
   - UIに検索フィールドを追加

5. **マルチサイト対応**
   - サイト一覧を取得
   - ドロップダウンでサイトを選択

## パフォーマンス考慮事項

1. **トークンキャッシュ**
   - MSALが自動的にキャッシュを管理
   - セッション間で再利用

2. **ページネーション**
   - Graph APIは大量データの場合ページング
   - `@odata.nextLink`を使用して次のページを取得

3. **並列処理**
   - 複数のファイル操作を並列化可能
   - `asyncio`や`concurrent.futures`を使用

## エラーハンドリング

各層でのエラーハンドリング：

1. **Graph API層**
   - HTTPステータスコードをチェック
   - 詳細なエラーメッセージを抽出

2. **認証層**
   - トークン取得失敗
   - 有効期限切れ

3. **アプリケーション層**
   - ユーザーフレンドリーなエラーメッセージ
   - リトライロジック
