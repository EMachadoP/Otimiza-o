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
            
            inputs[name] = {
                'type': var_type,
                'default': default,
                'description': description.strip() if description else name,
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

    def _build_python_code(self, parsed: Dict) -> str:
        """Constrói o código Python a partir dos dados do parser."""
        strategy_name = str(parsed.get("name", "Custom_MQL_Strategy")).replace('"""', '\\"\\"\\"')
        strategy_type = str(parsed.get("type", "trend")).replace('"""', '\\"\\"\\"')
        clean_name = self._sanitize_name(strategy_name).lower()

        python_code = f'''import pandas as pd
import pandas_ta as ta

def {clean_name}(df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Estrategia: {strategy_name}
    Tipo: {strategy_type}
    """
    close = df['close']
    signals = pd.Series(0, index=df.index)

'''

        for name, info in parsed.get('inputs', {}).items():
            python_code += f"    {name} = params.get('{name}', {repr(info['default'])})\n"

        if 'ema' in parsed.get('indicators', []):
            python_code += (
                "    fast_period = params.get('FastEMA', params.get('fast_period', 12))\n"
                "    slow_period = params.get('SlowEMA', params.get('slow_period', 26))\n"
                "    fast_ema = ta.ema(close, length=fast_period)\n"
                "    slow_ema = ta.ema(close, length=slow_period)\n"
            )

        if 'rsi' in parsed.get('indicators', []):
            python_code += (
                "    rsi_period = params.get('RsiPeriod', params.get('rsi_period', 14))\n"
                "    rsi = ta.rsi(close, length=rsi_period)\n"
            )

        python_code += "\n    # Logica MQL extraida\n"
        logic = (parsed.get("signals_logic") or "").splitlines()
        if logic:
            for line in logic:
                stripped = line.rstrip()
                if stripped:
                    python_code += f"    # {stripped}\n"
        else:
            python_code += "    # Nenhuma logica extraida do snippet.\n"

        python_code += "\n    return signals\n"
        return python_code

    def convert_to_python(self, mql_code: str) -> str:
        """Converte MQL para Python."""
        parsed = self.parse(mql_code)
        return self._build_python_code(parsed)

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
        return self._build_python_code(parsed)


mql_parser = MQLParser()
