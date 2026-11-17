# oqrusk.github.io

公開しているアプリの一覧と、アプリごとの紹介・プライバシーポリシーのページ。GitHub Pages（main ブランチのルート）で配信する。

- 元データ: `src/site.json`（サイト名・連絡先）、`src/apps/<slug>/app.json`（アプリの情報）、`src/apps/<slug>/privacy.md`（ポリシー）
- 生成: `pip install markdown && python3 src/build.py` でルートに HTML を書き出す。生成物もコミットする
- アプリを足す: `src/apps/<slug>/` を作って上の 2 ファイルを置き、生成し直す。ページは `https://oqrusk.github.io/<slug>/`、ポリシーは `.../<slug>/privacy/`
