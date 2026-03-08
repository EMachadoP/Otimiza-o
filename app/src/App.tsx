import { Dashboard } from '@/sections/Dashboard';
import { Toaster } from '@/components/ui/sonner';
import { ErrorBoundary } from '@/components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Dashboard />
      <Toaster />
    </ErrorBoundary>
  );
}

export default App;
