# app.py
from flask import Flask, redirect, render_template, request, url_for
from config import Config
from models import db, Formulario, Pergunta, Alternativa, Resposta

app = Flask(__name__)
app.config.from_object(Config)

# Inicializa o banco de dados com o app Flask
db.init_app(app)

# Cria as tabelas no banco de dados e testa a conexão
with app.app_context():
    db.create_all()  # Cria as tabelas
    try:
        db.engine.execute('SELECT 1')  # Testa a conexão
        print("Conexão bem-sucedida!")
    except Exception as e:
        print(f"Erro de conexão: {e}")

@app.route('/')
def index():
    formularios = Formulario.query.all()
    return render_template('index.html', formularios=formularios)

# Adicione o resto do seu código de rotas aqui...


@app.route('/create', methods=['GET', 'POST'])
def create_form():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        novo_formulario = Formulario(titulo=titulo, descricao=descricao)
        db.session.add(novo_formulario)
        db.session.commit()

        # Adicionar perguntas e alternativas (caso seja de múltipla escolha)
        for i in range(1, 100):  # Ajuste conforme necessário
            if request.form.get(f'pergunta_texto_{i}'):
                pergunta_texto = request.form[f'pergunta_texto_{i}']
                pergunta_tipo = request.form[f'pergunta_tipo_{i}']
                nova_pergunta = Pergunta(texto=pergunta_texto, tipo=pergunta_tipo, formulario_id=novo_formulario.id)
                db.session.add(nova_pergunta)
                db.session.commit()  # Precisamos do ID da nova pergunta para adicionar alternativas
                
                # Adicionar alternativas se a pergunta for de múltipla escolha
                if pergunta_tipo == 'multipla_escolha':
                    for j in range(1, 5):  # Supondo até 4 alternativas por pergunta
                        alternativa_texto = request.form.get(f'alternativa_texto_{i}_{j}')
                        if alternativa_texto:
                            nova_alternativa = Alternativa(texto=alternativa_texto, pergunta_id=nova_pergunta.id)
                            db.session.add(nova_alternativa)

        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_form.html')



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_form(id):
    formulario = Formulario.query.get_or_404(id)

    if request.method == 'POST':
        # Atualiza título e descrição do formulário
        formulario.titulo = request.form['titulo']
        formulario.descricao = request.form['descricao']

        # Atualiza perguntas e alternativas
        perguntas_existentes = {p.id: p for p in Pergunta.query.filter_by(formulario_id=formulario.id).all()}

        for key in request.form:
            if key.startswith('pergunta_texto_'):
                pergunta_id = key.split('_')[-1]
                pergunta = perguntas_existentes.get(int(pergunta_id))

                if pergunta:
                    # Atualiza texto e tipo da pergunta
                    pergunta.texto = request.form[key]
                    pergunta.tipo = request.form.get(f'pergunta_tipo_{pergunta_id}')

                    # Remove as alternativas antigas se a pergunta for do tipo múltipla escolha
                    if pergunta.tipo in ['multipla_escolha', 'caixa_selecao']:
                        Alternativa.query.filter_by(pergunta_id=pergunta.id).delete()
                        alternativa_index = 1
                        while True:
                            alternativa_texto = request.form.get(f'alternativa_{pergunta_id}_{alternativa_index}')
                            if not alternativa_texto:
                                break
                            nova_alternativa = Alternativa(texto=alternativa_texto, pergunta_id=pergunta.id)
                            db.session.add(nova_alternativa)
                            alternativa_index += 1

                else:
                    # Se a pergunta não existe, cria uma nova
                    nova_pergunta = Pergunta(
                        texto=request.form[key],
                        tipo=request.form.get(f'pergunta_tipo_{pergunta_id}'),
                        formulario_id=formulario.id
                    )
                    db.session.add(nova_pergunta)

        # Remover perguntas que não estão mais no formulário
        for pergunta_id in perguntas_existentes.keys():
            if f'pergunta_texto_{pergunta_id}' not in request.form:
                db.session.delete(perguntas_existentes[pergunta_id])

        db.session.commit()  # Salva as mudanças no banco de dados
        return redirect(url_for('index'))

    perguntas = Pergunta.query.filter_by(formulario_id=id).all()
    return render_template('edit_form.html', formulario=formulario, perguntas=perguntas)




@app.route('/responder_formulario/<int:id>', methods=['GET', 'POST'])
def responder_formulario(id):
    formulario = Formulario.query.get_or_404(id)
    perguntas = Pergunta.query.filter_by(formulario_id=formulario.id).all()

    if request.method == 'POST':
        for pergunta in perguntas:
            # Salvar respostas de múltipla escolha
            if pergunta.tipo == 'multipla_escolha':
                alternativa_selecionada = request.form.get(f'pergunta_{pergunta.id}')
                if alternativa_selecionada:
                    nova_resposta = Resposta(pergunta_id=pergunta.id, texto=alternativa_selecionada)
                    db.session.add(nova_resposta)

            # Salvar respostas de texto (resposta curta ou longa)
            elif pergunta.tipo in ['resposta_curta', 'resposta_longa']:
                resposta_texto = request.form.get(f'pergunta_{pergunta.id}')
                if resposta_texto:
                    nova_resposta = Resposta(pergunta_id=pergunta.id, texto=resposta_texto)
                    db.session.add(nova_resposta)

        db.session.commit()  # Salva as respostas no banco de dados
        return redirect(url_for('index'))

    return render_template('responder_form.html', formulario=formulario, perguntas=perguntas)



@app.route('/remover_pergunta/<int:id>', methods=['POST'])
def remover_pergunta(id):
    pergunta = Pergunta.query.get_or_404(id)
    
    # Remover respostas associadas antes de remover a pergunta
    respostas = Resposta.query.filter_by(pergunta_id=id).all()
    for resposta in respostas:
        db.session.delete(resposta)

    db.session.delete(pergunta)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/remover_formulario/<int:id>', methods=['POST'])
def remover_formulario(id):
    formulario = Formulario.query.get_or_404(id)

    # Atualiza ou remove as perguntas associadas
    perguntas = Pergunta.query.filter_by(formulario_id=id).all()
    for pergunta in perguntas:
        db.session.delete(pergunta)  # Remove as perguntas

    db.session.delete(formulario)
    db.session.commit()
    return redirect(url_for('index'))

