from contagem_de_tempo import FactoryDateTimeFromStrings
from dateutil.relativedelta import relativedelta
from money_mask import real_br_money_mask as real_mask
import json

class Pessoa:
    
    def __init__(self):
        
        self._nome = None
        self._data_de_nascimento = None
        self._idade = None
        self._sexo = None
        self._grupo_familiar = GrupoFamiliar()
        self._is_ja_contribuiu = False
        self._is_rural = False
        self._is_deficiente = False
        self._direitos = []
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        
    @property
    def nome(self):
        return self._nome
        
    @nome.setter
    def nome(self,new_value):
        self._nome = new_value
        
    @property
    def data_de_nascimento(self):
        return self._data_de_nascimento
        
    @data_de_nascimento.setter
    def data_de_nascimento(self,new_value):
        self._data_de_nascimento = new_value
        self._calcula_idade()
        
    @property
    def idade(self):
        return self._idade
        
    def _calcula_idade(self):
        self._idade = CalculaIdade(self.data_de_nascimento).idade
        
    @property
    def sexo(self):
        return self._sexo
        
    @sexo.setter
    def sexo(self,new_value):
        self._sexo = new_value
        
    @property
    def grupo_familiar(self):
        return self._grupo_familiar
        
    @grupo_familiar.setter
    def grupo_familiar(self,new_value):
        self._grupo_familiar = new_value
    
    @property
    def is_ja_contribuiu(self):
        return self._is_ja_contribuiu
        
    @is_ja_contribuiu.setter
    def is_ja_contribuiu(self,new_value):
        self._is_ja_contribuiu = new_value
        
    @property
    def is_rural(self):
        return self._is_rural
        
    @is_rural.setter
    def is_rural(self,new_value):
        self._is_rural = new_value
        
    @property
    def is_deficiente(self):
        return self._is_deficiente
        
    @is_deficiente.setter
    def is_deficiente(self,new_value):
        self._is_deficiente = new_value
        
    @property
    def direitos(self):
        return self._direitos

    def add_direito_analisado(self,new_value):
        self._direitos.append(new_value)

    def direitos_limpar_todos(self,new_value):
        self._direitos = []
        

class CalculaIdade:
    
    def __init__(self,data_de_nascimento):
        self.data_de_nascimento = FactoryDateTimeFromStrings().get_date_time(data_de_nascimento)
        self.today = FactoryDateTimeFromStrings().get_data_atual()
        self._difference = relativedelta(self.today,self.data_de_nascimento)
        self._idade = self._difference.years
        
    @property
    def idade(self):
        return self._idade    
        

class GrupoFamiliar:

    def __init__(self):
        self._qtd_pessoas = 1.00
        self._renda_total = 0.00
        self._renda_per_capita = 0.00

    def imprime(self):
        pass
        #print("Grupo Familiar: Composto por %s pessoas com renda total de R$ %s, o que resulta em renda per-capita de R$%s" %(self.qtd_pessoas(),self.get_renda_total(),self.get_renda_per_capita()))

    @property
    def qtd_pessoas(self):
        return self._qtd_pessoas
        
    @qtd_pessoas.setter
    def qtd_pessoas(self,new_value):
        self._qtd_pessoas = new_value
        self._calcula_renda_per_capita()
        
    def add_pessoa(self):
        self.qtd_pessoas += 1
        
    @property
    def renda_total(self):
        return self._renda_total
        
    @renda_total.setter
    def renda_total(self,new_value):
        self._renda_total = new_value
        self._calcula_renda_per_capita()
        
    def add_renda(self,new_value):
        self.renda_total += float(new_value)
        self._calcula_renda_per_capita()
    
    @property
    def renda_per_capita(self):
        return self._renda_per_capita
        
    @renda_per_capita.setter
    def renda_per_capita(self,new_value):
        self._renda_per_capita = new_value

    @property
    def renda_total_money_mask(self):
        return real_mask(self._renda_total)

    @property
    def renda_per_capita_money_mask(self):
        return real_mask(self._renda_per_capita)

    def _calcula_renda_per_capita(self):
        self.renda_per_capita = float(self.renda_total) / float(self.qtd_pessoas)
        

    