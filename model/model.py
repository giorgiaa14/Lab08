from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        risultato = []
        for distributore in self._distributori:
            # sfrutto l'ORM: chiedo i prezzi direttamente all'oggetto
            prezzi = distributore.get_prezzi()

            # filtro solo quelli del mese corretto
            prezzi_mese = [p.prezzo_litro for p in prezzi if p.data.month == mese]

            if prezzi_mese:
                media = sum(prezzi_mese) / len(prezzi_mese)
                risultato.append((distributore.nome, round(media, 3)))

        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

        # struttura per gestire i giorni tramite indici fissi
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in
                         enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

            # esploroo i distributori
        for id_distributore, prezzi in prezzi_settimana.items():
            prezzo_litro = prezzi[giorno - 1]
            # Filtro per saltare i giorni in cui il database non ha prezzi registrati
            if prezzo_litro is None:
                continue
 # Calcolo costo parziale della giornata
            costo_giorno = prezzo_litro * 100

            # aggiungo 5€ di spostamento se non è il primo giorno e ho cambiato distributore
            if ultimo_distributore is not None and id_distributore != ultimo_distributore:
                costo_giorno += 5

            nuovo_costo = costo_corrente + costo_giorno
            sequenza_parziale.append(id_distributore)

            # vado avanti solo se posso ancora migliorare
            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                self.__ricorsione(sequenza_parziale, giorno + 1, id_distributore, nuovo_costo, prezzi_settimana)

            #annullo l'ultima scelta per provare l'altra strada
            sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        risultato = {}
        for distributore in self._distributori:
            # Manteniamo l'ORM chiamando i prezzi direttamente dal DTO
            prezzi = distributore.get_prezzi()

            # Struttura di sicurezza vista in laboratorio
            risultato[distributore.id] = [None] * 7

            for prezzo in prezzi:
                if prezzo.data.month == mese and 1 <= prezzo.data.day <= 7:
                    giorno_indice = prezzo.data.day - 1
                    risultato[distributore.id][giorno_indice] = prezzo.prezzo_litro

        return risultato