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

@app.route('/')
def home():
    _reseta_todos_os_dados()
    return render_template("v2home.html")

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

@app.route('/contagem', methods=['POST','GET'])
def contagem():
    _reseta_gerente()
    return render_template("v2contagem.html")

def _reseta_todos_os_dados():
    _reseta_gerente()
    _reseta_pessoa()

def _reseta_gerente():
    global gerente    
    gerente = GerenteDeContagem()
    gerente_to_session()

def _reseta_pessoa():
    print("Resetou PESSOA")
    global pessoa
    pessoa = Pessoa()
    pessoa_to_session()


@app.route('/continua_contagem', methods=['POST','GET'])
def continua_contagem():
    if request.method=='POST':
        result=request.form
        vinculo = _recebe_formulario_retorna_objeto_vinculo(result)

        session_to_global_gerente()
        global gerente
        gerente.add_vinculo(vinculo)
        gerente_to_session()
        return render_template('v2continua_contagem.html',gerente=gerente)

def _recebe_formulario_retorna_objeto_vinculo(result):
    empregador = result['empregador']
    dataInicio = result['dataInicioVinculo']
    dataTermino = result['dataTerminoVinculo']
    return Vinculo(empregador,dataInicio,dataTermino)

def _recebe_formulario_retorna_objeto_vinculo_para_edicao(result):
    empregador = result['empregadorEdita']
    dataInicio = result['dataInicioVinculoEdita']
    dataTermino = result['dataTerminoVinculoEdita']
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
    return render_template('v2resultadoContagemDeTempo.html',gerente=gerente)

@app.route('/meus_direitos_resultado', methods=['POST','GET'])
def meus_direitos_resultado():
    '''
    Função que verifica se a pessoa é conhecida.
    Se sim exibe os resultados de direito aos benefícios
    Se não forem conhecidos ele direciona para receber os dados da pessoa
    '''
    session_to_global_gerente()
    session_to_global_pessoa()
    if is_dados_pessoa_conhecidos():
        return exibe_resultados()
    else:
        print("Pessoa desconhecida")
        return analise_direiros_parte_01()
    

def is_dados_pessoa_conhecidos():
    global pessoa
    return not pessoa.data_de_nascimento == None

def is_tempo_de_contribuicao_contado():
    session_to_global_gerente()
    global gerente
    return len(gerente.get_vinculos())>0

def exibe_resultados():
    session_to_global_pessoa()
    global pessoa
    session_to_global_gerente()
    global gerente
    AnaliseDeDireitos(pessoa,gerente)
    tem_algum_direito = is_tem_algum_direito(pessoa)
    return render_template('v2exibe_resultados.html',pessoa=pessoa,tem_algum_direito = tem_algum_direito)

def is_tem_algum_direito(pessoa):
    for resultado in pessoa.direitos:
        if resultado.is_tem_direito:
            return True
    return False

@app.route('/meus_direitos', methods=['POST','GET'])
def analise_direiros_parte_01():
    '''
    Tela em que o usuário informa sua data de nascimento e sexo
    '''
    return render_template("v2meus_direiros.html")

@app.route('/analise_direiros_parte_02', methods=['POST','GET'])
def analise_direiros_parte_02():
    '''
    Tela em que o usuário informa se já contribuiu com a previdência
    '''
    global pessoa
    _reseta_pessoa()
    result=request.form
    
    pessoa.data_de_nascimento = result['datadenascimento']
    atribuir_sexo_da_pessoa(result)
    pessoa_to_session()
    session_to_global_gerente()
    if is_tempo_de_contribuicao_contado():
        return meus_direitos_resultado()

    return render_template("v2analise_direiros_parte_02.html")

@app.route('/analise_direiros_parte_03', methods=['POST','GET'])
def analise_direiros_parte_03():
    '''
    Tela em que o usuário informa se é trabalhador rural
    '''
    session_to_global_pessoa()
    global pessoa
    
    result=request.form

    pessoa.is_ja_contribuiu = result['jacontribuiu'] == 'simcontribui'
    pessoa_to_session()
    if pessoa.is_ja_contribuiu:
        return render_template("v2analise_direiros_parte_03_contribuinte.html")
    else:
        return render_template("v2analise_direiros_parte_03_rural.html")

@app.route('/analise_direiros_parte_04', methods=['POST','GET'])
def analise_direiros_parte_04():
    '''
    Tela em que o usuário é direcionado ou para a contagem de tempo rural ou para o início da análise de LOAS
    '''
    session_to_global_pessoa()
    global pessoa
    
    result=request.form
    pessoa.is_rural = result['isRural'] == 'simSouRural'
    pessoa_to_session()       

    if pessoa.is_rural:
        return render_template("v2analise_direiros_parte_03_explicacao_previa_rural.html")
    else:
        return render_template("v2analise_direiros_parte_04.html")

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

@app.route('/analise_direiros_loas_verifica_deficiencia', methods=['POST','GET'])
def analise_direiros_loas_verifica_deficiencia():
    session_to_global_pessoa()
    global pessoa
    result=request.form

    pessoa.is_deficiente = result['isDeficiente'] == 'simDeficiente'
    pessoa_to_session()
    if not pessoa.is_deficiente:
        return exibe_resultados()#se a pessoa não tem idade e não é dificente já podemos analisar os resultados
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
    return exibe_resultados()

def recebe_renda_do_grupo_familiar(result,grupo_familiar):
    renda = result['renda']
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

def atribuir_sexo_da_pessoa(result):
    global pessoa
    if result['sexo'] == 'masculino':
        pessoa.sexo = 'M'
    else:
        pessoa.sexo = 'F'
    


if __name__=="__main__":
    '''app.secret_key = os.urandom(24)'''
    app.run(debug=True)

