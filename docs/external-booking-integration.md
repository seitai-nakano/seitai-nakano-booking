# 外部予約連携の将来対応

この予約システムは、将来 HOT PEPPER Beauty / SALON BOARD 等の外部予約台帳と連携できるように、外部予約の「予約済み時間」を取り込む受け口を先に用意している。

## 現在の状態

- 外部サービスとはまだ接続していない。
- 現在の予約フロー・空き枠表示は従来どおり動作する。
- `nakano_external_busy_times` は現在空で、現行予約への影響はない。

## 外部予約の受け口

外部側で予約が入った場合、サーバー側の連携処理から `nakano_upsert_external_busy_time(...)` を呼ぶ。

引数:

- `p_provider`: 連携元の識別子。例: `salon_board`
- `p_external_booking_id`: 外部予約ID
- `p_date`: 予約日
- `p_start_time`: 開始時刻
- `p_end_time`: 終了時刻
- `p_status`: `confirmed` / `cancelled` / `pending`

このRPCは `service_role` 専用。ブラウザから直接呼ばないこと。

`confirmed` の外部予約は自動的に以下へ反映される。

1. `nakano_available_slots` の空き枠から除外される。
2. `nakano_month_availability` の月間空き枠集計からも除外される。
3. `nakano_create_booking` の最終確定時にも重複チェックされる。

そのため、外部予約を取り込めるようになれば、既存の予約画面を作り直さずに二重予約防止へ接続できる。

## 自社予約の外部連携用フィールド

`nakano_bookings` には将来の外部連携用として以下を追加済み。

- `booking_source` — 現在は既定値 `direct`
- `external_provider`
- `external_booking_id`

将来、自社予約を外部台帳へ送信できる連携方式が使える場合は、送信成功後に `external_provider` と `external_booking_id` を保存して対応関係を持たせる。

## 将来の接続方式

外部サービス側で利用できる方式に合わせ、Supabase Edge Function などのサーバー側アダプターを1つ追加する。

- Webhook が使える場合: 予約作成・変更・キャンセルを受信して即時反映
- API取得のみ可能な場合: 定期同期で外部予約を取得して反映
- CSV等しか使えない場合: インポート処理を追加して同じ受け口へ流す

いずれの場合も、フロント側の予約画面は原則変更せず、外部予約データを `nakano_external_busy_times` に同期する設計とする。

## 重要

- 外部サービスの認証情報や `service_role` キーをフロントエンドへ置かない。
- 外部予約同期はサーバー側のみで行う。
- 外部予約の更新時も日付単位の advisory lock を使う設計にしてあり、自社予約確定処理との競合を減らしている。
