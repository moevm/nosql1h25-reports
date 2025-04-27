import glob
import sys
sys.path.append('c:/Users/bhunp/Documents/nosql1h25-reports/')

from src.diploma_processing.parsing_docx.docxParser import DocxParser
from src.diploma_processing.stats import CalcStats
from src.diploma_processing.utils import save_diploma_json


if __name__ == "__main__":
    path_to_docx = "src/diploma_processing/testkit/docx_examples"
    path_to_save = "src/diploma_processing/testkit/parsing_examples/"

    docx_list = glob.glob(path_to_docx + '/*.docx')
    parsing_list = []
    for path in docx_list:
        print(path)
        file = open(path, 'rb')
        dp = DocxParser(file)
        dp.read_document()
        parsing_list.append(dp)
    cs = CalcStats()
    diplomas = [cs.calc_stats(e.doc) for e in parsing_list]
    for i in range(len(parsing_list)):
        docx_path = docx_list[i]
        diploma = diplomas[i]
        name = docx_path.replace('docx_examples', 'parsing_examples')
        path = name[:name.rfind('.')] + '.json'
        save_diploma_json(diploma, path)