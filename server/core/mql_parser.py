"""
Parser para extrair estratégias de código MQL4/5.
Converte código MQL em estratégias Python executáveis.
"""

import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MQLParser:
    """Parser de código MQL4/5 para estratégias Python."""
    
    def __init__(self):
        self.indicators_map = {
            'iMA': 'ema',
            'iRSI': 'rsi',
            'iMACD': 'macd',
            'iATR': 'atr',
            'iBands': 'bbands',
            'iStochastic': 'stoch',
            'iCCI': 'cci',
            'iADX': 'adx',
            'iOBV': 'obv',
            'iMFI': 'mfi',
            'iSAR': 'psar',
            'iWPR': 'willr',
        }

    def parse(self, mql_code: str) -> Dict:
        """
        Parse código MQL e extrai informações da estratégia.
        """
        validation_errors = self._validate_mql_structure(mql_code)

        try:
            return {
                'name': self._extract_name(mql_code),
                'type': self._detect_type(mql_code),
                'inputs': self._extract_inputs(mql_code),
                'indicators': self._extract_indicators(mql_code),
                'signals_logic': self._extract_signals_logic(mql_code),
                'errors': validation_errors,
            }
        except Exception as e:
            logger.error("Error parsing MQL", exc_info=True)
            return {
                'name': 'Error_Parsing',
                'type': 'trend',
                'inputs': {},
                'indicators': [],
                'signals_logic': mql_code.strip(),
                'errors': validation_errors + [str(e)],
            }

    def _extract_name(self, code: str) -> str:
        """Extrai nome do EA do código."""
        name_match = re.search(r'#property\s+name\s+"([^"]+)"', code, re.IGNORECASE)
        if name_match:
            return name_match.group(1)

        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            return class_match.group(1)

        return "Custom_MQL_Strategy"

    def _sanitize_name(self, name: str) -> str:
        """Sanitiza o nome para ser um identificador Python válido."""
        sanitized = re.sub(r'[^\w]', '_', name)
        if sanitized and sanitized[0].isdigit():
            sanitized = "strategy_" + sanitized
        return sanitized or "custom_strategy"

    def _detect_type(self, code: str) -> str:
        """Detecta o tipo de estratégia baseado no código."""
        code_lower = code.lower()

        if 'reversal' in code_lower or 'oversold' in code_lower or 'overbought' in code_lower:
            return 'reversal'
        if 'breakout' in code_lower or 'donchian' in code_lower or 'break' in code_lower:
            return 'breakout'
        if 'scalp' in code_lower or 'momentum' in code_lower:
            return 'scalping'
        if 'mean' in code_lower and 'reversion' in code_lower:
            return 'mean_reversion'
        return 'trend'

    def _extract_inputs(self, code: str) -> Dict[str, Dict]:
        """Extrai parâmetros input do código MQL."""
        inputs = {}
        pattern = r'(?:input|extern)\s+(\w+)\s+(\w+)\s*=\s*([^;]+);(?:\s*//\s*(.*))?'

        for match in re.finditer(pattern, code, re.IGNORECASE):
            var_type, name, default_value, description = match.groups()
            
            # Normalização de nome: Remover prefixo "Inp" ou "input" comumente usado
            clean_name = name
            if name.lower().startswith('inp') and len(name) > 3:
                clean_name = name[3:]
                # Lowercase first letter if it was InpSomething -> something
                if clean_name:
                    clean_name = clean_name[0].lower() + clean_name[1:]
            
            clean_val = default_value.strip().split('//')[0].strip()

            try:
                if var_type.lower() in ['int', 'integer', 'long', 'uint', 'uchar', 'short']:
                    default = int(re.sub(r'[^\d\-]', '', clean_val)) if any(c.isdigit() for c in clean_val) else 0
                elif var_type.lower() in ['double', 'float']:
                    default = float(re.sub(r'[^\d\.\-]', '', clean_val)) if any(c.isdigit() for c in clean_val) else 0.0
                elif var_type.lower() == 'bool':
                    default = clean_val.lower() == 'true'
                else:
                    default = clean_val.strip('"\'')
            except Exception:
                default = clean_val.strip('"\'')
            
            inputs[clean_name] = {
                'type': var_type,
                'default': default,
                'description': description.strip() if description else clean_name,
                'original_name': name # Guardar original se precisar
            }

        return inputs

    def _extract_indicators(self, code: str) -> List[str]:
        """Extrai indicadores técnicos utilizados."""
        indicators = []

        for mql_func, py_name in self.indicators_map.items():
            if re.search(rf'{mql_func}\s*\(', code):
                indicators.append(py_name)

        return indicators

    def _validate_mql_structure(self, code: str) -> List[str]:
        """Valida se o código MQL parece completo e balanceado."""
        errors = []

        open_braces = code.count('{')
        close_braces = code.count('}')

        if 'OnTick' not in code and 'OnCalculate' not in code:
            errors.append("Snippet sem OnTick/OnCalculate; a conversão será parcial.")

        if open_braces != close_braces:
            errors.append(
                f"Número de chaves incompatível: {open_braces} abre vs {close_braces} fecha."
            )

        return errors

    def _extract_block_body(self, code: str, func_pattern: str) -> str:
        """Extrai o corpo de uma função MQL usando balanceamento de chaves."""
        match = re.search(func_pattern, code, re.IGNORECASE)
        if not match:
            return ""

        start = match.end()
        brace_start = code.find('{', start)
        if brace_start == -1:
            return ""

        depth = 0
        i = brace_start
        while i < len(code):
            ch = code[i]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return code[brace_start + 1:i].strip()
            i += 1

        return ""

    def _extract_signals_logic(self, code: str) -> str:
        """Extrai a lógica de sinais de entrada/saída de OnTick ou OnCalculate."""
        tick_body = self._extract_block_body(code, r'void\s+OnTick\s*\([^)]*\)')
        if tick_body:
            return tick_body

        calc_body = self._extract_block_body(code, r'int\s+OnCalculate\s*\([^)]*\)')
        if calc_body:
            return calc_body

        snippet = code.strip()
        return snippet if snippet else ""

    def _extract_signal_logic_detailed(self, code: str) -> Dict:
        """Extrai lógica de sinais detalhada do MQL."""
        
        # Encontrar função de sinal (CheckEntrySignal, OnTick, etc.)
        signal_patterns = [
            r'int\s+(\w+)\s*\([^)]*\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
            r'void\s+OnTick\s*\([^)]*\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
        ]
        
        for pattern in signal_patterns:
            match = re.search(pattern, code, re.DOTALL)
            if match:
                logic = match.group(2) if len(match.groups()) > 1 else match.group(1)
                
                # Extrair condições
                conditions = []
                
                # Padrão: if (condição) return 1;
                if_matches = re.findall(r'if\s*\(([^)]+)\)\s*return\s*([-\d]+)', logic)
                for cond, signal in if_matches:
                    conditions.append({
                        'condition': cond.strip(),
                        'signal': int(signal)
                    })
                
                return {'conditions': conditions, 'raw_logic': logic}
        
        return {'conditions': [], 'raw_logic': ''}

    def _mql_condition_to_python(self, condition: str) -> str:
        """Converte condição MQL para Python."""
        
        # Substituir funções MQL
        replacements = {
            'iMA': 'ta.ema(close, length={})',
            'iRSI': 'ta.rsi(close, length={})',
            'iMACD': 'ta.macd(close)',
            'iATR': 'ta.atr(high, low, close, length={})',
            'iBands': 'ta.bbands(close, length={})',
            'Symbol()': 'symbol',
            'PERIOD_CURRENT': 'timeframe',
            'PRICE_CLOSE': '',
            'MODE_EMA': '',
        }
        
        result = condition
        for mql, py in replacements.items():
            result = result.replace(mql, py)
        
        # Remover parâmetros vazios
        result = re.sub(r'\(\s*\)', '()', result)
        
        return result

    def convert_to_python(self, mql_code: str) -> str:
        """Converte código MQL para Python executável."""
        parsed = self.parse(mql_code)
        
        # Extrair lógica detalhada
        logic = self._extract_signal_logic_detailed(mql_code)
        
        python_code = f'''import pandas as pd
import pandas_ta as ta
import numpy as np

def {self._sanitize_name(parsed['name']).lower()}(df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Estratégia: {parsed['name']}
    Tipo: {parsed['type']}
    """
    close = df['close']
    high = df.get('high', close)
    low = df.get('low', close)
    
    # Parâmetros
'''
        
        # Adicionar parâmetros
        for name, info in parsed.get('inputs', {}).items():
            python_code += f"    {name} = params.get('{name}', {repr(info['default'])})\n"
        
        # Adicionar indicadores
        python_code += '''
    # Indicadores
'''
        for ind in parsed.get('indicators', []):
            if ind == 'ema':
                python_code += '''    fast_ema = ta.ema(close, length=params.get('fastEMA', 9))
    slow_ema = ta.ema(close, length=params.get('slowEMA', 21))
'''
            elif ind == 'rsi':
                python_code += '''    rsi = ta.rsi(close, length=params.get('rsiPeriod', 14))
'''
        
        # Adicionar lógica de sinais convertida
        python_code += '''
    # Sinais
    signals = pd.Series(0, index=df.index)
'''
        
        for cond in logic['conditions']:
            py_cond = self._mql_condition_to_python(cond['condition'])
            signal = cond['signal']
            python_code += f'''
    # {cond['condition']}
    condition = {py_cond}
    signals = np.where(condition, {signal}, signals)
'''
        
        python_code += '''
    return signals
'''
        
        return python_code

    def build_fallback_python(self, mql_code: str, parsed: Optional[Dict] = None) -> str:
        """Constrói um código Python de fallback quando a conversão principal falha."""
        parsed = parsed or {
            "name": "Custom_MQL_Strategy",
            "type": "trend",
            "inputs": {},
            "indicators": [],
            "signals_logic": mql_code.strip(),
            "errors": [],
        }
        
        # Fallback minimalista para evitar loop de recursão
        python_code = f'''import pandas as pd
import pandas_ta as ta
import numpy as np

def {self._sanitize_name(parsed['name']).lower()}(df: pd.DataFrame, params: dict) -> pd.Series:
    # Fallback: EMA Crossover básico
    close = df['close']
    fast_ema = ta.ema(close, length=params.get('fastEMA', 9))
    slow_ema = ta.ema(close, length=params.get('slowEMA', 21))
    signals = np.where(fast_ema > slow_ema, 1, -1)
    return pd.Series(signals, index=df.index)
'''
        return python_code


mql_parser = MQLParser()
