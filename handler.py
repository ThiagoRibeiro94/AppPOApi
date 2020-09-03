# Importar o Flask
from flask import Flask,jsonify,request
import json
import pulp
import os

app = Flask(__name__)

multiplicador = 2

@app.route('/resultado/<string:dados>', methods=['POST'])
def resolver(dados):
    #Pega os dados que é uma string e retorna um dicionário
    obj = json.loads(dados)

    def Criar_Model(tipo_problema):

        if tipo_problema == 'Min':
            return pulp.LpProblem('model',pulp.LpMinimize)
        else:
            return pulp.LpProblem('model',pulp.LpMaximize)

    def Criar_Vars(lista_obj_var):

        dict_var = {}
        print(dict_var)
        for var in lista_obj_var:
            nome = var['var']
            up = var['upBound']
            low = var['lowBound']
            cat = var['tipo']

            VAR = pulp.LpVariable(name=nome,lowBound = low,upBound = up,cat = cat)
            new_var = {nome:VAR}

            dict_var.update(new_var)
        return dict_var

    def Criar_fo(fo,dicionario):

        raw_fo = fo
        raw_fo = raw_fo.split('+')
        
        fo = 0
        for termo in raw_fo:
            termo = termo.split('*')
            first = float(termo[0])
            second = dicionario[termo[1]] 

            fo = fo + first*second      
        return fo

    def Criar_Restrições(modelo,lista_restricao,dicionario):

        for restricao in lista_restricao:
            code = 0
            raw_restricao = restricao
            if '<=' in raw_restricao:
                raw_restricao = raw_restricao.split('<=')
                code = 1 
            elif '==' in raw_restricao:
                raw_restricao = raw_restricao.split('==')
                code = 2
            else:
                raw_restricao = raw_restricao.split('>=')
                code = 3

        rhs = float(raw_restricao[1])
        lado_esq = raw_restricao[0]
        lado_esq = lado_esq.split('+')

        rest = 0
        for termo in lado_esq:

            termo = termo.split('*')
            first = float(termo[0])
            second = dicionario[termo[1]]
            rest = rest + first*second
        
        restricao_montada = []
        if code==1:
            modelo += rest<=rhs
        elif code==2:
            modelo += rest == rhs
            modelo += rest >= rhs
        else:
            modelo += rest >= rhs

    def Solucao_Modelo(modelo,dicionario):
        status = modelo.solve()
        estado = pulp.LpStatus[status]
        fo_otima = pulp.value(model.objective)

        dict_var_otimas = {}
        for i in dicionario.keys():
            dict_var_otimas.update({i:pulp.value(dicionario[i])})


        resposta_dicionario = {
            'status':estado,
            'fo_otima':fo_otima,
            'vars_otimas':dict_var_otimas
        }

        return resposta_dicionario




    model = Criar_Model(obj['tipo_problema'])
    variaveis = Criar_Vars(obj['vars'])
    model += Criar_fo(obj['fo'],variaveis)
    Criar_Restrições(model,obj['restricao'],variaveis)
    sol = Solucao_Modelo(model,variaveis)

    return jsonify(sol), 200




if __name__ == '__main__':
    port = os.environ.get('PORT',5000)
    app.run(host = '0.0.0.0',port=port)