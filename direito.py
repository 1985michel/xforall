# -*- coding: utf-8 -*-

from pessoa import Pessoa,GrupoFamiliar
from money_mask import real_br_money_mask as real_money_mask

salario_minimo = 954.00

class Direito:
    
    beneficios = {"21":"Pensão por Morte","25":"Auxílio-Reclusão","31":"Auxílio-Doença","41": "Aposentadoria por Idade","4150":"Aposentadoria por Idade Rural","42":"Aposentadoria por Tempo de Contribuição","80":"Salário Maternidade","87":"Benefício Assistencial à Pessoa Deficiente","88":"Benefício Assistencial à Pessoa Idosa"}
    '''
    Classe base relativa a cada beneficio que a pessoa possa ter ou não direito
    '''
    def __init__(self):
        self._codigo_do_beneficio = None
        self._nome_do_beneficio = None
        self._is_tem_direito = True
        self._razoes_de_nao_ter_direito = []

    @property
    def codigo_do_beneficio(self):
        return self._codigo_do_beneficio
    
    @codigo_do_beneficio.setter
    def codigo_do_beneficio(self,new_value):
        nome = self._get_nome_do_beneficio(new_value)
        if nome != None:
            self._codigo_do_beneficio = new_value
            self._nome_do_beneficio = nome
        
    def _get_nome_do_beneficio(self,codigo):
        return Direito.beneficios[codigo]

    @property
    def nome_do_beneficio(self):
        return self._nome_do_beneficio

    
    def _edit_nome_do_beneficio(self,new_value):
        self._nome_do_beneficio = new_value

    @property
    def is_tem_direito(self):
        return self._is_tem_direito

    @is_tem_direito.setter
    def is_tem_direito(self,new_value):
        self._is_tem_direito = new_value
        
    @property
    def razoes_de_nao_ter_direito(self):
        return self._razoes_de_nao_ter_direito

    def limpar_razoes_de_nao_ter_direito(self):
        self._razoes_de_nao_ter_direito = []

    def registra_nao_ter_direito(self,new_value):
        self._razoes_de_nao_ter_direito.append(new_value)
        self.is_tem_direito = False
        
        
        
        
class AnaliseDeDireitos:
    def __init__(self,pessoa,gerente):
        self.pessoa = pessoa
        self.gerente = gerente
        self._analisarAposentadorias()
        self._analisarLOAS()
        
    def _analisarAposentadorias(self):
        self.pessoa.add_direito_analisado(AnaliseB41(self.pessoa,self.gerente).direito)
        self.pessoa.add_direito_analisado(AnaliseB42(self.pessoa,self.gerente).direito)
        if self.pessoa.is_rural:
            self.pessoa.add_direito_analisado(AnaliseB4150(self.pessoa,self.gerente).direito)
    
    def _analisarLOAS(self):
        self.pessoa.add_direito_analisado(AnaliseB87(self.pessoa).direito)
        self.pessoa.add_direito_analisado(AnaliseB88(self.pessoa).direito)
    
    def _analisarSalarioMaternidades(self):
        pass
    
    def _analisarAuxilioReclusao(self):
        pass
    
    def _analisarAuxilioDoenca(self):
        pass
        
        
class AnaliseB87:
    
    def __init__(self,pessoa):
        self._direito = Direito()
        self.direito.codigo_do_beneficio = "87"
        self._verifica_criterio_deficiencia(pessoa)
        self._verifica_criterio_renda_familiar(pessoa.grupo_familiar)
        
    @property
    def direito(self):
        return self._direito
        
    def _verifica_criterio_deficiencia(self,pessoa):
        if not pessoa.is_deficiente:
            razao = "O Benefício Assistencial à Pessoa Deficiente é exclusivo para pessoas com alguma deficiência física ou mental. Você declarou não ser deficiente."
            self.direito.registra_nao_ter_direito(razao)
            
    def _verifica_criterio_renda_familiar(self,grupo_familiar):
        global salario_minimo
        if grupo_familiar.renda_per_capita >= (salario_minimo/4):
            razao = "Para ter acesso a algum Benefício Assistencial é necessário que a renda per capita ( renda por pessoa ) seja inferior a 1/4 de salário-mínimo. O valor limite atual é de R$ {}, .A renda per capita do seu grupo familiar informado ficou em R$ {}".format(real_money_mask(salario_minimo/4),grupo_familiar.renda_per_capita_money_mask)
            self.direito.registra_nao_ter_direito(razao)
            
class AnaliseB88:
    
    def __init__(self,pessoa):
        self._direito = Direito()
        self.direito.codigo_do_beneficio = "88"
        self._verifica_criterio_deficiencia(pessoa)
        self._verifica_criterio_renda_familiar(pessoa.grupo_familiar)
        
    @property
    def direito(self):
        return self._direito
        
    def _verifica_criterio_deficiencia(self,pessoa):
        if pessoa.idade<65:
            razao = "O Benefício Assistencial à Pessoa Idosa é exclusivo para pessoas com idade igual ou superior a 65 (sessenta e cinco) anos. Atualmente você conta somente com {} anos de vida.".format(pessoa.idade)
            self.direito.registra_nao_ter_direito(razao)
            
    def _verifica_criterio_renda_familiar(self,grupo_familiar):
        global salario_minimo
        if grupo_familiar.renda_per_capita >= (salario_minimo/4):
            razao = "Para ter acesso a algum Benefício Assistencial é necessário que a renda per capita ( renda por pessoa ) seja inferior a 1/4 de salário-mínimo. O valor limite atual é de R$ {}, .A renda per capita do seu grupo familiar informado ficou em R$ {}".format(real_money_mask(salario_minimo/4),grupo_familiar.renda_per_capita_money_mask)
            self.direito.registra_nao_ter_direito(razao)
        
