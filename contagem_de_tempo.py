# -*- coding: utf-8 -*-

import datetime

from dateutil.relativedelta import relativedelta
from factory_date_time import FactoryDateTimeFromStrings

import json


class GerenteDeContagem:
    '''
    Classe responsável por gerenciar a contagem de tempo
    '''
    def __init__(self):
        #define as variaveis
        self.reset_id()#reinicia o _id da classe vínculo
        self._duracao_total = Duracao()
        self._carencia_total = 0
        self._lista_de_vinculos = [] #lista de AssistenteDeContagem
        self._meses_a_descontar_da_carencia = 0
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        
    def reset_id(self):
        Vinculo._id = 0
        
    def get_vinculos(self):
        #retorna lista de vínculos
        return self._lista_de_vinculos
        
    def add_vinculo(self,vinculo):
        #adiciona um vinculo aos vínculos contabilizados
        self._lista_de_vinculos.append(vinculo)
        self._reorganiza_lista()
        
    def remove_vinculo(self,vinculo):
        
        del self._lista_de_vinculos[vinculo]
        self._reorganiza_lista()
        
    def remove_vinculo_by_id(self,identificador):
        indice = 0
        for vinculo in self.get_vinculos():
            if int(vinculo.get_id()) == int(identificador):
                del self._lista_de_vinculos[indice]
                self._reorganiza_lista()
            else:
                indice+=1
        
    def edit_vinculo(self,identificador,new_vinculo):
        '''
        Edita um vínculo com base em um id fornecido. O parâmetro passado é um outro objeto vínculo que será copiado 
  .     '''
        for vinculo in self.get_vinculos():
            if int(vinculo.get_id()) == int(identificador):
                vinculo.set_empregador(new_vinculo.get_empregador())
                vinculo.set_data_inicio(new_vinculo.get_data_inicio())
                vinculo.set_data_fim(new_vinculo.get_data_fim())
        self._reorganiza_lista()
                
    def get_vinculo(self,identificador):
        '''
        Retorna um vínculo com base no id fornecido
        '''
        for vinculo in self.get_vinculos():
            if int(vinculo.get_id()) == int(identificador):
                return vinculo
    
    def _ordenar_vinculos_cronologicamente(self):
        self._lista_de_vinculos = sorted(self.get_vinculos(),key=lambda vinculo: vinculo._data_inicio)
        '''
        ToDo: fazer renumeração dos vínculos com base na nova sequência criada
        '''

    def _retirar_duplicidade(self):
        count = 0
        a = 0
        while count<(len(self._lista_de_vinculos)-1):#percorrendo a lista ordenada
            
            primeiro = self._lista_de_vinculos[a]
            segundo = self._lista_de_vinculos[count+1]
            if self.__is_primeiro_termina_depois_do_comeco_do_segundo(primeiro,segundo):
                if self.__is_primeiro_termina_antes_do_fim_do_segundo(primeiro,segundo):
                    self.__primeiro_absorve_segundo(primeiro,segundo)
                self.__ignorar_para_efeito_de_contagem_e_carencia(segundo)
                count+=1
            else:
                count+=1
                a=count
                

                
    def __is_primeiro_termina_depois_do_comeco_do_segundo(self,a,b):
        return a.get_data_fim_considerada() >= b.get_data_inicio_considerada()
        
    def __is_primeiro_termina_antes_do_fim_do_segundo(self,a,b):
        return a.get_data_fim_considerada() < b.get_data_fim_considerada()
        
    def __primeiro_absorve_segundo(self,a,b):
        a.set_data_fim_considerada(b.get_data_fim_considerada())
        
    def __ignorar_para_efeito_de_contagem_e_carencia(self,vinculo):
        vinculo.set_ignorado(True)
    
    def _calcular_carencia_total(self):
        #método rescponsável por calcular a carência total
        self._carencia_total = 0
        for v in self.get_vinculos():
            self._carencia_total+=v.get_carencia_considerada()
            
        self._carencia_total -=self._meses_a_descontar_da_carencia
    
    def get_contagem_total(self):
        #método que retorna o resultado da contagem de tempo
        return self._duracao_total
        
    def get_carencia_total(self):
        #método que retorna a carência que foi computada
        return self._carencia_total
        
    def _reorganiza_lista(self):
        self._retornar_datas_consideradas_as_datas_reais()
        self._reconsiderar_todos_os_vinculos()
        self._ordenar_vinculos_cronologicamente()
        self._retirar_duplicidade()
        self._recalcular_duracao_e_carencia_considerados_em_cada_vinculo()
        self._set_meses_a_descontar_da_carencia()
        self._calcular_carencia_total()
        self._set_meses_a_descontar_da_carencia()
        
    def _retornar_datas_consideradas_as_datas_reais(self):
         for v in self.get_vinculos():
             v.retornar_datas_consideradas_as_datas_reais()
             
    def _reconsiderar_todos_os_vinculos(self):
        for v in self.get_vinculos():
            v.set_ignorado(False)
  
    def _recalcular_duracao_e_carencia_considerados_em_cada_vinculo(self):
        self._duracao_total = Duracao() #zera a duracao para recalcular
        for v in self.get_vinculos():
            v.atualiza_duracao_e_carencia_considerados()
            self.__add_duracao_ao_total(v.get_duracao_considerada())
        self.__trata_dias_e_meses_apos_somados()
            
    def __add_duracao_ao_total(self,duracao_do_vinculo):
        self._duracao_total.add_duracao(duracao_do_vinculo)
        
    def __trata_dias_e_meses_apos_somados(self):
        anos = self._duracao_total.get_anos()
        meses = self._duracao_total.get_meses()
        dias = self._duracao_total.get_dias()
        
        while dias >=30:
            dias-=30
            meses+=1
            
        while meses >=12:
            meses-=12
            anos+=1
            
        self._duracao_total = Duracao(anos,meses,dias)
        
    def _set_meses_a_descontar_da_carencia(self):
        '''
        Método responsável por verificar a quantidade de meses que devem ser considerados no cálculo da carência total
        Ele atua calculando a quantidade de vínculos em que as datas efetivamente consideradas (descontadas as duplicidades) compartilham o mesmo mes ( começam ou terminam no mesmo mês entre si)
        '''
        self._meses_a_descontar_da_carencia = 0
        count = 0
        a = 0
        while count<(len(self._lista_de_vinculos)-1):#percorrendo a lista ordenada
            primeiro = self._lista_de_vinculos[a]
            segundo = self._lista_de_vinculos[count+1]
            if not primeiro.is_ignorado():
                if not segundo.is_ignorado():
                    if self._datas_consideradas_comecam_ou_terminam_no_mesmo_mes(primeiro,segundo):
                        self._meses_a_descontar_da_carencia+=1
                count+=1
            else:
                count+=1
                a=count
    
    def _datas_consideradas_comecam_ou_terminam_no_mesmo_mes(self,v1,v2):
        return FactoryDateTimeFromStrings()._is_mesmo_mes(v1.get_data_fim_considerada(),v2.get_data_inicio_considerada())
            
        


