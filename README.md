# MikuMikuDB エディター

> Project Diva カスタム楽曲パック用の `mod_pv_db.txt` ファイルを生成する GUI アプリケーション。
>
> **英語版:** `MikuMikuDB Editor.exe`（Python 3.12 で開発され、単体の Windows 実行ファイルとして配布）。

---

## 目次

1. [概要](#概要)
2. [主な機能](#主な機能)
3. [動作環境](#動作環境)
4. [インストール](#インストール)
5. [基本的な使い方](#基本的な使い方)
6. [設定 & 自動保存](#設定--自動保存)
7. [`mod_pv_db.txt`](#mod_pv_dbtxt-の出力)[ の出力](#mod_pv_dbtxt-の出力)
8. [プロジェクト構成](#プロジェクト構成)
9. [ライセンス](#ライセンス)
10. [謝辞](#謝辞)

---

## 概要

MikuMikuDB エディターは、Project Diva カスタム楽曲パック向けの設定ファイル `mod_pv_db.txt` を、コードを書かずに直感的なインターフェースで生成できるツールです。パックのメタ情報、楽曲情報、難易度、クレジット、出演者、複数のオーディオバリアントなどを一貫して管理できます。

* **インターフェース:** 英語（UTF-8）
* **配布形式:** 単一の `.exe`（Windows 10/11 対応）
* **出力:** 暗号化された `.pdpack` プロジェクトファイルと最終的な UTF-8 エンコードの `mod_pv_db.txt`

---

## 主な機能

1. **パック情報設定**

   * **Pack Name**（ローマ字）と任意の**日本語名**を入力
2. **楽曲ライブラリ管理**

   * ツリービューで複数楽曲を一覧表示（PV ID、原題、英題）
   * **Add Song** / **Edit Song** / **Delete Song** ボタンで管理
3. **楽曲設定ダイアログ**（5 タブ）

   * **Basic Information**：PV ID、原題・英題、ひらがな読み、ローマ字、BPM、日付(YYYYMMDD)、サビ開始・長さ
   * **Difficulties**：Easy/Normal/Hard/Extreme/Extra Extreme の有効化と `PV_LV_XX_X` コード設定
   * **Performers**：初音ミク、鏡音リン・レン、巡音ルカ、KAITO、MEIKO、弱音ハク、亞北ネル、咲音メイコ、重音テト から最大6名選択
   * **Credits**：編曲者、作詞者、作曲者／アーティスト、マニピュレーター、ギタープレイヤー、PV 編集者（オリジナル & 英語）
   * **Audio Variants**：別バージョン（デュエット、ミックスなど）ごとに名称、アーティスト、サフィックス、出演者リストを設定
4. **自動 & 手動保存**

   * 5 分ごとに `.pdpack` を自動保存（最大 60 ファイル）
   * **Save Configuration** / **Load Configuration** で手動保存・読み込み
5. **最終出力**

   * **Generate File** ボタンで UTF-8 エンコードの `mod_pv_db.txt` を生成

---

## 動作環境

* **OS:** Windows 10 または 11 (64bit 推奨)
* **依存:** なし（単体の実行ファイル）

---

## インストール方法 (GitHub)

1. [GitHub Releases](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases) ページにアクセス。  
2. **`MikuMikuDB Editor.exe`** をダウンロード。  
3. ダウンロードした `.exe` をダブルクリックで実行。  
   - “発行元を確認できません” 警告が出た場合は、ファイルを右クリック → **プロパティ** → 「全般」タブの下部で **ブロックの解除** にチェック → **適用** → 再度実行。

---

## 代替インストール方法 (GameBanana)

1. 本ツールの **GameBanana** ページ（https://gamebanana.com/tools/19907）にアクセス。  
2. 英語版または日本語版の最新 **`Editor.exe`** をダウンロード。  
3. ダウンロード完了後、`Editor.exe` をダブルクリックで起動 — インストール不要。  
   - Windows のセキュリティ警告が表示された場合：  
     1. ダウンロードしたファイルを右クリック → **プロパティ**  
     2. 「全般」タブの下部で **ブロックの解除** にチェック  
     3. **適用** → **OK**  

---

## 基本的な使い方

1. アプリを起動
2. **Pack Name** と任意の**日本語名**を入力
3. **Add Song** で楽曲を追加

   * **Basic Information** タブで基本情報を入力
   * **Difficulties** タブで難易度とレベルコードを設定
   * **Performers** タブで出演者を選択
   * **Credits** タブでクレジットを入力（任意）
   * **Audio Variants** タブでオーディオバリアントを追加
   * **Accept** で楽曲リストに登録
4. 曲を選択して **Edit Song** / **Delete Song**
5. 必要に応じて **Save Configuration** で `.pdpack` を保存
6. **Generate File** をクリックして `mod_pv_db.txt` を出力

---

## 設定 & 自動保存

* **Auto-Save:** 5 分ごとに `Autosaves/` フォルダへ暗号化 `.pdpack` を保存（最大 60 個）
* **Save Configuration:** 任意のタイミングで手動保存
* **Load Configuration:** 保存済み `.pdpack` の読み込み
* **Load Autosave:** 自動保存ファイル一覧から復元

---

## `mod_pv_db.txt` の出力

1. **Pack Name** が設定され、楽曲が 1 曲以上あることを確認
2. **Generate File** をクリック
3. ファイル名（デフォルト: `mod_pv_db.txt`）と保存先を指定し、**保存**
4. UTF-8 形式の `mod_pv_db.txt` が生成される

---

## プロジェクト構成

```text
MikuMikuDB-Editor/
├── MikuMikuDB Editor.exe    # 実行ファイル
├── Autosaves/               # 自動保存した .pdpack
├── share/                   # 補足ドキュメント
└── libs/                    # 補足ドキュメント
```

---

## ライセンス

本プロジェクトは **MIT ライセンス** の下で公開されています。詳細は [LICENSE](./LICENSE) を参照してください。

---

## 謝辞

* Project Diva モッディングコミュニティに感謝
* 開発・保守: **NyxC**
* ベータテスターおよび協力者の皆様に感謝


------


# MikuMikuDB Editor

> A GUI application for generating `mod_pv_db.txt` files for custom Project Diva song packs.
>
> **English Version:** `MikuMikuDB Editor.exe` (built with Python 3.12, packaged as a standalone Windows executable).

---

## Table of Contents

1. [Overview](#overview)
2. [Core Features](#core-features)
3. [Technical Requirements](#technical-requirements)
4. [Quick Installation](#quick-installation)
5. [Step-by-Step Usage](#step-by-step-usage)
6. [Configuration & Auto-Save](#configuration--auto-save)
7. [Exporting `mod_pv_db.txt`](#exporting-mod_pv_dbtxt)
8. [Project Structure](#project-structure)
9. [License](#license)
10. [Acknowledgments](#acknowledgments)

---

## Overview

MikuMikuDB Editor streamlines the creation of `mod_pv_db.txt`—the configuration file powering custom song packs in Project Diva. With an intuitive interface, modders can define pack metadata, song details, difficulty levels, credits, performers, and even multiple audio variants per track, all without writing code.

* **Interface:** Full English (UTF-8) with clear labels and tooltips.
* **Packaging:** Single `.exe` for Windows 10/11—no Python or dependencies needed.
* **Output:** Encrypted `.pdpack` for project saves plus a final `mod_pv_db.txt` in proper UTF-8.

---

## Core Features

1. **Pack Metadata**

   * Enter **Pack Name** (Roman letters) and optional **Japanese Name**.
2. **Song Library**

   * Manage multiple songs via a tree view: **PV ID**, **Original Name**, **English Name**.
   * Add, edit, or delete songs with dedicated buttons.
3. **Comprehensive Song Editor** (5-tab dialog)

   * **Basic Information**: PV ID, original & English titles, Hiragana reading, Romanized title, BPM, date (YYYYMMDD), chorus (Sabi) start & duration.
   * **Difficulty Levels**: Enable **Easy**, **Normal**, **Hard**, **Extreme**, **Extra Extreme**; assign each a `PV_LV_XX_X` code.
   * **Performers**: Choose up to six vocalists from Hatsune Miku, Kagamine Rin/Len, Megurine Luka, KAITO, MEIKO, Yowane Haku, Akita Neru, Sakine Meiko, Kasane Teto.
   * **Credits**: Optional fields for arranger, lyricist, composer/artist, manipulator, guitar player, and PV editor—each in original and English.
   * **Audio Variants**: Define alternate mixes or duet tracks with separate names, artists, suffixes, and performer sets; enforces Hiragana-only readings and required fields.
4. **Auto-Save & Manual Save**

   * Automatic `.pdpack` backups every 5 minutes (up to 60 files).
   * Manual **Save Configuration** and **Load Configuration** for encrypted project files.
5. **Final Export**

   * Click **Generate File** to create a UTF-8 `mod_pv_db.txt` ready for Project Diva packs.

---

## Technical Requirements

* **Windows 10 or 11** (64‑bit recommended)
* No installation of Python or libraries—just run the executable.

---

## Quick Installation (GitHub)

1. Visit the [GitHub Releases](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases) page.
2. Download **`MikuMikuDB Editor.exe`**.
3. Double-click to run; if Windows warns about an unknown publisher, right-click → **Properties** → Check **Unblock** → **Apply**, then run again.

---

## Alternative Installation Method (GameBanana)

1. Go to this tool’s **GameBanana** [page](https://gamebanana.com/tools/19907).
2. Download the latest version of this tool in English or Japanese.
3. After the download completes, double-click `Editor.exe` to launch it—no installation required.
   - If Windows shows a security warning:
     1. Right-click the downloaded file → **Properties**.
     2. In the **General** tab, check **Unblock** at the bottom.
     3. Click **Apply**, then **OK**.

---

## Step-by-Step Usage

1. **Launch** the application.
2. Input **Pack Name** and optional **Japanese Name**.
3. **Add Songs**:

   * Click **Add Song** to open the editor.
   * Complete **Basic Information**: PV ID, titles, BPM, date, Sabi timing.
   * Configure **Difficulties** and select level codes.
   * Assign **Performers** via dropdown and **Add** button.
   * Fill in **Credits** (optional).
   * Define **Audio Variants** if needed.
   * Click **Accept** to save the song entry.
4. **Manage** the list: select any song and use **Edit** or **Delete**.
5. **Save** your project anytime via **Save Configuration** (\`.pdpack\`).
6. When ready, click **Generate File** to export `mod_pv_db.txt`.

---

## Configuration & Auto-Save

* **Auto-Save:** Every 5 minutes, an encrypted `.pdpack` is saved in the **Autosaves/** folder (max 60 files).
* **Manual Save/Load:** Use **Save Configuration** / **Load Configuration** buttons for secure project files.
* **Load Autosave:** Quickly restore from recent backups via **Load Autosave**.

---

## Exporting `mod_pv_db.txt`

1. Ensure **Pack Name** is set and ≥1 song exists.
2. Click **Generate File**.
3. Choose filename (default `mod_pv_db.txt`) and destination.
4. Confirm to create a UTF-8 `mod_pv_db.txt` with full pack definition.

---

## Project Structure

```
MikuMikuDB-Editor/
├── Editor.exe    # Main executable
├── Autosaves/               # Auto-saved .pdpack files
├── share/                   # Additional resources, schema definitions
└── libs/                    # Additional resources, schema definitions
```

---

## License

This project is released under the **MIT License**. See [LICENSE](./LICENSE) for details.

---

## Acknowledgments

* Inspired by the vibrant Project Diva modding community.
* Developed and maintained by **NyxC**.
* Special thanks to all beta testers and contributors.

![Rin Fuwapuchi](images/rin_fuwapuchi.png)
