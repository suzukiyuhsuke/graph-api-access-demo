# 使用方法 / Usage Guide

## ローカル開発環境でのテスト手順

### 1. 環境変数の設定

`.env.example`ファイルをコピーして`.env`を作成し、Azure ADの情報を設定します：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```env
CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
```

### 2. アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザが自動的に開き、`http://localhost:8501`にアクセスします。

### 3. サインイン

1. サイドバーの「🔑 Sign In with Microsoft」ボタンをクリック
2. ブラウザウィンドウが開き、Microsoftアカウントでサインイン
3. アクセス許可を確認し、承認

### 4. SharePointサイトへのアクセス

1. SharePoint Site URLフィールドにサイトのURLを入力
   - 例: `https://yourtenant.sharepoint.com/sites/yoursite`
2. オプション：特定のフォルダパスを指定
   - 例: `Documents/ProjectA`
3. 「🔄 Fetch Files」ボタンをクリック
4. ファイルとフォルダの一覧が表示されます

## Azure環境でのデプロイ後の動作

### Easy Authによる自動認証

Azure App ServiceにEasy Authが設定されている場合：

1. アプリケーションのURLにアクセス
2. 自動的にMicrosoftのサインインページにリダイレクト
3. サインイン完了後、アプリケーションにリダイレクト
4. SharePoint Site URLを入力して「Fetch Files」を実行

### 環境変数の確認

Azure Portal > App Service > 構成 で以下が設定されていることを確認：

```
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
WEBSITE_AUTH_ENABLED=True
```

## トラブルシューティング

### エラー: "CLIENT_ID and TENANT_ID must be set"

**原因**: 環境変数が設定されていない

**解決方法**:
```bash
# .envファイルが存在するか確認
ls -la .env

# .envファイルの内容を確認
cat .env
```

### エラー: "Authentication failed"

**原因**: Azure ADアプリケーションの設定に問題がある

**確認事項**:
1. リダイレクトURIが正しく設定されているか
   - ローカル: `http://localhost:8501`
2. APIのアクセス許可が付与されているか
   - `Sites.Read.All`
   - `Files.Read.All`
3. 管理者の同意が付与されているか

### エラー: "Graph API request failed with status 403"

**原因**: 必要な権限が不足している

**解決方法**:
1. Azure Portal > Azure Active Directory > アプリの登録
2. 対象のアプリケーションを選択
3. APIのアクセス許可 > アクセス許可の追加
4. Microsoft Graph > 委任されたアクセス許可
5. `Sites.Read.All`または`Sites.ReadWrite.All`を追加
6. 管理者の同意を付与

### エラー: "Failed to get site ID"

**原因**: SharePointサイトのURLが間違っている、またはアクセス権限がない

**解決方法**:
1. SharePointサイトのURLを確認
2. ブラウザでSharePointサイトに直接アクセスできるか確認
3. ユーザーがSharePointサイトのメンバーであることを確認

## 開発のヒント

### デバッグモードで実行

```bash
streamlit run app.py --logger.level=debug
```

### MSALのトークンキャッシュをクリア

```bash
# Windowsの場合
rm -rf $HOME/.msal_token_cache.bin

# macOS/Linuxの場合
rm -rf ~/.msal_token_cache.bin
```

### Pythonインタープリタでテスト

```python
from graph.sharepoint_client import SharePointClient

# トークンを取得（別途MSALで取得）
token = "your_access_token_here"

# クライアントを初期化
client = SharePointClient(token)

# サイトIDを取得
site_id = client.get_site_id_by_url("https://yourtenant.sharepoint.com/sites/yoursite")
print(f"Site ID: {site_id}")

# ファイル一覧を取得
files = client.list_files("https://yourtenant.sharepoint.com/sites/yoursite")
for file in files:
    print(f"- {file['name']} ({'folder' if file['folder'] else 'file'})")
```

## セキュリティのベストプラクティス

1. **環境変数の管理**
   - `.env`ファイルは絶対にGitにコミットしない
   - 本番環境ではAzure Key Vaultを使用する

2. **アクセス許可の最小化**
   - 必要最小限の権限のみを付与する
   - `Read`権限で十分な場合は`Write`権限を付与しない

3. **トークンの管理**
   - アクセストークンをログに出力しない
   - トークンの有効期限を考慮する

4. **Easy Authの設定**
   - 認証されていないアクセスをブロックする
   - トークンストアを有効化する

## 参考リンク

- [Microsoft Graph API ドキュメント](https://learn.microsoft.com/ja-jp/graph/)
- [SharePoint REST API](https://learn.microsoft.com/ja-jp/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest)
- [MSAL Python](https://msal-python.readthedocs.io/)
- [Streamlit ドキュメント](https://docs.streamlit.io/)
- [Azure App Service Easy Auth](https://learn.microsoft.com/ja-jp/azure/app-service/overview-authentication-authorization)
