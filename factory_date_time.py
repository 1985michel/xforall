import datetime

class FactoryDateTimeFromStrings:
    '''
    Classe que constroi objetos DateTime ao receber uma string
    A classe está preparada para receber strings de data com 10 caracteres quer sejam dd/mm/aaaa ou aaaa/mm/dd ou dd-mm-aaaa ou aaaa-mm-dd
    '''
    def get_date_time(self,str_date):
        marcador = self.get_marcador(str_date)
        date_time_produzido = self._get_data_from_string(str_date,marcador)
        return date_time_produzido
        
    def get_marcador(self,str_date):
        #metodo que seleciona o marcador do split
        if '-' in str_date:
            return '-'
        if '/' in str_date:
            return '/'
            
    def _get_data_from_string(self,str_date,marcador):
        '''
        Método que recebe uma string no formado dd-mm-aaaa ou aaaa-mm-dd
        Retorna um obj DateTime
        '''
        pieces = str_date.split(marcador)
        if(len(pieces[0])==2):
            return self._constroi_data(pieces[2],pieces[1],pieces[0])
        return self._constroi_data(pieces[0],pieces[1],pieces[2])
        
    
    def _constroi_data(self,ano,mes,dia):
        '''
        Método que recebe um obj Tempo e retorna um obj DateTime
        '''
        data = datetime.datetime(int(ano),int(mes),int(dia),0,0,0,0)
        return data

    def get_data_atual(self):
        #retorna um objeto DateTime com o momento presente
        now = datetime.datetime.now()
        return now
        
    def get_dia(self,str_date):
        return self.get_date_time(str_date).day
        
    def get_mes(self,str_date):
        return self.get_date_time(str_date).month
        
    def get_ano(self,str_date):
        return self.get_date_time(str_date).year
        
    def _is_mesmo_mes(self,str_dateOut_v1,str_dateIn_v2):
        if self.get_ano(str_dateOut_v1) == self.get_ano(str_dateIn_v2):
            if self.get_mes(str_dateOut_v1) == self.get_mes(str_dateIn_v2):
                return True
        return False
        
