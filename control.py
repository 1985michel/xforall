# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, request, session
from contagem_de_tempo import GerenteDeContagem,Vinculo,Duracao
from pessoa import Pessoa
from direito import AnaliseDeDireitos
from json_to_python import JsonToPython
import json

app = Flask(__name__)

#app.secret_key = os.urandom(24)
app.secret_key = 'LmijdkfjduhEHUdHDUEHDUSH'

gerente = None
pessoa = None


def gerente_to_session():
    global gerente  
    session['gerente'] =  gerente.toJSON()

def session_to_global_gerente():
    global gerente
    gerente = JsonToPython().json_to_gerente(session['gerente'])

def pessoa_to_session():
    global pessoa  
    session['pessoa'] =  pessoa.toJSON()

def session_to_global_pessoa():
    global pessoa
    
    decoded = json.loads(session['pessoa'])
    if not decoded['_data_de_nascimento'] == None:
        pessoa = JsonToPython().json_to_pessoa(session['pessoa'])

def _reseta_todos_os_dados():
    _reseta_gerente()
    _reseta_pessoa()

def _reseta_gerente():
    global gerente    
    gerente = GerenteDeContagem()
    gerente_to_session()

def _reseta_pessoa():
    global pessoa
    pessoa = Pessoa()
    pessoa_to_session()

def atribuir_sexo_da_pessoa(result):
    global pessoa
    if result['sexo'] == 'masculino':
        pessoa.sexo = 'M'
    else:
        pessoa.sexo = 'F'

'''TRILHA ANÁLISE DE DIREITO A APOSENTADORIAS'''


@app.route('/')
def home():
    _reseta_todos_os_dados()
    return render_template("v2home.html")

@app.route('/contagem', methods=['POST','GET'])
def contagem():
    _reseta_gerente()

    session_to_global_pessoa()
    global pessoa
    
    if not pessoa == None:#prevenindo um erro de processamento comum no Heroku
        if pessoa.is_rural:
            return render_template("v2contagem_rural.html")

    return render_template("v2contagem.html")

@app.route('/continua_contagem', methods=['POST','GET'])
def continua_contagem():
    if request.method=='POST':

        session_to_global_gerente()
        global gerente
        session_to_global_pessoa()
        global pessoa
        result=request.form
        vinculo = _recebe_formulario_retorna_objeto_vinculo(result)
        
        gerente.add_vinculo(vinculo)
        gerente_to_session()

        if pessoa.is_rural:
            return render_template('v2continua_contagem_rural.html',gerente=gerente)
        return render_template('v2continua_contagem.html',gerente=gerente)

def _recebe_formulario_retorna_objeto_vinculo(result):
    empregador = result['empregador']
    dataInicio = result['dataInicioVinculo']
    dataTermino = result['dataTerminoVinculo']
    return Vinculo(empregador,dataInicio,dataTermino)

@app.route('/atualizaVinculo', methods=['POST','GET'])
def atualizaVinculo():
    session_to_global_gerente()
    global gerente
    result=request.form
    id_do_vinculo = result['idAtualizaVinculo']
    vinculo = _recebe_formulario_retorna_objeto_vinculo_para_edicao(result)    
    gerente.edit_vinculo(id_do_vinculo,vinculo)
    gerente_to_session()
    return render_template('v2continua_contagem.html',gerente=gerente)

def _recebe_formulario_retorna_objeto_vinculo_para_edicao(result):
    empregador = result['empregadorEdita']
    dataInicio = result['dataInicioVinculoEdita']
    dataTermino = result['dataTerminoVinculoEdita']
    return Vinculo(empregador,dataInicio,dataTermino)

@app.route('/deleteVinculo/<int:id>', methods=['POST'])
def deleteVinculo(id):
    session_to_global_gerente()
    global gerente
    gerente.remove_vinculo_by_id(id)
    gerente_to_session()
    return render_template('v2continua_contagem.html',gerente=gerente)

@app.route('/resultado_da_contagem', methods=['POST','GET'])
def calculaTempoTotal():
    session_to_global_gerente()
    global gerente
    if len(gerente.get_vinculos())==0:
        return pergunta_se_ja_contribuiu()
    return render_template('v2resultadoContagemDeTempo.html',gerente=gerente)

