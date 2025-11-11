import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  ja: {
    translation: {
      // Common
      appName: 'Hermes',
      loading: '読み込み中...',
      error: 'エラーが発生しました',
      retry: '再試行',
      cancel: 'キャンセル',
      save: '保存',
      delete: '削除',
      edit: '編集',

      // Auth
      login: 'ログイン',
      logout: 'ログアウト',
      register: '新規登録',
      email: 'メールアドレス',
      username: 'ユーザー名',
      password: 'パスワード',
      confirmPassword: 'パスワード確認',
      forgotPassword: 'パスワードをお忘れですか？',
      alreadyHaveAccount: 'アカウントをお持ちですか？',
      dontHaveAccount: 'アカウントをお持ちでないですか？',

      // Chat
      chat: 'チャット',
      newChat: '新しいチャット',
      typeMessage: 'メッセージを入力...',
      send: '送信',
      uploadFile: 'ファイルをアップロード',
      summary: '要約',
      analysis: '分析',

      // Tasks
      tasks: 'タスク',
      schedule: 'スケジュール',
      scheduleTask: 'タスクを予約',
      pending: '保留中',
      running: '実行中',
      completed: '完了',
      failed: '失敗',

      // Models
      model: 'モデル',
      selectModel: 'モデルを選択',

      // Settings
      settings: '設定',
      language: '言語',
      theme: 'テーマ',
      darkMode: 'ダークモード',
      lightMode: 'ライトモード',

      // Notifications
      taskStarted: 'タスクを開始しました',
      taskCompleted: 'タスクが完了しました',
      taskFailed: 'タスクが失敗しました',
    },
  },
  en: {
    translation: {
      // Common
      appName: 'Hermes',
      loading: 'Loading...',
      error: 'An error occurred',
      retry: 'Retry',
      cancel: 'Cancel',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',

      // Auth
      login: 'Login',
      logout: 'Logout',
      register: 'Register',
      email: 'Email',
      username: 'Username',
      password: 'Password',
      confirmPassword: 'Confirm Password',
      forgotPassword: 'Forgot Password?',
      alreadyHaveAccount: 'Already have an account?',
      dontHaveAccount: "Don't have an account?",

      // Chat
      chat: 'Chat',
      newChat: 'New Chat',
      typeMessage: 'Type a message...',
      send: 'Send',
      uploadFile: 'Upload File',
      summary: 'Summary',
      analysis: 'Analysis',

      // Tasks
      tasks: 'Tasks',
      schedule: 'Schedule',
      scheduleTask: 'Schedule Task',
      pending: 'Pending',
      running: 'Running',
      completed: 'Completed',
      failed: 'Failed',

      // Models
      model: 'Model',
      selectModel: 'Select Model',

      // Settings
      settings: 'Settings',
      language: 'Language',
      theme: 'Theme',
      darkMode: 'Dark Mode',
      lightMode: 'Light Mode',

      // Notifications
      taskStarted: 'Task started',
      taskCompleted: 'Task completed',
      taskFailed: 'Task failed',
    },
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('language') || 'ja',
    fallbackLng: 'ja',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
