# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, request, session
from contagem_de_tempo import GerenteDeContagem,Vinculo,Duracao
from pessoa import Pessoa
from direito import AnaliseDeDireitos

app = Flask(__name__)

gerente = None
pessoa = None
@app.route('/')
def home():
    _reseta_todos_os_dados()
    return render_template("v2home.html")

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
    session['gerente'] = gerente.toJSON()

def _reseta_pessoa():
    print("Resetou PESSOA")
    global pessoa
    pessoa = Pessoa()
    session['pessoa'] = pessoa.toJSON()


@app.route('/continua_contagem', methods=['POST','GET'])
def continua_contagem():
    if request.method=='POST':
        result=request.form
        vinculo = _recebe_formulario_retorna_objeto_vinculo(result)

        global gerente
        gerente.add_vinculo(vinculo)
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
    global gerente
    result=request.form
    id_do_vinculo = result['idAtualizaVinculo']
    vinculo = _recebe_formulario_retorna_objeto_vinculo_para_edicao(result)    
    gerente.edit_vinculo(id_do_vinculo,vinculo)
    return render_template('v2continua_contagem.html',gerente=gerente)

@app.route('/deleteVinculo/<int:id>', methods=['POST'])
def deleteVinculo(id):
    global gerente
    gerente.remove_vinculo_by_id(id)
    return render_template('v2continua_contagem.html',gerente=gerente)

@app.route('/resultado_da_contagem', methods=['POST','GET'])
def calculaTempoTotal():
    global gerente
    return render_template('v2resultadoContagemDeTempo.html',gerente=gerente)

@app.route('/meus_direitos_resultado', methods=['POST','GET'])
def meus_direitos_resultado():
    '''
    Função que verifica se a pessoa é conhecida.
    Se sim exibe os resultados de direito aos benefícios
    Se não forem conhecidos ele direciona para receber os dados da pessoa
    '''    
    global gerente
    if is_dados_pessoa_conhecidos():
        return exibe_resultados()
    else:
        print("Pessoa desconhecida")
        return analise_direiros_parte_01()
    

def is_dados_pessoa_conhecidos():
    global pessoa
    return not pessoa.idade == None

def is_tempo_de_contribuicao_contado():
    global gerente
    return len(gerente.get_vinculos())>0

def exibe_resultados():
    global pessoa
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

    if is_tempo_de_contribuicao_contado():
        return meus_direitos_resultado()

    return render_template("v2analise_direiros_parte_02.html")

@app.route('/analise_direiros_parte_03', methods=['POST','GET'])
def analise_direiros_parte_03():
    '''
    Tela em que o usuário informa se é trabalhador rural
    '''
    global pessoa
    
    result=request.form

    pessoa.is_ja_contribuiu = result['jacontribuiu'] == 'simcontribui'
    if pessoa.is_ja_contribuiu:
        return render_template("v2analise_direiros_parte_03_contribuinte.html")
    else:
        return render_template("v2analise_direiros_parte_03_rural.html")

@app.route('/analise_direiros_parte_04', methods=['POST','GET'])
def analise_direiros_parte_04():
    '''
    Tela em que o usuário é direcionado ou para a contagem de tempo rural ou para o início da análise de LOAS
    '''
    global pessoa
    
    result=request.form
    pessoa.is_rural = result['isRural'] == 'simSouRural'        

    if pessoa.is_rural:
        return render_template("v2analise_direiros_parte_03_explicacao_previa_rural.html")
    else:
        return render_template("v2analise_direiros_parte_04.html")

@app.route('/analise_direiros_loas_parte_01', methods=['POST','GET'])
def analise_direiros_loas_parte_01():
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
    global pessoa
    result=request.form

    pessoa.is_deficiente = result['isDeficiente'] == 'simDeficiente'
    if not pessoa.is_deficiente:
        return exibe_resultados()#se a pessoa não tem idade e não é dificente já podemos analisar os resultados
    return render_template("v2verifica_grupo_familiar.html")

@app.route('/analise_direiros_loas_verifica_grupo_familiar', methods=['POST','GET'])
def analise_direiros_loas_verifica_grupo_familiar():
    global pessoa
    result=request.form
    recebe_grupo_familiar(result,pessoa.grupo_familiar)
    return render_template("v2verifica_renda_do_grupo_familiar.html")

@app.route('/analise_direiros_loas_verifica_renda', methods=['POST','GET'])
def analise_direiros_loas_verifica_renda():
    global pessoa
    result=request.form
    recebe_renda_do_grupo_familiar(result,pessoa.grupo_familiar)
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
    # set the secret key.  keep this really secret:
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    "app.secret_key = os.urandom(24)
    app.run(debug=True)

