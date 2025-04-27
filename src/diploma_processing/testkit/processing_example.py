import glob
import sys
sys.path.append('c:/Users/bhunp/Documents/nosql1h25-reports/')

from src.diploma_processing.stats import CalcStats
from src.diploma_processing.utils import save_diploma_json


if __name__ == "__main__":
    path_to_docx = "src/diploma_processing/testkit/docx_examples"
    path_to_save = "src/diploma_processing/testkit/parsing_examples/"

    docx_list = glob.glob(path_to_docx + '/*.docx')
    cs = CalcStats()
    for docx_path in docx_list:
        print(docx_path)
        file = open(docx_path, 'rb')
        diploma = cs.get_diploma_stats(file)
        name = docx_path.replace('docx_examples', 'parsing_examples')
        path = name[:name.rfind('.')] + '.json'
        save_diploma_json(diploma, path)