class AnaliseB41:
    
    def __init__(self,pessoa,gerente):
        self._direito = Direito()
        self.direito.codigo_do_beneficio = "41"
        self._verifica_criterio_idade(pessoa)
        self._verifica_criterio_carencia(gerente.get_carencia_total())
        
    @property
    def direito(self):
        return self._direito
        
    def _verifica_criterio_idade(self,pessoa):
        if pessoa.sexo == 'M' and pessoa.idade <65:
            razao = "Para os Homens, a idade mínima exigida para Aposentadoria por Idade é de 65 (sessenta e cinco) anos. Sua idade é de apenas {} anos completos".format(pessoa.idade)
            self.direito.registra_nao_ter_direito(razao)
            
            
        elif pessoa.sexo == 'F' and pessoa.idade <60:
            razao = "Para as Mulheres, a idade mínima para Aposentadoria por Idade é de 60 (sessenta) anos. Sua idade é de apenas {} anos completos".format(pessoa.idade)
            self.direito.registra_nao_ter_direito(razao)
            
    def _verifica_criterio_carencia(self,carencia_total):
        if int(carencia_total) < 180:
            razao = "Você só tem {} contribuições. A carência minima exigida para Aposentadoria por Idade é de 180 (cento e oitenta) contribuições.".format(carencia_total)
            self.direito.registra_nao_ter_direito(razao)
            
class AnaliseB4150:
    
    def __init__(self,pessoa,gerente):
        self._direito = Direito()
        self.direito.codigo_do_beneficio = "4150"
        self._verifica_criterio_idade(pessoa)
        self._verifica_criterio_carencia(gerente.get_carencia_total())
        
    @property
    def direito(self):
        return self._direito
        
    def _verifica_criterio_idade(self,pessoa):
        if pessoa.sexo == 'M' and pessoa.idade <60:
            razao = "Para os Homens, a idade mínima exigida para Aposentadoria por Idade Rural é de 60 (sessenta e cinco) anos. Sua idade é de apenas {} anos completos".format(pessoa.idade)
            self.direito.registra_nao_ter_direito(razao)
            
            
        elif pessoa.sexo == 'F' and pessoa.idade <55:
            razao = "Para as Mulheres, a idade mínima para Aposentadoria por Idade Rural é de 55 (sessenta) anos. Sua idade é de apenas {} anos completos".format(pessoa.idade)
            self.direito.registra_nao_ter_direito(razao)
            
    def _verifica_criterio_carencia(self,carencia_total):
        if int(carencia_total) < 180:
            razao = "Você só tem {} contribuições. A carência minima exigida para Aposentadoria por Idade Rural é de 180 (cento e oitenta) meses.".format(carencia_total)
            self.direito.registra_nao_ter_direito(razao)
            

class AnaliseB42:
    
    def __init__(self,pessoa,gerente):
        self._direito = Direito()
        self.direito.codigo_do_beneficio = "42"
        self._verifica_criterio_tempo_de_contribuicao(pessoa,gerente.get_contagem_total())
        
    @property
    def direito(self):
        return self._direito
        
    def _verifica_criterio_tempo_de_contribuicao(self,pessoa,contagem_total):
        if pessoa.sexo == 'M' and int(contagem_total.get_anos())<35:
            razao = "Para os Homens, o tempo mínimo de contribuição para Aposentadoria por Tempo de Contribuição é de 35 (trinta e cinco) anos. Você conta até o momento com {} de contribuição.".format(contagem_total.to_string())
            self.direito.registra_nao_ter_direito(razao)
            
        elif pessoa.sexo == 'F' and int(contagem_total.get_anos())<30:
            razao = "Para as Mulheres, o tempo mínimo de contribuição para Aposentadoria por Tempo de Contribuição é de 30 (trinta) anos. Você conta até o momento com {} de contribuição.".format(contagem_total.to_string())
            self.direito.registra_nao_ter_direito(razao)
            
class AnaliseB80:
    
    def __init__(self,pessoa,gerente,data_do_parto):
        self._direito = Direito()
        self.direito.codigo_do_beneficio = "80"
        self._verifica_criterio_ser_mulher(pessoa)
        self._verifica_criterio_qualidade_de_segurado(gerente,data_do_parto)
        self._verifica_criterio_carência(gerente,data_do_parto)
        
    @property
    def direito(self):
        return self._direito
        
    def _verifica_criterio_ser_mulher(self,pessoa):
        if pessoa.sexo == 'F':
            razao = "O salário maternidade é normalmente um benefício pago a mulheres ( mães - maternidade ). Existem situações legais em que homens podem ter direito - óbito da mãe durante o parto, adoção, etc. Futuramente disponibilizaremos um artigos explicando melhor essa situação."
            self.direito.registra_nao_ter_direito(razao)
        
    def _verifica_criterio_qualidade_de_segurado(self,gerente,data_do_parto):
        pass
    
    def _verifica_criterio_carência(self,gerente,data_do_parto):
        pass
        
            
            
            
            
            
            
            
            
        
        
        