@app.route('/data_de_nascimento_e_sexo', methods=['POST','GET'])
def data_de_nascimento_e_sexo():
    #exibe a tela para o usuário informar data de nascimento e sexo
    return render_template("v2data_de_nascimento_e_sexo.html")   

@app.route('/processa_resultado_aposentadorias', methods=['POST','GET'])
def processa_resultado_aposentadorias():
    '''
    - recebe os dados da pessoa
    - processa o resultado dos direitos
    - exibe o resultado dos direitos analisados
    '''
    session_to_global_pessoa()
    global pessoa
    rural = pessoa.is_rural

    session_to_global_gerente()
    global gerente
    
    _reseta_pessoa()

    result=request.form    
    pessoa.data_de_nascimento = result['datadenascimento']
    atribuir_sexo_da_pessoa(result)
    pessoa_to_session()
    #session_to_global_gerente()
    if rural:
        pessoa.is_rural = rural
        return exibe_resultado_aposentadoria_rural()

    if pessoa.is_ja_contribuiu or len(gerente.get_vinculos())>0:
        return exibe_resultados_aposentadorias()

    if not pessoa.is_ja_contribuiu:
        #print("LINHA 167")
        if(int(pessoa.idade)>=65):
            return render_template("v2verifica_grupo_familiar.html")
        else:
            #se nao for idoso tem que ser deficiente
            return render_template("v2verifica_deficiencia.html")
        return analise_direiros_loas_verifica_deficiencia()
    

def exibe_resultados_aposentadorias(): #APOSENTADORIA
    session_to_global_pessoa()
    global pessoa
    session_to_global_gerente()
    global gerente

    AnaliseDeDireitos(pessoa,gerente).analisarAposentadoriasUrbanas()
    tem_algum_direito = is_tem_algum_direito(pessoa)
    nao_tem_algum_direito = is_nao_tem_algum_direito(pessoa)
    return render_template('v2exibe_resultados_aposentadorias.html',pessoa=pessoa,tem_algum_direito = tem_algum_direito,nao_tem_algum_direito = nao_tem_algum_direito)

def exibe_resultado_aposentadoria_rural(): #APOSENTADORIA
    session_to_global_pessoa()
    global pessoa
    session_to_global_gerente()
    global gerente

    AnaliseDeDireitos(pessoa,gerente).analisarAposentadoriaRural()
    tem_algum_direito = is_tem_algum_direito(pessoa)
    nao_tem_algum_direito = is_nao_tem_algum_direito(pessoa)
    return render_template('v2exibe_resultados_aposentadorias.html',pessoa=pessoa,tem_algum_direito = tem_algum_direito,nao_tem_algum_direito = nao_tem_algum_direito)

def exibe_resultados_loas(): #APOSENTADORIA
    session_to_global_pessoa()
    global pessoa
    session_to_global_gerente()
    global gerente

    if(int(pessoa.idade)>=65):
        AnaliseDeDireitos(pessoa,gerente).analisarB88()
    else:
        #se nao for idoso tem que ser deficiente
        AnaliseDeDireitos(pessoa,gerente).analisarB87()
    #AnaliseDeDireitos(pessoa,gerente).analisarLOAS()
    tem_algum_direito = is_tem_algum_direito(pessoa)
    nao_tem_algum_direito = is_nao_tem_algum_direito(pessoa)
    return render_template('v2exibe_resultados_aposentadorias.html',pessoa=pessoa,tem_algum_direito = tem_algum_direito,nao_tem_algum_direito = nao_tem_algum_direito)


def is_tem_algum_direito(pessoa):
    for resultado in pessoa.direitos:
        if resultado.is_tem_direito:
            return True
    return False

def is_nao_tem_algum_direito(pessoa):
    for resultado in pessoa.direitos:
        if not resultado.is_tem_direito:
            return True
    return False

@app.route('/pergunta_se_ja_contribuiu', methods=['POST','GET'])
def pergunta_se_ja_contribuiu():
    return render_template('v2pergunta_se_ja_contribuiu.html')

@app.route('/nunca_contribuiu', methods=['POST','GET'])
def nunca_contribuiu():
    session_to_global_pessoa()
    global pessoa
    session_to_global_gerente()
    global gerente
    pessoa.is_ja_contribuiu = False
    pessoa_to_session()
    return render_template("v2pergunta_se_trabalhador_rural.html")


