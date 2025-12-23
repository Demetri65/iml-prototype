import "./globals.css";

export const metadata = {
  title: "Starter App",
  description: "A minimal Next.js + FastAPI starter.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-black antialiased">
        {children}
      </body>
    </html>
  );
}
