import psycopg2
from questao import Questao

def create_table():
    conn = psycopg2.connect("dbname='inssparatodos' user='postgres' password='livresql' host='localhost' port='5432'")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS questoes (id SERIAL PRIMARY KEY, data_do_cadastramento TEXT, quem_perguntou TEXT, pergunta TEXT, is_respondida BOOLEAN, resposta TEXT)")
    conn.commit()
    conn.close()

def insert(questao):
    conn = psycopg2.connect("dbname='inssparatodos' user='postgres' password='livresql' host='localhost' port='5432'")
    cur = conn.cursor()
    sql_string = "INSERT INTO questoes (data_do_cadastramento,quem_perguntou,pergunta,is_respondida,resposta) VALUES (%s,%s,%s,%s,%s) RETURNING id;"
    cur.execute(sql_string, (questao.data_do_cadastramento_string(),questao.quem_perguntou,questao.pergunta,questao.is_respondida,questao.resposta))
    id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return id

def view():
    conn = psycopg2.connect("dbname='inssparatodos' user='postgres' password='livresql' host='localhost' port='5432'")
    cur = conn.cursor()
    cur.execute("SELECT * FROM questoes")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_by_id(id):
    conn = psycopg2.connect("dbname='inssparatodos' user='postgres' password='livresql' host='localhost' port='5432'")
    cur = conn.cursor()
    cur.execute("SELECT * FROM questoes WHERE id={}".format(id))
    rows = cur.fetchall()
    conn.close()
    return rows


def update(questao):
    conn = psycopg2.connect("dbname='inssparatodos' user='postgres' password='livresql' host='localhost' port='5432'")
    cur = conn.cursor()
    sql_string = "UPDATE questoes SET data_do_cadastramento = %s, quem_perguntou = %s,pergunta = %s,is_respondida = %s, resposta = %s WHERE id=%s"
    cur.execute(sql_string, (questao.data_do_cadastramento_string(), questao.quem_perguntou, questao.pergunta, questao.is_respondida, questao.resposta, questao.id))
    conn.commit()
    conn.close()


def delete(questao):
    conn = psycopg2.connect("dbname='inssparatodos' user='postgres' password='livresql' host='localhost' port='5432'")
    cur = conn.cursor()
    cur.execute("DELETE FROM questoes WHERE id={}".format(questao.id))
    conn.commit()
    conn.close()
