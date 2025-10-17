import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '相続計算機 Web',
  description: '日本の民法に基づく相続計算のWebアプリケーション',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  )
}
