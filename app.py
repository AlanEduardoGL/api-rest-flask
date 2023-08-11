from flask import (
    Flask,
    request,
    jsonify
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError


# Creamos Aplicación Flask.
app = Flask(__name__)

# Configuramos SQLITE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.db"

# Creamos instancia de la clase SQLAlchemy()
db = SQLAlchemy(app)


class Contact(db.Model):
    # Colocamos nombre tabla.
    __tablename__ = "contact"

    # Colocamos columnas tabla.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(11), nullable=False)

    # Metodo para serializamos los datos.
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }


# Migramos los Modelos creados de manera automática.
with app.app_context():
    db.create_all()


# Creamos rutas.
# @audit Route /contact create
@app.route('/contact', methods=['POST'])
def create_contact():
    return 'Se creo un contacto.'


# @audit Route /contact get
@app.route('/contact', methods=['GET'])
def get_contact():
    try:
        contacts = Contact.query.all()
    except SQLAlchemyError as e:
        print(f'Error al traer los contactos registrados. Mensaje: {str(e)}')
    else:
        list_contacts = []
        
        for contact in contacts:
            contact.serialize()
            list_contacts.append(contact.serialize())
    
    return jsonify(
        {
            'contacts': list_contacts
        }
    )


# @audit Route /contact delete
@app.route('/contact', methods=['DELETE'])
def delete_contact():
    return 'Contacto eliminado correctamente.'


# @audit Route /contact edit
@app.route('/contact', methods=['PUT', 'PATCH'])
def edit_contact():
    return 'Contacto editado correctamente.'
