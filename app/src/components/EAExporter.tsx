import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Copy, Download, FileCode, Settings, Check, Loader2 } from 'lucide-react';
import type { Strategy } from '@/types/trading';

interface EAExporterProps {
  strategy: Strategy | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EAExporter({ strategy, open, onOpenChange }: EAExporterProps) {
  const [version, setVersion] = useState<'mql4' | 'mql5'>('mql5');
  const [copied, setCopied] = useState(false);
  const [exportData, setExportData] = useState<{
    mql4: string;
    mql5: string;
    json: string;
    yaml: string;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && strategy) {
      const fetchExport = async () => {
        setIsLoading(true);
        setExportData(null); // Resetar antes de buscar
        try {
          console.log("Fetching export for strategy:", strategy.name, strategy.id);
          const response = await fetch('/api/export-ea', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ strategy }),
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Falha na resposta do servidor');
          }

          const data = await response.json();
          console.log("Export API Response:", data);

          if (data.status === 'success') {
            setExportData(data);
            setError(null);
            // Default to MQL5 if available
            setVersion('mql5');
          } else {
            setError(data.detail || 'Ocorreu um erro ao gerar o código da estratégia.');
            console.error("Export API Error:", data.detail);
          }
        } catch (error: any) {
          setError(error.message || 'Falha na conexão com o servidor.');
          console.error("Failed to fetch export data", error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchExport();
    }
  }, [open, strategy]);

  if (!strategy) return null;

  const mqlCode = version === 'mql4' ? exportData?.mql4 || '' : exportData?.mql5 || '';
  const jsonConfig = exportData?.json || '';
  const yamlConfig = exportData?.yaml || '';

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl bg-slate-900 border-slate-700 text-slate-200 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl flex items-center gap-3">
            <FileCode className="h-5 w-5 text-blue-400" />
            Exportar EA Profissional: {strategy.name}
          </DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <Loader2 className="h-10 w-10 text-blue-500 animate-spin" />
            <p className="text-slate-400">Gerando arquivos profissionais...</p>
          </div>
        ) : (
          <Tabs defaultValue="mql" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-slate-800">
              <TabsTrigger value="mql" className="data-[state=active]:bg-slate-700">
                <FileCode className="h-4 w-4 mr-2" />
                MQL4/5
              </TabsTrigger>
              <TabsTrigger value="json" className="data-[state=active]:bg-slate-700">
                <Settings className="h-4 w-4 mr-2" />
                JSON
              </TabsTrigger>
              <TabsTrigger value="yaml" className="data-[state=active]:bg-slate-700">
                <Settings className="h-4 w-4 mr-2" />
                YAML
              </TabsTrigger>
            </TabsList>

            {/* MQL Tab */}
            <TabsContent value="mql" className="space-y-4">
              <div className="flex items-center justify-between mt-4">
                <div className="flex flex-col gap-1">
                  <select
                    value={version}
                    onChange={(e) => setVersion(e.target.value as 'mql4' | 'mql5')}
                    className="w-32 bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm"
                  >
                    <option value="mql4">MQL4</option>
                    <option value="mql5">MQL5</option>
                  </select>
                  <p className="text-[10px] text-slate-500 italic">* Template MQL profissional (RF-08)</p>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopy(mqlCode)}
                    className="border-slate-600"
                    disabled={!mqlCode}
                  >
                    {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                    Copiar Código
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload(mqlCode, `${strategy.name.replace(/\s+/g, '_')}.${version}`)}
                    className="border-slate-600"
                    disabled={!mqlCode}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Salvar .{version}
                  </Button>
                </div>
              </div>

              <div className="bg-slate-950 rounded-lg p-4 overflow-x-auto max-h-96 overflow-y-auto border border-slate-800">
                {error ? (
                  <div className="h-full flex flex-col items-center justify-center text-red-400 py-10 text-center">
                    <p className="font-bold mb-2">Erro ao gerar código</p>
                    <p className="text-xs text-slate-500 max-w-sm">{error}</p>
                  </div>
                ) : (
                  <pre className="text-xs font-mono text-slate-200 whitespace-pre">
                    {mqlCode || "// Selecione uma versão para visualizar o código"}
                  </pre>
                )}
              </div>
            </TabsContent>

            {/* JSON Tab */}
            <TabsContent value="json" className="space-y-4">
              <div className="flex justify-end gap-2 mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(jsonConfig)}
                  className="border-slate-600"
                  disabled={!jsonConfig}
                >
                  {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                  Copiar
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownload(jsonConfig, `${strategy.name.replace(/\s+/g, '_')}.json`)}
                  className="border-slate-600"
                  disabled={!jsonConfig}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>

              <div className="bg-slate-950 rounded-lg p-4 overflow-x-auto max-h-96 overflow-y-auto border border-slate-800">
                <pre className="text-xs font-mono text-slate-300 whitespace-pre">
                  {jsonConfig}
                </pre>
              </div>
            </TabsContent>

            {/* YAML Tab */}
            <TabsContent value="yaml" className="space-y-4">
              <div className="flex justify-end gap-2 mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(yamlConfig)}
                  className="border-slate-600"
                  disabled={!yamlConfig}
                >
                  {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                  Copiar
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownload(yamlConfig, `${strategy.name.replace(/\s+/g, '_')}.yaml`)}
                  className="border-slate-600"
                  disabled={!yamlConfig}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>

              <div className="bg-slate-950 rounded-lg p-4 overflow-x-auto max-h-96 overflow-y-auto border border-slate-800">
                <pre className="text-xs font-mono text-slate-300 whitespace-pre">
                  {yamlConfig}
                </pre>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}
