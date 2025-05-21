class Doc:
    def __init__(self):
        self.name = None
        self.author = None
        self.academic_supervisor = None # научный реководитель
        self.year = None
        self.pages = None
        self.words = None

        self.structure = [] # структура всего документа - список разделов,
                            # стостоит из объектов разделов (DocSectoin)


class DocSection():
    def __init__(self):
        self.name = None
        self.text = ''
        
        # таблицы и изображения договорились не читать
        # хотя на счёт таблиц не уверен, что это хорошая идея,
        # можно попробовать потом будет как-то учесть их
        
        self.upper = None
        self.level = None
        
        self.structure = [] # если есть какие-то подразделы - то тут будет список
                            # с ними, по сути список объектов разделов (DocSectoin)

