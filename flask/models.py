from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Formulario(db.Model):
    __tablename__ = 'formulario'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    # Relação com Perguntas
    perguntas = db.relationship('Pergunta', backref='formulario', lazy=True, cascade="all, delete-orphan")


class Pergunta(db.Model):
    __tablename__ = 'pergunta'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Tipo da pergunta (ex: multipla_escolha, resposta_curta, etc.)
    formulario_id = db.Column(db.Integer, db.ForeignKey('formulario.id'), nullable=False)

    # Relação com Alternativas
    alternativas = db.relationship('Alternativa', backref='pergunta', lazy=True, cascade="all, delete-orphan")
    
    # Relação com Respostas
    respostas = db.relationship('Resposta', backref='pergunta', lazy=True, cascade="all, delete-orphan")


class Alternativa(db.Model):
    __tablename__ = 'alternativa'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey('pergunta.id'), nullable=False)


class Resposta(db.Model):
    __tablename__ = 'resposta'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey('pergunta.id'), nullable=False)
