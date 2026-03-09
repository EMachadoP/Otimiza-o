"""
Parser para extrair estratégias de código MQL4/5.
Converte código MQL em estratégias Python executáveis.
"""

import re
import ast
from typing import Dict, List, Optional, Callable
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
        
        Returns:
            Dict com: name, type, inputs, indicators, signals_logic
        """
        validation_errors = self._validate_mql_structure(mql_code)
        
        try:
            result = {
                'name': self._extract_name(mql_code),
                'type': self._detect_type(mql_code),
                'inputs': self._extract_inputs(mql_code),
                'indicators': self._extract_indicators(mql_code),
                'signals_logic': self._extract_signals_logic(mql_code),
                'errors': validation_errors
            }
        except Exception as e:
            logger.error(f"Error parsing MQL: {e}", exc_info=True)
            result = {
                'name': 'Error_Parsing',
                'type': 'trend',
                'inputs': {},
                'indicators': [],
                'signals_logic': '',
                'errors': validation_errors + [str(e)]
            }
        
        return result
    
    def _extract_name(self, code: str) -> str:
        """Extrai nome do EA do código."""
        # Procura por #property name ou nome da classe/função
        name_match = re.search(r'#property\s+name\s+"([^"]+)"', code, re.IGNORECASE)
        if name_match:
            return name_match.group(1)
        
        # Tenta extrair do nome do arquivo ou classe
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            return class_match.group(1)
        
        return "Custom_MQL_Strategy"

    def _sanitize_name(self, name: str) -> str:
        """Sanitiza o nome para ser um identificador Python válido."""
        # Remover caracteres especiais, manter apenas letras, números e underlines
        sanitized = re.sub(r'[^\w]', '_', name)
        # Garantir que não comece com número
        if sanitized and sanitized[0].isdigit():
            sanitized = "strategy_" + sanitized
        return sanitized or "custom_strategy"
    
    def _detect_type(self, code: str) -> str:
        """Detecta o tipo de estratégia baseado no código."""
        code_lower = code.lower()
        
        if 'reversal' in code_lower or 'oversold' in code_lower or 'overbought' in code_lower:
            return 'reversal'
        elif 'breakout' in code_lower or 'donchian' in code_lower or 'break' in code_lower:
            return 'breakout'
        elif 'scalp' in code_lower or 'momentum' in code_lower:
            return 'scalping'
        elif 'mean' in code_lower and 'reversion' in code_lower:
            return 'mean_reversion'
        else:
            return 'trend'
    
    def _extract_inputs(self, code: str) -> Dict[str, Dict]:
        """Extrai parâmetros input do código MQL."""
        inputs = {}
        
        # Padrão mais robusto: aceita espaços extras, aspas simples/duplas e comentários opcionais
        pattern = r'(?:input|extern)\s+(\w+)\s+(\w+)\s*=\s*([^;]+);(?:\s*//\s*(.*))?'
        matches = re.finditer(pattern, code, re.IGNORECASE)
        
        for match in matches:
            var_type, name, default_value, description = match.groups()
            
            # Limpar valor padrão (remover comentários inline ou espaços)
            clean_val = default_value.strip().split('//')[0].strip()
            
            try:
                # Normalizar bools MQL
                if var_type.lower() in ['int', 'integer', 'long', 'uint', 'uchar', 'short']:
                    default = int(re.sub(r'[^\d\-]', '', clean_val)) if any(c.isdigit() for c in clean_val) else 0
                elif var_type.lower() in ['double', 'float']:
                    default = float(re.sub(r'[^\d\.\-]', '', clean_val)) if any(c.isdigit() for c in clean_val) else 0.0
                elif var_type.lower() == 'bool':
                    default = clean_val.lower() == 'true'
                else:
                    default = clean_val.strip('"\'')
            except:
                default = clean_val.strip('"\'')
            
            inputs[name] = {
                'type': var_type,
                'default': default,
                'description': description.strip() if description else name
            }
        
        return inputs

    def _extract_indicators(self, code: str) -> List[str]:
        """Extrai indicadores técnicos utilizados."""
        indicators = []
        
        # Busca por chamadas de função iMA, iRSI, etc.
        for mql_func, py_name in self.indicators_map.items():
            if re.search(rf'{mql_func}\s*\(', code):
                indicators.append(py_name)
        
        return indicators

    def _validate_mql_structure(self, code: str) -> List[str]:
        """Valida se o código MQL parece completo e balanceado."""
        errors = []
        
        if 'OnTick' not in code and 'OnCalculate' not in code:
            errors.append("Função OnTick ou OnCalculate não encontrada.")
            
        if code.count('{') != code.count('}'):
            errors.append(f"Número de chaves incompatível: {code.count('{')} abre vs {code.count('}')} fecha.")
            
        return errors

    def _extract_block_body(self, code: str, func_pattern: str) -> str:
        """Extrai o corpo de uma função MQL usando balanceamento de chaves."""
        match = re.search(func_pattern, code, re.IGNORECASE)
        if not match:
            return ""

        start = match.end()
        # Encontra a primeira abertura de chave após a assinatura
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
                    # Retorna o conteúdo entre as chaves externas
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
        
        # Se não achar blocos fechados, tenta capturar tudo se parecer snippet
        if len(code) > 20 and '{' not in code:
             return code.strip()
        
        return ""
    
    def convert_to_python(self, mql_code: str) -> str:
        """
        Converte código MQL para função Python executável.
        
        Returns:
            Código Python como string
        """
        parsed = self.parse(mql_code)
        clean_name = self._sanitize_name(parsed['name'])
        
        python_code = f'''
import pandas as pd
import numpy as np
import pandas_ta as ta

def {clean_name.lower()}(df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Estratégia: {parsed['name']}
    Tipo: {parsed['type']}
    """
    close = df['close']
    
    # Parâmetros
