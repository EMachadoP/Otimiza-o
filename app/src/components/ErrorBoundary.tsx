import React from 'react';

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends React.Component<
    { children: React.ReactNode; fallback?: React.ReactNode },
    ErrorBoundaryState
> {
    constructor(props: { children: React.ReactNode; fallback?: React.ReactNode }) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('ErrorBoundary caught:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                this.props.fallback || (
                    <div className="flex items-center justify-center min-h-screen bg-slate-950 text-slate-400">
                        <div className="text-center space-y-4">
                            <div className="text-4xl">⚠️</div>
                            <h2 className="text-xl font-bold text-slate-200">Erro ao carregar dados</h2>
                            <p className="text-sm">
                                Verifique se o MetaTrader 5 está aberto e o servidor backend está rodando.
                            </p>
                            <button
                                onClick={() => {
                                    this.setState({ hasError: false, error: null });
                                    window.location.reload();
                                }}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                            >
                                Recarregar
                            </button>
                            {this.state.error && (
                                <p className="text-xs text-slate-600 font-mono mt-2">
                                    {this.state.error.message}
                                </p>
                            )}
                        </div>
                    </div>
                )
            );
        }

        return this.props.children;
    }
}
