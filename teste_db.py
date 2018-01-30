from questao import Questao
import db_pergunta

#print("Funcionando")

'''
q = Questao("1Michel","Hoje vai chover?")
q.responder("Acho que não.")

db_pergunta.create_table()
#db_pergunta.insert(q)
print("id: {}".format(db_pergunta.insert(q)))

print(db_pergunta.view)
'''
#print(db_pergunta.view())

#print(db_pergunta.get_by_id(6))

'''
q = Questao("Miguel","Tem bolo?")
q.responder("Limão.")
q._id = 5 
#print(q.questao_as_string())
db_pergunta.update(q)'''
'''
q = Questao("Miguel","Tem bolo?")
q.responder("Limão.")
q._id = 6
db_pergunta.delete(q)
'''

q = Questao("1Michel","Hoje vai chover?")
q.responder("Acho que não.")

db_pergunta.create_table()
#db_pergunta.insert(q)
print("id: {}".format(db_pergunta.insert(q)))