@app.route('/recebe_se_contribuiu', methods=['POST','GET'])
def recebe_se_contribuiu():
    '''
    Recebe se o usuário já contribuiu
    '''
    session_to_global_pessoa()
    global pessoa
    session_to_global_gerente()
    global gerente

    result=request.form

    pessoa.is_ja_contribuiu = result['jacontribuiu'] == 'simcontribui'
    pessoa_to_session()
    if pessoa.is_ja_contribuiu:
        return render_template("v2contagem.html")#se ele diz que é contribuinte mas não informou vinculo, retorna ao início da contagem
    else:
        return render_template("v2pergunta_se_trabalhador_rural.html")

@app.route('/recebe_se_rural', methods=['POST','GET'])
def recebe_se_rural():
    '''
    Tela em que o usuário é direcionado ou para a contagem de tempo rural ou para o início da análise de LOAS
    '''
    session_to_global_pessoa()
    global pessoa
    
    result=request.form
    pessoa.is_rural = result['isRural'] == 'simSouRural'
    pessoa_to_session()       

    if pessoa.is_rural:
        return render_template("v2orientacoes_para_inicio_contagem_rural.html")        
    else:
        return render_template("v2orientacoes_para_inicio_analise_loas.html")

'''
@app.route('/analise_direiros_loas_parte_01', methods=['POST','GET'])
def analise_direiros_loas_parte_01():
    session_to_global_pessoa()
    global pessoa
    #se for idoso, nao precisa saber se é dificente
    #entao verifique a renda
    if(int(pessoa.idade)>=65):
        return render_template("v2verifica_grupo_familiar.html")
    else:
    #se nao for idoso tem que ser deficiente
        return render_template("v2verifica_deficiencia.html")
'''

@app.route('/analise_direiros_loas_verifica_deficiencia', methods=['POST','GET'])
def analise_direiros_loas_verifica_deficiencia():
    session_to_global_pessoa()
    global pessoa
    result=request.form

    pessoa.is_deficiente = result['isDeficiente'] == 'simDeficiente'
    pessoa_to_session()
    if not pessoa.is_deficiente:
        return exibe_resultados_loas()#se a pessoa não tem idade e não é dificente já podemos analisar os resultados
    return render_template("v2verifica_grupo_familiar.html")

@app.route('/analise_direiros_loas_verifica_grupo_familiar', methods=['POST','GET'])
def analise_direiros_loas_verifica_grupo_familiar():
    session_to_global_pessoa()
    global pessoa
    result=request.form
    recebe_grupo_familiar(result,pessoa.grupo_familiar)
    pessoa_to_session()
    return render_template("v2verifica_renda_do_grupo_familiar.html")

@app.route('/analise_direiros_loas_verifica_renda', methods=['POST','GET'])
def analise_direiros_loas_verifica_renda():
    session_to_global_pessoa()
    global pessoa
    result=request.form
    recebe_renda_do_grupo_familiar(result,pessoa.grupo_familiar)
    pessoa_to_session()
    return exibe_resultados_loas()

def recebe_renda_do_grupo_familiar(result,grupo_familiar):
    renda = result['renda']
    global pessoa
    pessoa.grupo_familiar.renda_total = 0 #zerando renda do grupo
    if not renda == '0,00':
        renda = trata_formatacao_renda_informada(renda)
    else:
        renda = 0
    grupo_familiar.add_renda(float(renda))


def trata_formatacao_renda_informada(renda):
    renda = renda.replace('.','')
    renda = renda.replace(',','.')
    return renda
    

def recebe_grupo_familiar(result,grupo_familiar):
    grupo = ['mae','pai','irmaos','filhos','conjuge']

    #setando os valores do grupo FAMILIAR
    for checkbox in grupo:
        value = result.get(checkbox)
        if value:
            if checkbox == 'irmaos':
                qtd = result['qtdirmaos']
                count = 0
                while count < int(qtd):
                    grupo_familiar.add_pessoa()
                    count+=1
            elif checkbox == 'filhos':
                qtd = result['qtdfilhos']
                count = 0
                while count < int(qtd):
                    grupo_familiar.add_pessoa()
                    count+=1
            else:
                grupo_familiar.add_pessoa()
    if result['solteirooucasado'] == 'soucasado':
        grupo_familiar.add_pessoa()
    


if __name__=="__main__":
    '''app.secret_key = os.urandom(24)'''
    app.run(debug=True)