# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
import json

class Questao:
    
    _id = 0
    
    def __init__(self,nome,pergunta):
        self._id = Questao._id
        Questao._id +=1
        self._data_de_cadastramento = datetime.date.today()
        self.quem_perguntou = nome
        self._tags = []
        self.pergunta = pergunta
        self.is_respondida = False
        self.resposta = ""
        
        
    @property
    def id(self):
        return self._id

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @property
    def data_do_cadastramento(self):
        return self._data_de_cadastramento
        
    def data_do_cadastramento_string(self):
        today = self.data_do_cadastramento

        dia = today.day
        mes = today.month
        ano = today.year

        if len(str(dia))==1:
            dia = "0"+str(dia)
    
        if len(str(mes))==1:
            mes = "0"+str(mes)


        return "{}/{}/{}".format(dia,mes,ano)
        
        
    @property
    def add_tag(self,new_value):
        self._tags.append(new_value)
        
    @property
    def tags(self):
        return self._tags
        
    def clean_tags(self):
        self._tags = []
        
    def is_tags_contains(self,value):
        return value in self._tags
        
    def perguntar(self,pergunta):
        self.pergunta = pergunta
        
    def responder(self,resposta):
        self.is_respondida = True
        self.resposta = resposta
        
    def apagar_resposta(self):
        self.is_respondida = False
        self.resposta = ""
        
        
    def questao_as_string(self):
        return "Questão nº:{}\nPergunta cadasttrada por:{}\nPergunta:{}\nResposta:{}\nFoi respondia:{}\nData:{}".format(self.id,self.quem_perguntou,self.pergunta,self.resposta,self.is_respondida,self.data_do_cadastramento_string())
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        
    
        
        