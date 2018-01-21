# -*- coding: utf-8 -*-

from pessoa import Pessoa,GrupoFamiliar
from money_mask import real_br_money_mask as real_money_mask
import datetime
import time
from factory_date_time import FactoryDateTimeFromStrings

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
        self._limpar_os_direitos_para_novo_processamento()
        
        
    def _limpar_os_direitos_para_novo_processamento(self):
        self.pessoa.direitos_limpar_todos()
        
    def analisarAposentadoriasUrbanas(self):
        self.pessoa.add_direito_analisado(AnaliseB41(self.pessoa,self.gerente).direito)
        self.pessoa.add_direito_analisado(AnaliseB42(self.pessoa,self.gerente).direito)
        
         
    def analisarAposentadoriaRural(self):
        self.pessoa.add_direito_analisado(AnaliseB4150(self.pessoa,self.gerente).direito)  
    
    
    def analisarLOAS(self):
        self.analisarB87()
        self.analisarB88()
        
    def analisarB87(self):
        self.pessoa.add_direito_analisado(AnaliseB87(self.pessoa).direito)
        
    def analisarB88(self):
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
            razao = "Você só tem {} meses trabalhados. A carência minima exigida para Aposentadoria por Idade Rural é de 180 (cento e oitenta) meses.".format(carencia_total)
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
        if pessoa.sexo == 'M':
            razao = "O salário maternidade é normalmente um benefício pago a mulheres ( mães - maternidade ). Existem situações legais em que homens podem ter direito - óbito da mãe durante o parto, adoção, etc. Futuramente disponibilizaremos artigos explicando melhor essa situação."
            self.direito.registra_nao_ter_direito(razao)
        
    def _verifica_criterio_qualidade_de_segurado(self,gerente,data_do_parto):
        
        data_do_parto = FactoryDateTimeFromStrings().get_date_time(data_do_parto)
        data_do_parto_string = "{}/{}/{}".format(data_do_parto.day,data_do_parto.month,data_do_parto.year)
        tem_qualidade = False
        maior_qualidade = None
        
        for vinculo in gerente.get_vinculos():
            perda = PerdaDaQualidadeDeSegurado(vinculo,gerente).data_da_perda_da_qualidade_de_segurado
            if  perda > data_do_parto:
                if vinculo.get_data_inicio_date_time() < data_do_parto:
                    tem_qualidade = True
                    maior_qualidade = PerdaDaQualidadeDeSegurado(vinculo,gerente).data_da_perda_da_qualidade_de_segurado_string()
            
        if not tem_qualidade:
            for vinculo in gerente.get_vinculos():
                if vinculo.get_data_inicio_date_time() < data_do_parto:
                    maior_qualidade = PerdaDaQualidadeDeSegurado(vinculo,gerente).data_da_perda_da_qualidade_de_segurado_string()
            
        
        if not tem_qualidade:
            if maior_qualidade == None:
                razao = "Para ter direito ao Salário Maternidade é necessário que na data do parto a mãe tenha qualidade de segurada, ou seja, ainda esteja coberta pelo seguro da Previdência Social. Ao que parece você nunca contribuiu com a Previdência Social e portanto nunca teve qualidade de segurada."
            else:
                razao = "Para ter direito ao Salário Maternidade é necessário que na data do parto a mãe tenha qualidade de segurada, ou seja, ainda esteja coberta pelo seguro da Previdência Social. Ao que parece você não tinha qualidade de segurado na data do parto. Com base nos dados informados, calculamos que a perda da qualidade de segurada ocorreu em {}, ao passo que o parto ocorreu em {}".format(maior_qualidade,data_do_parto_string)
            self.direito.registra_nao_ter_direito(razao)
    
    def _verifica_criterio_carência(self,gerente,data_do_parto):
        pass
        
class PerdaDaQualidadeDeSegurado:
    
    '''
    Falta fazer a análise do critério de mais de 120 contribuições sem perda da qualidade de segurado
    '''
    
    def __init__(self,vinculo,gerente):
        self.vinculo = vinculo
        self.gerente = gerente
        self._data_da_perda = vinculo.get_data_fim_date_time()
        self._data_da_perda = self.calcula_data_da_perda_simples()
        
    @property
    def data_da_perda_da_qualidade_de_segurado(self):
        return self._data_da_perda
        
    def data_da_perda_da_qualidade_de_segurado_string(self):
        return "{}/{}/{}".format( self._data_da_perda.day, self._data_da_perda.month, self._data_da_perda.year)
        
    def calcula_data_da_perda_simples(self):
         
        ano = self._data_da_perda.year
        mes = self._data_da_perda.month
         
        if self.vinculo.is_facultativo:
            mes+=8
        else:
            mes+=14
            
        if self.vinculo.is_fez_registro_no_mte:
            mes+=12
            
        while mes > 12:
            ano+=1
            mes-=12
             
        return datetime.datetime(ano,mes,16,0,0,0,0)
        
    def get_qtd_de_contribuicoes_sem_perda_da_qualidade_de_segurado(self):
        total_sem_perda =0
       
        count = 0
        a = 0
        lista = self.gerente.get_vinculos()
        total_sem_perda+=lista[0].get_carencia_considerada()
        while count<(len(lista)-1):#percorrendo a lista ordenada
            primeiro = lista[a]
            segundo = lista[count+1]
            if __is_segundo_vinculo_comeca_antes_da_perda_de_qualidade_do_primeiro(self.gerente,primeiro,segundo):
                total_sem_perda+=segundo.get_carencia_considerada()
                count+=1
            else:
                count+=1
                a=count
                total_sem_perda=lista[a].get_carencia_considerada()
        return total_sem_perda
            
def __is_segundo_vinculo_comeca_antes_da_perda_de_qualidade_do_primeiro(gerente,primeiro,segundo):
    return PerdaDaQualidadeDeSegurado(primeiro,gerente).calcula_data_da_perda_simples() >= segundo.get_data_inicio_date_time()
         
    
         
         
            
            
            
        
        
        