#self._meses_a_descontar_da_carencia+=1
                
    
                
class Vinculo:
    _id = 0
    '''
    Classe que define um vinculo trabalhista
    '''
    def __init__(self,empregador,data_inicio,data_fim):
        
        self._id = Vinculo._id
        Vinculo._id +=1
        self._empregador = empregador
        self._data_inicio = data_inicio
        self._data_fim = data_fim
        self._duracao = 0
        self._data_inicio_considerada = data_inicio
        self._data_fim_considerada = data_fim
        self._duracao_considerada = Duracao(0,0,0)
        self._carencia = 0
        self._carencia_considerada = 0
        self._ignorado = False
        self._calcula_duracao()
        self._calcula_duracao_considerada()
        self._calcula_carencia()
        self._calcula_carencia_considerada()
        self._is_facultativo = False
        self._is_fez_registro_no_mte = False
        
    @property
    def is_facultativo(self):
        return self._is_facultativo
        
    @is_facultativo.setter 
    def is_facultativo(self,new_value):
        self._is_facultativo = new_value
        
    @property
    def is_fez_registro_no_mte(self):
        return self._is_fez_registro_no_mte
        
    @is_fez_registro_no_mte.setter 
    def is_fez_registro_no_mte(self,new_value):
        if not self._is_facultativo:#segurado facultativo não faz registro no MTE
            self._is_fez_registro_no_mte = new_value
    
    def get_id(self):
        return self._id
        
    def is_ignorado(self):
        return self._ignorado
    
    def get_carencia(self):
        return self._carencia
        
    def get_carencia_considerada(self):
        return self._carencia_considerada
        
    def get_empregador(self):
        return self._empregador
        
    def get_data_inicio(self):
        return self._data_inicio
        
    def get_data_inicio_date_time(self):
        return FactoryDateTimeFromStrings().get_date_time(self._data_inicio)

    def get_data_fim(self):
        return self._data_fim
        
    def get_data_fim_date_time(self):
        return FactoryDateTimeFromStrings().get_date_time(self._data_fim)

    def _formata_data_br(self,str_date):
        marcador = FactoryDateTimeFromStrings().get_marcador(str_date)
        pieces = str_date.split(marcador)
        return "{} / {} / {}".format(pieces[2],pieces[1],pieces[0])
        
    def get_data_inicio_formatada(self):
        return self._formata_data_br(self.get_data_inicio())

    def get_data_fim_formatada(self):
        return self._formata_data_br(self.get_data_fim())
        
    def get_duracao(self):
        return self._duracao
        
    def get_duracao_considerada(self):
        return self._duracao_considerada
        
    def get_data_inicio_considerada(self):
        return self._data_inicio_considerada
        
    def get_data_fim_considerada(self):
        return self._data_fim_considerada
    
    def set_id(self,new_id):
        self._id = new_id
        
    def set_ignorado(self,value):
        self._ignorado = value
        if self.is_ignorado():
            self._zerar_valores_considerados()
        
    def _zerar_valores_considerados(self):
        self._zerar_duracao_considerada()
        self._zerar_carencia_considerada()
        
    def _zerar_duracao_considerada(self):
        self._duracao_considerada = Duracao(0,0,0)
        
    def _zerar_carencia_considerada(self):
        self._carencia_considerada = 0
        
    def set_empregador(self,new_empregador):
        self._empregador = new_empregador
        
    def set_data_inicio(self,new_data_inicio):
        self._data_inicio = new_data_inicio
        self.set_data_inicio_considerada(self._data_inicio)
        self.__atualiza_valores_calculados()
        
    def set_data_fim(self,new_data_fim):
        self._data_fim = new_data_fim
        self.set_data_fim_considerada(self._data_fim)
        self.__atualiza_valores_calculados()
        
    def retornar_datas_consideradas_as_datas_reais(self):
        self.set_data_inicio_considerada(self._data_inicio)
        self.set_data_fim_considerada(self._data_fim)
        
    def set_data_inicio_considerada(self, new_data_inicio):
        self._data_inicio_considerada = new_data_inicio
        
    def set_data_fim_considerada(self, new_data_fim):
        self._data_fim_considerada = new_data_fim
        
    def __atualiza_valores_calculados(self):
        self._calcula_duracao()
        self._calcula_carencia()
        if not self.is_ignorado():
            self.atualiza_duracao_e_carencia_considerados()
        
    def atualiza_duracao_e_carencia_considerados(self):
        self._calcula_duracao_considerada()
        self._calcula_carencia_considerada()
        
    def _calcula_duracao(self):
        self._duracao = CalculaDuracao(self.get_data_inicio(),self.get_data_fim()).calcula_duracao_vinculo()
        
    def _calcula_carencia(self):
        self._carencia = CalculaCarencia().get_carencia_vinculo(self)
        
    def _calcula_duracao_considerada(self):
        if self.is_ignorado():
            self._zerar_valores_considerados()
            return
        self._duracao_considerada = CalculaDuracao(self.get_data_inicio_considerada(),self.get_data_fim_considerada()).calcula_duracao_vinculo()
    
    def _calcula_carencia_considerada(self):
        if not self.is_ignorado():
            self._carencia_considerada = CalculaCarencia().get_carencia_considerada_vinculo(self)



