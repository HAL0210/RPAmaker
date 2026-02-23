# Copilot Instructions for RPAmaker

このファイルは、このリポジトリで Copilot がコード提案・修正を行う際のプロジェクト固有ルールです。

## プロジェクト概要
- エントリポイントは `CommandRPA.py`。
- コマンド解決・1行実行は `readLines.py`。
- 実アクションは `module/*Actions.py` に実装。
- 共通処理は `lib/*.py`。
- テスト用コマンドは `tests/commands/**`、テストコードは `tests/test_*.py`。

## 実装ルール
- 既存スタイルを優先し、差分は最小にする。
- 例外は `except:` を使わず `except Exception as e:` を使う。
- ログは `getMyLogger(__name__)` で取得した logger を使う。
- 新規関数には docstring（Args/Returns/Raises/Params/Note）を付ける。
- `getParam` / `setParam` で使うキーは docstring の `Params` に記載する。

## 命名ルール
- 関数・変数: `snake_case`
- クラス: `PascalCase`
- 定数: `UPPER_SNAKE_CASE`
- テストメソッド: `test_<genre>_<case>_<purpose>`（例: `test_01_05_core_flow_param_branch`）
- テスト用 command: `tests/commands/<genre>/<genre_case>_<name>.txt`

## テストルール
- 変更時は `tests/test_01_00_command_cases.py` を優先的に更新する。
- 新規 command 追加時は対応テストも同時に追加する。
- サブプロセス実行結果は、終了コードと標準出力を検証する。

## 変更時の注意
- `COMMAND_FOLDER` に依存する実行パス解決を壊さない。
- `flow`（if/elif/else/fi）のネスト挙動を壊さない。
- reserved parameter（`${clip}`, `${input}`）の既存仕様を維持する。
- README とテストの整合を維持する。
