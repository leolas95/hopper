from declaration_parser import DeclarationParser

class ModelParser:
    def __init__(self, model):
        self.model = model

    def parse_model(self):
        dp = DeclarationParser()
        for decl in self.model.declarations:
            dp.parse_declaration(decl, type(decl).__name__)

        return dp.get_results()
