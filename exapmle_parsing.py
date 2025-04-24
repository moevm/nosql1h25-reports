import glob
import os

from src.parsing_docx.docxParser import DocxParser
from src.stats import CalcStats
from src.utils import save_diploma_json


if __name__ == '__main__':
    path_to_docx = "./tests/docx_examples"
    docx_list = glob.glob(path_to_docx + '/*.docx')

    parsing_list = []
    for path in docx_list:
        print(path)
        file = open(path, 'rb')
        dp = DocxParser(file)
        dp.read_document()
        parsing_list.append(dp)
    
    cs = CalcStats()
    for i in range(len(docx_list)):
        path = docx_list[i][:docx_list[i].rfind('.')] + '.json'
        diploma = cs.calc_stats(parsing_list[i].doc)
        save_diploma_json(diploma, path)