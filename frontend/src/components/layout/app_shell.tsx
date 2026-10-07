export const AppShell = (): JSX.Element => (
  <div className="min-h-screen flex flex-col bg-slate-50">
    <header className="flex items-center justify-between p-4 bg-white shadow">
      <h1 className="text-xl font-semibold text-slate-900">Expense Tracker</h1>
      <nav className="flex gap-4">
        <span className="text-slate-500">Dashboard</span>
      </nav>
    </header>
    <main className="flex-1 p-4">
      <p className="text-slate-600">Frontend skeleton is running.</p>
    </main>
  </div>
);
