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
        
    def json_to_grupo_familiar(self,grupo_familiar_json):
        
        grupo_familiar = GrupoFamiliar()
        grupo_familiar.qtd_pessoas = grupo_familiar_json['_qtd_pessoas']
        grupo_familiar.renda_total = grupo_familiar_json['_renda_total']
        return grupo_familiar
        
    def json_to_pessoa(self,json_string):
        pessoa = Pessoa()
        
        decoded = json.loads(json_string)
        
        pessoa.nome = decoded['_nome']
        pessoa.data_de_nascimento = decoded['_data_de_nascimento']
        pessoa.sexo = decoded['_sexo']
        pessoa.grupo_familiar = self.json_to_grupo_familiar(decoded['_grupo_familiar'])
        pessoa.is_ja_contribuiu = decoded['_is_ja_contribuiu']
        pessoa.is_rural = decoded['_is_rural']
        pessoa.is_deficiente = decoded['_is_deficiente']
        
        return pessoa
        
        
            
    
    