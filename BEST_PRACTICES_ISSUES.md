# ベストプラクティスから外れている箇所（要改善）

以下はこのリポジトリをざっと解析して検出した「改善を推奨する箇所」です。各項目に該当ファイルと該当行番号へのリンクを記載します。

- **`eval` / `exec` の直接使用（セキュリティリスク）**: 任意コード実行につながるため入力の流入経路がある場合は危険です。可能であれば安全なパーサや限定的な評価関数に置き換えてください。
  - [module/datetimeActions.py](module/datetimeActions.py#L25) (eval 実行)
  - [module/datetimeActions.py](module/datetimeActions.py#L32) (eval 登録)
  - [module/defaultActions.py](module/defaultActions.py#L269) (doc example)
  - [module/defaultActions.py](module/defaultActions.py#L276) (eval 実行)
  - [module/defaultActions.py](module/defaultActions.py#L545) (exec 登録)
  - [module/defaultActions.py](module/defaultActions.py#L547) (eval 登録)

- **外部コマンドの直接実行（subprocess 等）**: コマンドインジェクションに注意。外部実行が必要な場合は引数をリストで渡す、入力検証を行う、または安全なラッパーを使用してください。
  - [module/extraActions.py](module/extraActions.py#L4) (import subprocess)
  - [module/extraActions.py](module/extraActions.py#L37) (netsh 実行)
  - [module/extraActions.py](module/extraActions.py#L49) (subprocess.run)
  - [module/defaultActions.py](module/defaultActions.py#L5) (import subprocess)
  - [module/defaultActions.py](module/defaultActions.py#L120) (subprocess.run)
  - [module/defaultActions.py](module/defaultActions.py#L156) (Popen)
  - [module/defaultActions.py](module/defaultActions.py#L186) (Popen)
  - [module/defaultActions.py](module/defaultActions.py#L189) (stdout pipe)
  - [module/defaultActions.py](module/defaultActions.py#L190) (stderr pipe)

- **ワイルドカードインポート (`from ... import *`) の多用**: 名前空間汚染と可読性低下を招きます。明示的なシンボルインポートに置き換えてください。
  - [lib/commonDefine.py](lib/commonDefine.py#L10)
  - [lib/commonDefine.py](lib/commonDefine.py#L11)
  - [readLines.py](readLines.py#L6)
  - [readLines.py](readLines.py#L7)
  - [readLines.py](readLines.py#L8)
  - （他、複数のモジュールで使用）

- **依存関係明示がない**: `requirements.txt` が見つかりません（プロジェクトルートに配置を推奨）。環境再現性のため必須パッケージを列挙してください。
  - ファイル: `requirements.txt` が存在しません

- **ライセンス未記載**: 利用者や貢献者へ許諾を明確にするため、`LICENSE` ファイルを追加してください。
  - ファイル: `LICENSE` が存在しません

- **テスト・CI が無い**: 自動テストや CI（GitHub Actions など）を追加すると品質が保ちやすくなります。

- **機密情報管理の明示不足**: 現在 `param/` 配下に設定がある構成ですが、機密値（パスワードや API キー）を直接 YAML に置かない旨のドキュメントや .env 例があると良いです。

## 推奨対応（優先度順）
1. `eval` / `exec` を使用している箇所を見直す。どうしても必要な箇所は入力のサニタイズ、ホワイトリスト評価、または小さな言語パーサに置換する。
2. 外部コマンド実行周りを安全化する（`shlex.split` か引数リストで渡す、ユーザ入力を直接渡さない）。
3. `from module import *` をやめ、明示的な `from module import name1, name2` に置き換える。
4. `requirements.txt` を作成して依存パッケージを列挙する。
5. `LICENSE` を追加してライセンス方針を明確にする。
6. 機密情報の取り扱い方針を `README.md` や `CONTRIBUTING.md` に明記する。
7. 単体テストと CI を導入して継続的に品質を担保する。

---
※このファイルは自動スキャンによる指摘を手作業でまとめたものです。さらに詳細な修正案や自動修正パッチを希望する場合は、どの項目を優先するか教えてください。