class CalculaDuracao:
    '''
    Classe responsável por realizar a contagem de tempo
    '''
    def __init__(self,data_inicio,data_fim):
        self._dt_fim = FactoryDateTimeFromStrings().get_date_time(data_fim)
        self._dt_inicio = FactoryDateTimeFromStrings().get_date_time(data_inicio)
        self._difference = relativedelta(self._dt_fim,self._dt_inicio)
        self.duracao = Duracao()
        
    def calcula_duracao_vinculo(self):
        self._calcula_qtd_anos()
        self._calcula_qtd_meses()
        self._calcula_qtd_dias()
        return self.duracao
        
    def _calcula_qtd_anos(self):
        #Calcula qtd de anos
        self.duracao.set_anos(self._difference.years)
    
    def _calcula_qtd_meses(self):
        #Calcula quantidade de meses
        self.duracao.set_meses(self._difference.months)
        
    def _trata_meses(self):
        meses = 0 
        if self.duracao.get_meses() ==12:
            meses = 0 
            self.duracao.set_anos(self.duracao.get_anos()+1)
            self.duracao.set_meses(meses)
    
    def _calcula_qtd_dias(self):
        #Calcula qd de dias
        dias = self._difference.days + 1 # O INSS conta um dia a mais
        self._trata_dias(dias)
        
    def _trata_dias(self,dias):
        #método que faz arredondamentos de dias para meses se 
        if(dias >= 30):
            self._trata_dias_nao_fevereiro(dias)
        else:
            self.duracao.set_dias(dias)
        if(self.__is_fevereiro(self._dt_fim.month)):
            self._trata_dias_fevereiro(dias)
        
    def _trata_dias_nao_fevereiro(self,dias):
        
        self.duracao.set_meses(self.duracao.get_meses()+1)
        self._trata_meses()
        dias=0
        self.duracao.set_dias(dias) 
        
    def _trata_dias_fevereiro(self,dias):
        if(dias >= 28):
                self.duracao.set_meses(self.duracao.get_meses()+1)
                dias=0
                self._trata_meses()
        self.duracao.set_dias(dias)
        
    def __is_fevereiro(self,mes):
        if mes == 2:
            return True
        return False


