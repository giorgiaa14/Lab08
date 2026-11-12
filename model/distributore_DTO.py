from dataclasses import dataclass
from database.prezzo_DAO import PrezzoDAO

'''
    DTO (Data Transfer Object) dell'entità Distributore
'''

@dataclass()
class Distributore:
    id: int
    nome: str
    indirizzo: str

    # RELAZIONI
    lista_prezzi: list = None

    def get_prezzi(self):
        """ Aggiorna e Restituisce la lista di prezzi (self.lista_prezzi) associati al distributore"""
        #collego direttamente l'oggetto Distributore ai suoi prezzi giornalieri salvati nel database
        if self.lista_prezzi is None:
            self.lista_prezzi = PrezzoDAO.get_prezzi(self.id)
        return self.lista_prezzi

    def __eq__(self, other):
        return isinstance(other, Distributore) and self.id == other.id

    def __str__(self):
        return f"{self.id} | {self.nome} | Indirizzo: {self.indirizzo}"

    def __repr__(self):
        return f"{self.id} | {self.nome} | Indirizzo: {self.indirizzo}"
