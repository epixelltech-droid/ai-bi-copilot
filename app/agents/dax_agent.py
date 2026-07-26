from app.core.llm import llm_text

SYSTEM = '''
You are a senior Power BI developer.
Generate one valid DAX query starting with EVALUATE.
Assume a Sales table with Country, Product, Revenue and Margin.
Return DAX only.
'''

def deterministic_dax(question: str) -> str:
    if "pays" in question.lower() or "country" in question.lower():
        return '''EVALUATE
SUMMARIZECOLUMNS(
    Sales[Country],
    "Revenue", SUM(Sales[Revenue]),
    "Margin", SUM(Sales[Margin])
)
ORDER BY [Revenue] DESC'''
    return '''EVALUATE
TOPN(
    20,
    SUMMARIZECOLUMNS(Sales[Product], "Revenue", SUM(Sales[Revenue])),
    [Revenue], DESC
)'''

def generate_dax(question: str) -> str:
    result = llm_text(SYSTEM, question) or deterministic_dax(question)
    return result.replace("```dax","").replace("```","").strip()
