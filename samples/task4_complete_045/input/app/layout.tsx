export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {/* TODO: Add Clerk authentication */}
        {children}
      </body>
    </html>
  )
}