class CalculaCarencia:
    '''
    Classe responsável por calcular a carência dos vínculos ou da lista de vinculos, conforme for passado
    '''
    def __init__(self):
        pass
    
    def get_carencia_vinculo(self,vinculo):
        
        carencia = 0
        duracao = self._get_duracao_ideal(vinculo.get_data_inicio(),vinculo.get_data_fim())
        carencia = duracao.get_anos() * 12
        carencia += duracao.get_meses()
        
        if duracao.get_dias() > 0: 
            carencia+=1

        return carencia
        
    def get_carencia_considerada_vinculo(self,vinculo):
        
        carencia = 0
        duracao = self._get_duracao_ideal(vinculo.get_data_inicio_considerada(),vinculo.get_data_fim_considerada())
        carencia = duracao.get_anos() * 12
        carencia += duracao.get_meses()
        
        if duracao.get_dias() > 0: 
            carencia+=1

        return carencia

    def _get_duracao_ideal(self, data_inicio,data_fim):
        '''
        método que retorna a duracao do vinculo como se ele tivesse começado no primeiro dia do mes de inicio e terminado no ultimo dia do mes de termino.
        Sobre tal período será calculada a carência vez que 1 dia trabalhado no mês vale como um mês de carência.
        Ressalta-se que o método não altera a duração real do vínculo
        '''
        dataInicio = data_inicio
        dataFim = data_fim
        
        mesIn = FactoryDateTimeFromStrings().get_mes(dataInicio)
        mesOut = FactoryDateTimeFromStrings().get_mes(dataFim)
        
        anoIn = FactoryDateTimeFromStrings().get_ano(dataInicio)
        anoOut = FactoryDateTimeFromStrings().get_ano(dataFim)
        
        ultimo_dia_dataFim = self._get_ultimo_dia_do_mes(mesOut,anoOut)
        
        return CalculaDuracao("{}/{}/{}".format(anoIn,mesIn,1),"{}/{}/{}".format(anoOut,mesOut,ultimo_dia_dataFim)).calcula_duracao_vinculo()
    
        
    def _get_ultimo_dia_do_mes(self,mes,ano):
        if mes == 2:
            if self.__is_bissexto(ano):
                return 29
            else:
                return 28
        else:
            return 30
    
    def __is_bissexto(self,ano):
        return (ano % 4 == 0 and (ano % 400 == 0 or ano % 100 != 0))
        
    

