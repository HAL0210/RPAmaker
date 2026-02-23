# RPAmaker (CommandRPA)

テキストベースのシナリオを 1 行ずつ実行して、
キーボード操作・ブラウザ操作・Windows UI 操作などを行う RPA ツールです。

- エントリポイント: `CommandRPA.py`
- シナリオ実行: `readLines.py`
- コマンド実装: `module/*Actions.py`
- 設定: `init.yaml` と `param/**/*.yaml`

## 1. 事前準備

## 対応環境

- Windows（`winsound` / `netsh` / デスクトップ操作を使用）
- Python 3.x

## 必要パッケージ

プロジェクトに `requirements.txt` はないため、まずは以下をインストールしてください。

```powershell
pip install ruamel.yaml pyperclip wcwidth playwright pywinauto pynput
python -m playwright install
```

> 補足:
> - `page` モジュール（Playwright）を使わない場合でも、import 時に `playwright` が必要です。
> - `ui` モジュール利用時は、環境によって追加の Windows 依存が必要になる場合があります。

## 2. フォルダ構成（実行に関係する部分）

- `init.yaml`
  - 起動時の初期設定（`PARAM_FOLDER` / `COMMAND_FOLDER` など）
- `param/`
  - 起動時に再帰的に読み込まれる YAML 群
  - `param/sys/logger.yaml`, `param/sys/option.yaml` が主要設定
- `command/`（デフォルト）
  - 実行するシナリオファイルの格納先

`init.yaml` の既定値:

```yaml
PARAM_FOLDER: param
COMMAND_FOLDER: command
```

## 3. 起動方法

## 対話モード

```powershell
python CommandRPA.py
```

`>` プロンプトで 1 行ずつコマンドを実行します。

## ファイル実行モード

```powershell
python CommandRPA.py <シナリオファイル>
```

- `<シナリオファイル>` が相対パスの場合:
  1. そのままのパス
  2. `COMMAND_FOLDER/<シナリオファイル>`
  の順で探索されます。

例:

```powershell
python CommandRPA.py sample.txt
python CommandRPA.py command/sample.txt
```

## 起動時パラメータ上書き

第 2 引数以降に `key=value` 形式を渡すと、起動前に `setParam` されます。

```powershell
python CommandRPA.py sample.txt init_file_path=init.yaml module_priority=d,k,p
```

## 4. シナリオ記述ルール

1 行 1 コマンドです。

- 空行: 無視
- `#` 始まり: コメント
- 基本形式: `action: args`

例:

```text
print: start
wait: 1
k.type: hello
```

## 変数展開

`$\{key\}` の形式で、パラメータを展開できます。

```text
set: name=world
print: hello ${name}
```

## 代入ショートカット

`:` を使わず、`key=value` の行も実行できます（`set` 相当）。

```text
username=admin
```

## 実行結果の戻り値

コマンドが値を返した場合、その値は `return` パラメータに保存されます。

## 5. モジュールと呼び出し方

コマンド解決は次の順です。

1. `module.action` 形式（明示）
2. `module_priority`（`param/sys/option.yaml`）に従って `action` を解決

既定の `module_priority` は `d,k`（default → keyboard）です。

## 利用可能モジュール（正式名 / 別名）

- `default` / `d`
- `flow` / （別名なし）
- `keyboard` / `k`
- `page` / `p`
- `ui` / `u`
- `datetime` / `dt`
- `sound` / `s`
- `extra` / （別名なし）

## 代表コマンド

### default (`d`)

- `print`, `set`, `setInt`, `setFloat`, `setStr`, `setBool`
- `wait`, `load`, `read`, `cmd`, `exec`, `execAsync`, `eval`
- `bool`, `check`, `help`, `import`, `quit`, `hide`

### flow

- `if`, `elif`, `else`, `fi`

### keyboard (`k`)

- `type`, `key`, `press`, `release`, `tap`, `list`

### page (`p`)

- `open`, `goto`, `tab`, `click`, `doubleClick`, `rightClick`
- `input`, `select`, `focus`, `wait`, `upload`, `screenshot`
- `get`, `exist`, `key`

### ui (`u`)

- `run`, `connect`, `tree`, `inspect`, `inspector`
- `click`, `doubleClick` (`dbClick`), `input`, `target`, `edit`, `get`, `kill`

### datetime (`dt`)

- `eval`

### sound (`s`)

- `play`, `beep`, `msg`

### extra

- `SSID`, `VPN`

> 詳細は実行中に `help` / `help: モジュール名` / `help: コマンド名` を利用してください。

## 6. 制御構文（if / elif / else / fi）

`flow` モジュールの分岐はブロック終端に `fi` が必要です。

```text
set: mode=test
if: ${mode}=prod
print: production
elif: ${mode}=test
print: test mode
else
print: unknown
fi
```

真偽判定は `bool` と同じルールです（`false`, `0`, `off`, 空文字などは偽）。

## 7. サンプルシナリオ

`command/sample.txt` の例:

```text
# 基本動作
print: start
set: user=hal02
print: hello ${user}

# OS コマンド
cmd: echo ok
print: returncode=${returncode}

# キーボード操作（必要に応じてフォーカス先を用意）
k.type: RPAmaker
k.key: ctrl+a

# 分岐
if: ${returncode}=0
print: command success
else
print: command failed
fi

print: end
```

実行:

```powershell
python CommandRPA.py sample.txt
```

## 8. よく使う設定キー

- `param/sys/option.yaml`
  - `READ_LINE_INTERVAL`: 行実行の待機秒
  - `sep`: 引数区切り文字（既定 `,`）
  - `module_priority`: モジュール解決優先順
  - `auto_interactive_when_read_line_except`: ファイル実行失敗時に対話モードへ移行するか
- `param/sys/logger.yaml`
  - ログ出力先・フォーマット・レベル
- `param/app_path.yaml`
  - `ui.run` / `p.browser.executable_path` などで使う実行ファイルパス定義
- `param/url.yaml`
  - `p.open` / `p.goto` で名前解決に使う URL 定義

## 9. 注意点

- `eval` / `cmd` は入力内容をそのまま評価・実行するため、安全なシナリオのみ実行してください。
- `page`・`ui` は対象アプリ/画面状態に強く依存します。
- 実行終了時に `finally` で shutdown hook が呼ばれ、ブラウザ停止などの後処理が実行されます。
