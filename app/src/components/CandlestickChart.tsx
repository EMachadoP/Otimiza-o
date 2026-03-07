import { useRef, useEffect, useState, useCallback } from 'react';
import type { OHLCV, Pattern, MarketRegime } from '@/types/trading';

interface CandlestickChartProps {
  data: OHLCV[];
  patterns?: Pattern[];
  regime?: MarketRegime | null;
  width?: number;
  height?: number;
  onCandleClick?: (candle: OHLCV) => void;
}

export function CandlestickChart({ 
  data, 
  patterns = [], 
  regime, 
  width = 800, 
  height = 500,
  onCandleClick 
}: CandlestickChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredCandle, setHoveredCandle] = useState<OHLCV | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState({ start: 0, end: 1 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStart = useRef({ x: 0, zoomStart: 0 });

  const padding = { top: 40, right: 80, bottom: 60, left: 10 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const visibleData = data.slice(
    Math.floor(data.length * zoom.start),
    Math.floor(data.length * zoom.end)
  );

  const priceRange = visibleData.reduce(
    (acc, d) => ({
      min: Math.min(acc.min, d.low),
      max: Math.max(acc.max, d.high)
    }),
    { min: Infinity, max: -Infinity }
  );

  const priceExtent = priceRange.max - priceRange.min;
  const priceMin = priceRange.min - priceExtent * 0.05;
  const priceMax = priceRange.max + priceExtent * 0.05;

  const scaleY = (price: number) => {
    return padding.top + chartHeight - ((price - priceMin) / (priceMax - priceMin)) * chartHeight;
  };

  const scaleX = (index: number) => {
    return padding.left + (index / (visibleData.length - 1)) * chartWidth;
  };

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Limpar canvas
    ctx.fillStyle = '#0B1120';
    ctx.fillRect(0, 0, width, height);

    // Desenhar grid
    ctx.strokeStyle = '#1E293B';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);

    // Grid horizontal (preços)
    const priceSteps = 8;
    for (let i = 0; i <= priceSteps; i++) {
      const price = priceMin + (priceMax - priceMin) * (i / priceSteps);
      const y = scaleY(price);
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();

      // Label de preço
      ctx.fillStyle = '#64748B';
      ctx.font = '11px Inter';
      ctx.textAlign = 'left';
      ctx.fillText(price.toFixed(5), width - padding.right + 5, y + 4);
    }

    // Grid vertical (tempo)
    const timeSteps = 10;
    for (let i = 0; i <= timeSteps; i++) {
      const x = padding.left + (chartWidth * i) / timeSteps;
      ctx.beginPath();
      ctx.moveTo(x, padding.top);
      ctx.lineTo(x, height - padding.bottom);
      ctx.stroke();
    }

    ctx.setLineDash([]);

    // Desenhar candles
    const candleWidth = (chartWidth / visibleData.length) * 0.7;

    visibleData.forEach((candle, i) => {
      const x = scaleX(i);
      const yOpen = scaleY(candle.open);
      const yClose = scaleY(candle.close);
      const yHigh = scaleY(candle.high);
      const yLow = scaleY(candle.low);

      const isGreen = candle.close >= candle.open;
      ctx.fillStyle = isGreen ? '#10B981' : '#EF4444';
      ctx.strokeStyle = isGreen ? '#10B981' : '#EF4444';

      // Wick
      ctx.beginPath();
      ctx.moveTo(x, yHigh);
      ctx.lineTo(x, yLow);
      ctx.stroke();

      // Body
      const bodyTop = Math.min(yOpen, yClose);
      const bodyHeight = Math.abs(yClose - yOpen) || 1;
      ctx.fillRect(x - candleWidth / 2, bodyTop, candleWidth, bodyHeight);
    });

    // Desenhar padrões
    patterns.forEach(pattern => {
      const candleIndex = visibleData.findIndex(d => d.time >= pattern.timestamp);
      if (candleIndex >= 0) {
        const x = scaleX(candleIndex);
        const y = scaleY(visibleData[candleIndex].high) - 20;

        // Círculo indicador
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, Math.PI * 2);
        ctx.fillStyle = pattern.direction === 'up' ? '#10B98140' : '#EF444440';
        ctx.fill();
        ctx.strokeStyle = pattern.direction === 'up' ? '#10B981' : '#EF4444';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Ícone do padrão
        ctx.fillStyle = pattern.direction === 'up' ? '#10B981' : '#EF4444';
        ctx.font = '10px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(pattern.direction === 'up' ? '▲' : '▼', x, y + 3);
      }
    });

    // Desenhar regime
    if (regime) {
      const regimeColors: Record<string, string> = {
        trend_up: '#10B981',
        trend_down: '#EF4444',
        range: '#F59E0B',
        range_volatile: '#F97316',
        breakout: '#8B5CF6',
        undefined: '#6B7280'
      };

      const color = regimeColors[regime.type] || '#6B7280';
      
      // Badge de regime
      ctx.fillStyle = color + '40';
      ctx.fillRect(padding.left + 10, padding.top + 10, 140, 30);
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.strokeRect(padding.left + 10, padding.top + 10, 140, 30);

      ctx.fillStyle = color;
      ctx.font = 'bold 12px Inter';
      ctx.textAlign = 'left';
      const regimeLabels: Record<string, string> = {
        trend_up: 'TREND UP',
        trend_down: 'TREND DOWN',
        range: 'RANGE',
        range_volatile: 'RANGE VOLÁTIL',
        breakout: 'BREAKOUT',
        undefined: 'ANALISANDO'
      };
      ctx.fillText(regimeLabels[regime.type] || 'ANALISANDO', padding.left + 20, padding.top + 29);
    }

    // Eixo X - Datas
    ctx.fillStyle = '#64748B';
    ctx.font = '10px Inter';
    ctx.textAlign = 'center';

    const dateStep = Math.ceil(visibleData.length / 8);
    for (let i = 0; i < visibleData.length; i += dateStep) {
      const x = scaleX(i);
      const date = new Date(visibleData[i].time);
      const dateStr = `${date.getDate()}/${date.getMonth() + 1}`;
      ctx.fillText(dateStr, x, height - padding.bottom + 20);
    }

    // Crosshair
    if (hoveredCandle && mousePos.x >= padding.left && mousePos.x <= width - padding.right) {
      ctx.strokeStyle = '#94A3B8';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);

      // Linha vertical
      const candleIndex = visibleData.findIndex(d => d.time === hoveredCandle.time);
      if (candleIndex >= 0) {
        const x = scaleX(candleIndex);
        ctx.beginPath();
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, height - padding.bottom);
        ctx.stroke();

        // Linha horizontal
        const y = mousePos.y;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();
      }

      ctx.setLineDash([]);
    }
  }, [data, patterns, regime, visibleData, width, height, hoveredCandle, mousePos, priceMin, priceMax]);

  useEffect(() => {
    draw();
  }, [draw]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setMousePos({ x, y });

    // Encontrar candle sob o mouse
    if (x >= padding.left && x <= width - padding.right) {
      const relativeX = x - padding.left;
      const index = Math.round((relativeX / chartWidth) * (visibleData.length - 1));
      if (index >= 0 && index < visibleData.length) {
        setHoveredCandle(visibleData[index]);
      }
    }

    if (isDragging) {
      const deltaX = e.clientX - dragStart.current.x;
      const zoomRange = zoom.end - zoom.start;
      const deltaZoom = (deltaX / chartWidth) * zoomRange * 0.5;
      
      setZoom(() => ({
        start: Math.max(0, Math.min(1 - zoomRange, dragStart.current.zoomStart - deltaZoom)),
        end: Math.max(zoomRange, Math.min(1, dragStart.current.zoomStart + zoomRange - deltaZoom))
      }));
    }
  };

  const handleMouseLeave = () => {
    setHoveredCandle(null);
    setIsDragging(false);
  };

  const handleClick = () => {
    if (hoveredCandle && onCandleClick) {
      onCandleClick(hoveredCandle);
    }
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY > 0 ? 1.1 : 0.9;
    const zoomRange = zoom.end - zoom.start;
    const newRange = Math.max(0.05, Math.min(1, zoomRange * zoomFactor));
    const center = (zoom.start + zoom.end) / 2;
    
    setZoom({
      start: Math.max(0, center - newRange / 2),
      end: Math.min(1, center + newRange / 2)
    });
  };

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="rounded-lg cursor-crosshair"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        onWheel={handleWheel}
      />
      
      {/* Tooltip */}
      {hoveredCandle && (
        <div 
          className="absolute bg-slate-800 border border-slate-600 rounded-lg p-3 text-xs pointer-events-none z-10"
          style={{ 
            left: mousePos.x + 10, 
            top: mousePos.y - 80,
            minWidth: 140
          }}
        >
          <div className="text-slate-400 mb-1">
            {new Date(hoveredCandle.time).toLocaleDateString('pt-BR')}
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-1">
            <span className="text-slate-500">Open:</span>
            <span className="text-slate-200 text-right font-mono">{hoveredCandle.open.toFixed(5)}</span>
            <span className="text-slate-500">High:</span>
            <span className="text-emerald-400 text-right font-mono">{hoveredCandle.high.toFixed(5)}</span>
            <span className="text-slate-500">Low:</span>
            <span className="text-red-400 text-right font-mono">{hoveredCandle.low.toFixed(5)}</span>
            <span className="text-slate-500">Close:</span>
            <span className={`text-right font-mono ${hoveredCandle.close >= hoveredCandle.open ? 'text-emerald-400' : 'text-red-400'}`}>
              {hoveredCandle.close.toFixed(5)}
            </span>
            <span className="text-slate-500">Vol:</span>
            <span className="text-slate-200 text-right font-mono">{hoveredCandle.volume.toLocaleString()}</span>
          </div>
        </div>
      )}

      {/* Controles de zoom */}
      <div className="absolute bottom-2 right-2 flex gap-1">
        <button
          onClick={() => setZoom({ start: 0, end: 1 })}
          className="px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs rounded"
        >
          Reset
        </button>
        <button
          onClick={() => {
            const range = zoom.end - zoom.start;
            const newRange = Math.max(0.05, range * 0.8);
            const center = (zoom.start + zoom.end) / 2;
            setZoom({
              start: Math.max(0, center - newRange / 2),
              end: Math.min(1, center + newRange / 2)
            });
          }}
          className="px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs rounded"
        >
          +
        </button>
        <button
          onClick={() => {
            const range = zoom.end - zoom.start;
            const newRange = Math.min(1, range * 1.2);
            const center = (zoom.start + zoom.end) / 2;
            setZoom({
              start: Math.max(0, center - newRange / 2),
              end: Math.min(1, center + newRange / 2)
            });
          }}
          className="px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs rounded"
        >
          -
        </button>
      </div>
    </div>
  );
}