class Duracao:
    '''
    Classe que defina uma estrutura de tempo sendo anos, meses e dias
    '''
    def __init__(self,anos=0,meses=0,dias=0):
        '''
        Inicializa variáveis
        Os parâmetros anos,meses e dias são opcionais
        '''
        self._anos = anos
        self._meses = meses
        self._dias = dias
        
    def print(self):
        print('{} anos, {} meses e {} dias'.format(self.get_anos(),self.get_meses(),self.get_dias()))
        
    def to_string(self):
        return('{} anos, {} meses e {} dias'.format(self.get_anos(),self.get_meses(),self.get_dias()))
    
    def get_anos(self):
        #retorna a quantidade de anos na forma de um int
        return self._anos
        
    def get_meses(self):
        #retorna a qtd de meses na forma de um int
        return self._meses
    
    def get_dias(self):
        #retorna a qtd de dias na forma de um int
        return self._dias
        
    def set_anos(self, new_anos):
        self._anos = new_anos
        
    def set_meses(self,new_meses):
        self._meses = new_meses
        
    def set_dias(self, new_dias):
        self._dias = new_dias
        
    def add_duracao(self,new_duracao):
        self._anos += new_duracao.get_anos()
        self._meses +=new_duracao.get_meses()
        self._dias += new_duracao.get_dias()
        
        
class QualidadeDeSegurado:
    '''
    Classe responsável por verificar os perídos de qualidade de segurado da pessoa
    '''
    def __init__(self,lista_de_vinculos,lista_de_beneficios_recebidos,data_do_evento):
        self._lista_de_vinculos = lista_de_vinculos
        self._lista_de_beneficios_recebidos = lista_de_beneficios_recebidos
        self._data_do_evento = data_do_evento
        
    def get_data_fim_qualidade_de_segurado(self):
        pass
    
    def _is_tem_qualidade_de_segurado_na_data_do_evento(self):
        pass
    
    def __is_esta_contribuindo_na_data_do_evento(self):
        pass
    
    def __get_data_da_ultima_contribuicao(self):
        pass
    
    def __get_qtd_de_periodo_de_graca(self):
        pass
    
    def __is_ultima_contribuicao_como_facultativo(self):
        pass
    
    def __is_contribuiu_por_mais_de_dez_anos_sem_intervalo(self):#consultar se é sem intervalo ou sem perda da qualidade de segurado
        pass
    
    def __is_recebeu_seguro_desemprego_ou_fez_inscricao_no_sine(self):
        pass
        
        
    
    

        
    
        
        
    
   



    
    