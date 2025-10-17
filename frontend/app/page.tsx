export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">
          相続計算機 Web
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          日本の民法に基づく相続計算のWebアプリケーション
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            ログイン
          </a>
          <a
            href="/register"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
          >
            新規登録
          </a>
        </div>
        <div className="mt-8 text-sm text-gray-500">
          <p>バージョン 0.1.0（開発中）</p>
        </div>
      </div>
    </main>
  )
}