'''
        
        # Adicionar parâmetros
        for name, info in parsed['inputs'].items():
            python_code += f"    {name} = params.get('{name}', {repr(info['default'])})\n"
        
        python_code += '''
    # Indicadores
'''
        
        # Adicionar cálculo de indicadores com defaults do params.get
        for ind in parsed['indicators']:
            if ind == 'ema':
                python_code += (
                    "    fast_period = params.get('FastEMA', params.get('fast_period', 12))\n"
                    "    slow_period = params.get('SlowEMA', params.get('slow_period', 26))\n"
                    "    fast_ema = ta.ema(close, length=fast_period)\n"
                    "    slow_ema = ta.ema(close, length=slow_period)\n"
                )
            elif ind == 'rsi':
                python_code += (
                    "    rsi_period = params.get('RsiPeriod', params.get('rsi_period', 14))\n"
                    "    rsi = ta.rsi(close, length=rsi_period)\n"
                )
            elif ind == 'macd':
                python_code += (
                    "    macd_fast = params.get('macd_fast', 12)\n"
                    "    macd_slow = params.get('macd_slow', 26)\n"
                    "    macd_signal_period = params.get('macd_signal', 9)\n"
                    "    macd_df = ta.macd(close, fast=macd_fast, slow=macd_slow, signal=macd_signal_period)\n"
                    "    macd_line = macd_df.iloc[:, 0] if macd_df is not None else pd.Series(index=df.index, dtype=float)\n"
                )
        
        python_code += '''
    # Sinais
    signals = pd.Series(0, index=df.index)
    
    # Lógica de entrada (extraída do MQL)
    # Note: A lógica específica abaixo é um rascunho baseado na extração.
    '''
        
        if parsed['signals_logic']:
             # Limpar comentários e indentar
             clean_logic = "\n".join(["    # " + line.strip() for line in parsed['signals_logic'].split('\n') if line.strip()])
             python_code += f"\n{clean_logic}\n"
        else:
             python_code += "\n    # Nenhuma lógica de OnTick encontrada no snippet.\n"
             
        python_code += '''
    return signals
'''
        
        return python_code


mql_parser = MQLParser()
