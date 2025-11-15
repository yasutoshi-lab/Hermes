# `test_task_service.py`

このファイルは、`hermes_cli.services.task_service.TaskService` の単体テストを格納しています。

## 目的

`TaskService` が担当するタスクのCRUD（作成、読み取り、更新、削除）操作と、それに関連するビジネスロジックが正しく動作することを確認します。

`TaskRepository`（永続化層）への依存は、`pytest` の `tmp_path` fixture を利用して作成された一時ディレクトリを使用することで、実際のファイルシステムとやり取りしつつも、テスト実行環境をクリーンに保ちます。

## テストケース概要

| テスト関数 | 説明 |
| :--- | :--- |
| `test_create_task` | 新しいタスクが正しく作成され、初期ステータスが `scheduled` に設定されることを確認します。 |
| `test_get_task` | 作成済みのタスクをIDで正しく取得できることを確認します。 |
| `test_get_nonexistent_task` | 存在しないタスクIDで取得しようとした場合に `None` が返されることを確認します。 |
| `test_list_tasks` | 複数のタスクが作成された後、すべてのタスクが一覧で取得できることを確認します。 |
| `test_list_tasks_by_status` | `status` パラメータでフィルタリングしてタスク一覧を取得できることを確認します。 |
| `test_update_task_status` | タスクのステータス（例: `scheduled` -> `running`）が正しく更新されることを確認します。 |
| `test_delete_task` | 指定したタスクが正しく削除され、その後取得できなくなることを確認します。 |
| `test_update_nonexistent_task_status` | 存在しないタスクのステータスを更新しようとしても、エラーが発生しないことを確認します。 |

## Fixture

| Fixture名 | スコープ | 説明 |
| :--- | :--- | :--- |
| `task_service` | `function` | 各テスト関数のために、一時的なワークディレクトリ (`tmp_path`) を持つ `TaskService` の新しいインスタンスを生成します。これにより、テスト間の状態の干渉を防ぎます。 |
