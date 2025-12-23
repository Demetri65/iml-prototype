export default function Page() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-3 px-6 text-center">
      <h1 className="text-2xl font-semibold">Starter Page</h1>
      <p className="text-sm text-neutral-600">Frontend is running.</p>
      <a className="text-sm text-blue-600 underline" href="/api/health">
        Check backend health
      </a>
    </main>
  );
}
