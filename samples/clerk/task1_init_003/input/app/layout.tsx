export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {/* TODO: Add Clerk authentication provider */}
        {children}
      </body>
    </html>
  )
}
