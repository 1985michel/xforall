# -*- coding: utf-8 -*-

import json
from contagem_de_tempo import Vinculo,GerenteDeContagem, CalculaCarencia
from pessoa import Pessoa,GrupoFamiliar

class JsonToPython:
    
    '''
    self.reset_id()#reinicia o _id da classe vínculo
    self._duracao_total = Duracao()
    self._carencia_total = 0
    self._lista_de_vinculos = [] #lista de AssistenteDeContagem
    self._meses_a_descontar_da_carencia = 0
    '''
    
    def json_to_vinculo(self,vinculo_json):
        
        empregador = vinculo_json['_empregador']
        data_inicio = vinculo_json['_data_inicio']
        data_fim = vinculo_json['_data_fim']
        _id = vinculo_json['_id']
        _is_facultativo = vinculo_json['_is_facultativo']
        _is_fez_registro_no_mte = vinculo_json['_is_fez_registro_no_mte']
        _ignorado = vinculo_json['_ignorado']
            
        vinculo = Vinculo(empregador,data_inicio,data_fim)
        vinculo.set_id(_id)
        vinculo.is_facultativo = _is_facultativo
        vinculo.is_fez_registro_no_mte = _is_fez_registro_no_mte
        vinculo.set_ignorado(_ignorado)
        return vinculo
    
    def json_to_gerente(self,json_string):
        gerente = GerenteDeContagem()
        
        decoded = json.loads(json_string)
        
        for v in decoded['_lista_de_vinculos']:
            gerente.add_vinculo(self.json_to_vinculo(v))
        return gerente
            
    
    