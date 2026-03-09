import sys
import os

# Adicionar o diretório do servidor ao path para importar os módulos
sys.path.append(os.path.join(os.getcwd(), 'server'))

from core.mql_parser import mql_parser

def test_conversion():
    code = """
    if(!ReverseOnSignal) return;
    if(!CloseCurrentPosition()) return;
    hasPos = false;
    }
    if(!hasPos)
    {
        if(!RSIAllowsSell()) { Print("SKIP SELL: RSI OS"); return; }
        OpenPosition(ORDER_TYPE_SELL);
    }
    return;
    }
    }
    //+------------------------------------------------------------------+
    //-------------------------+
    """
    
    try:
        print("Parsing...")
        parsed = mql_parser.parse(code)
        print("Parsed:", parsed)
        
        print("\nConverting to Python...")
        python_code = mql_parser.convert_to_python(code)
        print("Python Code generated successfully.")
        # print(python_code)
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversion()
