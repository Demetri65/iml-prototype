import "./globals.css";

export const metadata = {
  title: "Mapillary Snapshot Ingestion",
  description:
    "A Next.js and FastAPI prototype for ingesting and exploring Mapillary street-level imagery.",
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
