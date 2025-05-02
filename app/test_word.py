from docx_utils import generate_pretty_docx

with open("/cfs/home/u021554/clinical_report_generation/web_app/tests/generated_report.json", "r", encoding="utf-8") as f:
    json_string = f.read()

generate_pretty_docx(json_string, "relatorio_testado.docx")
