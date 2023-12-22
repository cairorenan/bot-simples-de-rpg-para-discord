import discord
from discord.ext import commands
import sqlite3
import random

# Configuração do Discord Bot com intents ativados
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Criação das tabelas se não existirem
cursor.execute('''CREATE TABLE IF NOT EXISTS skills(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT,
    Descricao TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS pessoas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT,
    Nskill INTEGER,
    Força INTEGER,
    Resistencia INTEGER,
    Agilidade INTEGER,
    Inteligência INTEGER,
    Mana INTEGER,
    Carisma INTEGER,
    Força_de_vontade INTEGER,
    Skills TEXT
)''')

# Adição da coluna 'Skills' à tabela 'pessoas' se não estiver presente
cursor.execute("PRAGMA table_info(pessoas)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]
if 'Skills' not in column_names:
    cursor.execute("ALTER TABLE pessoas ADD COLUMN Skills TEXT")

# Adição da coluna 'Descricao' à tabela 'skills' se não estiver presente
cursor.execute("PRAGMA table_info(skills)")
columns_skills = cursor.fetchall()
column_names_skills = [column[1] for column in columns_skills]
if 'Descricao' not in column_names_skills:
    cursor.execute("ALTER TABLE skills ADD COLUMN Descricao TEXT")

# Commit das alterações no banco de dados
conn.commit()

# Comando para adicionar uma habilidade ao banco de dados e associá-la a um usuário
@bot.command(name='addskill')
async def add_skill(ctx, Nome: str, Descricao: str):
    # Inserir habilidade na tabela 'skills'
    cursor.execute('INSERT OR IGNORE INTO skills (Nome, Descricao) VALUES (?, ?)', (Nome, Descricao))
    conn.commit()

    # Atualizar habilidades do usuário na tabela 'pessoas'
    cursor.execute('SELECT Skills FROM pessoas WHERE Nome = ?', (Nome,))
    existing_skills = cursor.fetchone()
    if existing_skills:
        existing_skills = existing_skills[0].split(', ')
        existing_skills.append(Descricao)
        updated_skills = ', '.join(existing_skills)

        cursor.execute('UPDATE pessoas SET Skills=? WHERE Nome=?', (updated_skills, Nome))
        conn.commit()
        await ctx.send(f'Skill {Descricao} foi adicionada ao banco de dados e associada a {Nome}')
    else:
        await ctx.send(f'Usuário {Nome} não encontrado no banco de dados')

# Comando para adicionar uma pessoa ao banco de dados com atributos e habilidades
@bot.command(name='addpessoa')
async def add_pessoa(ctx, Nome: str, Nskill: int, Força: int, Resistencia: int, Agilidade: int, Inteligência: int, Mana: int, Carisma: int, Força_de_vontade: int, *skills: str):
    skills_str = ', '.join(skills)
    cursor.execute('INSERT INTO pessoas (Nome, Nskill, Força, Resistencia, Agilidade, Inteligência, Mana, Carisma, Força_de_vontade, Skills) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (Nome, Nskill, Força, Resistencia, Agilidade, Inteligência, Mana, Carisma, Força_de_vontade, skills_str))
    conn.commit()
    await ctx.send(f'{Nome} adicionado ao banco de dados com as skills: {", ".join(skills)} e os atributos:\nNskill: {Nskill}, Força: {Força}, Resistência: {Resistencia}, Agilidade: {Agilidade}, Inteligência: {Inteligência}, Mana: {Mana}, Carisma: {Carisma}, Força_de_vontade: {Força_de_vontade}')

# Comando para apagar uma pessoa do banco de dados
@bot.command(name='apagarpessoa')
async def apagar_pessoa(ctx, Nome: str):
    # Remover a pessoa da tabela 'pessoas'
    cursor.execute('DELETE FROM pessoas WHERE Nome = ?', (Nome,))
    conn.commit()
    await ctx.send(f'{Nome} foi deletado do banco de dados')

# Comando para editar atributos de uma pessoa no banco de dados
@bot.command(name='editarpessoa')
async def editar_pessoa(ctx, Nome: str, Nskill: int, Força: int, Resistencia: int, Agilidade: int, Inteligência: int, Mana: int, Carisma: int, Força_de_vontade: int):
    cursor.execute('UPDATE pessoas SET Nskill=?, Força=?, Resistencia=?, Agilidade=?, Inteligência=?, Mana=?, Carisma=?, Força_de_vontade=? WHERE Nome =?', (Nskill, Força, Resistencia, Agilidade, Inteligência, Mana, Carisma, Força_de_vontade, Nome))
    conn.commit()
    await ctx.send(f'Dados de {Nome} foram editados')

# Comando para editar a descrição de uma habilidade no banco de dados
@bot.command(name='editarskill')
async def editar_skill(ctx, Nome: str, NovaDescricao: str):
    cursor.execute('UPDATE skills SET Descricao=? WHERE Nome=?', (NovaDescricao, Nome))
    conn.commit()
    await ctx.send(f'Descrição da skill {Nome} atualizada no banco de dados.')

# Comando para apagar uma habilidade do banco de dados
@bot.command(name='apagarskill')
async def apagar_skill(ctx, Nome: str):
    # Remover a habilidade da tabela 'skills'
    cursor.execute('DELETE FROM skills WHERE Nome = ?', (Nome,))
    conn.commit()

    # Remover a habilidade das skills associadas às pessoas na tabela 'pessoas'
    cursor.execute('UPDATE pessoas SET Skills = REPLACE(Skills, ?, "") WHERE Skills LIKE ?', (Nome, f"%{Nome}%"))
    conn.commit()

    await ctx.send(f'Skill {Nome} foi removida do banco de dados e desassociada das pessoas.')

# Comando para adicionar pontos a um atributo de uma pessoa
@bot.command(name='addstatus')
async def add_status(ctx, Nome: str, Status: str, Pontos: int):
    cursor.execute('SELECT * FROM pessoas WHERE Nome = ?', (Nome,))
    jogador = cursor.fetchone()
    if jogador:
        # Obter o índice do atributo no banco de dados
        index_status = column_names.index(Status)
        if index_status >= 2:
            valor_atual = jogador[index_status]
            novo_valor = valor_atual + Pontos
            cursor.execute(f'UPDATE pessoas SET {Status}=? WHERE Nome=?', (novo_valor, Nome))
            conn.commit()
            await ctx.send(f'Pontos adicionados ao status {Status} de {Nome}. Novo valor: {novo_valor}')
        else:
            await ctx.send(f'O status {Status} não foi encontrado no banco de dados.')
    else:
        await ctx.send(f'O jogador {Nome} não foi encontrado no banco de dados.')

# Comando para listar todas as pessoas no banco de dados
@bot.command(name='listpessoas')
async def listar_pessoas(ctx):
    cursor.execute('SELECT Nome, Nskill, Força, Resistencia, Agilidade, Inteligência, Mana, Carisma, Força_de_vontade, Skills FROM pessoas')
    pessoas = cursor.fetchall()
    if pessoas:
        for pessoa in pessoas:
            nome, nskill, forca, resistencia, agilidade, inteligencia, mana, carisma, forca_de_vontade, skills_str = pessoa
            skills = skills_str.split(', ')
            await ctx.send(f'Nome: {nome}, Nskill: {nskill}, Força: {forca}, Resistencia: {resistencia}, Agilidade: {agilidade}, Inteligência: {inteligencia}, Mana: {mana}, Carisma: {carisma}, Força_de_vontade: {forca_de_vontade}, Skills: {", ".join(skills)}')
    else:
        await ctx.send('Banco de dados de pessoas vazio.')

# Comando para rolar um dado
@bot.command(name='d')
async def dado(ctx, número: int):
    result = random.randint(1, número)
    await ctx.send(result)

@bot.event
async def on_ready():
    print(f'Bot está online como {bot.user.name}')

# Execução do bot com o token especificado
bot.run('Token') #coloque seu token aqui

conn.close()
