import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { SystemPage } from './pages/SystemPage';
import { VoiceListPage } from './pages/VoiceListPage';
import { GeneratePage } from './pages/GeneratePage';
import { DashboardPage } from './pages/DashboardPage';
import { HistoryPage } from './pages/HistoryPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <MainLayout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/voices" element={<VoiceListPage />} />
            <Route path="/system" element={<SystemPage />} />
            <Route path="/settings" element={<div className="animate-fade-in">Settings</div>} />
          </Routes>
        </MainLayout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
