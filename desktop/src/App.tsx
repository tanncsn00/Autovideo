import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "./components/layout/AppShell";
import Dashboard from "./pages/Dashboard";
import Create from "./pages/Create";
import Projects from "./pages/Projects";
import Settings from "./pages/Settings";
import Plugins from "./pages/Plugins";
import License from "./pages/License";
import Batch from "./pages/Batch";
import Schedule from "./pages/Schedule";
import Analytics from "./pages/Analytics";
import Manager from "./pages/Manager";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<Create />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/plugins" element={<Plugins />} />
            <Route path="/license" element={<License />} />
            <Route path="/batch" element={<Batch />} />
            <Route path="/schedule" element={<Schedule />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/manager" element={<Manager />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
