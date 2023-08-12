from flask import (
    Flask,
    request,
    jsonify
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError


"""
    Respuestas informativas (100–199),
    Respuestas satisfactorias (200–299),
    Redirecciones (300–399),
    Errores de los clientes (400–499),
    y errores de los servidores (500–599).
"""


# Creamos Aplicación Flask.
app = Flask(__name__)

# Configuramos SQLITE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.db"

# Creamos instancia de la clase SQLAlchemy()
db = SQLAlchemy(app)


# @audit Class Contact
class Contact(db.Model):
    """
    Clase que define la estructura de la tabla "contact"
    en la base de datos, sus columnas y tipos de datos, 
    y proporciona un método para serializar los datos de la tabla. 

    Args:
        db.Model (_type_): Representa una entidad en la base de datos.

    Returns:
        Dict: Devuelve un diccionario que contiene los datos de la 
        instancia actual en un formato serializado.
        Convierte objetos de la clase "Contact" en formatos JSON.
    """
    # Colocamos nombre tabla.
    __tablename__ = "contact"

    # Colocamos columnas tabla.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(11), nullable=False)

    # Metodo para serializar los datos.
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
# @audit Route /contact create_contact
@app.route('/contact', methods=['POST'])
def create_contact():
    """
    Funcion que recibe metodo POST,
    para crear un nuevo contacto.

    Returns:
        jsonify: Retorna mensajes en caso de error 
        o en caso de success la información del
        contacto en formato JSON.
    """
    try:
        # Recuperamos la información del nuevo contacto.
        data = request.get_json()

        # Creamos variables y recuperamos datos.
        name = data['name']
        email = data['email']
        phone = data['phone']

        # Validamos que los campos no vengan nulos.
        if name and email and phone:
            # Consulta para buscar si el contacto ya existe.
            existing_contact = Contact.query.filter_by(
                name=name,
                email=email,
                phone=phone
            ).first()

            # Validamos si existe el contacto a registrar/guardar.
            if existing_contact:
                return jsonify(
                    {
                        'message': f'El contacto {existing_contact.name} ya se encuentra registrado en tus contactos.'
                    }
                )

            else:
                # Creamos objeto y mandamos la información.
                contact = Contact(name=name, email=email, phone=phone)

                # Agregamos el nuevo contacto.
                db.session.add(contact)
                # Confirmamos los cambios en la base de datos.
                db.session.commit()

        else:
            # Retornamos mensaje de error.
            return jsonify(
                {
                    'message': 'Asegurate de colocar (name, email, phone) para registrar un nuevo contacto.'
                }
            )

    except SQLAlchemyError as e:
        # Deshacemos los cambios en caso de error.
        db.session.rollback()

        # Retornamos mensaje de error.
        return jsonify(
            {
                'message': f"Error al crear/guardar el contacto {data['name']}. Mensaje: {str(e)}"
            }
        )

    else:
        # Retornamos mensaje de exito. Mostrando el nuevo contacto creado.
        return jsonify(
            {
                'message': f'Se creo/guardo con éxito el contacto {data["name"]}.',
                'contact': contact.serialize()
            }
        ), 201


# @audit Route /contact get Por usuario
@app.route('/contact/<int:id>', methods=['GET'])
def get_one_contact(id):
    """
    Function que recibe metodo GET,
    para traer un contacto ya registrado.

    Args:
        id (int): id del contacto solicitado.

    Returns:
        jsonify: Retorna mensajes en caso de error 
        o en caso de success la información del
        contacto solicitado en formato JSON.
    """
    try:
        # Traemos la información del id contacto solicitado.
        contact = Contact.query.get(id)

        # Validamos que exista el contacto.
        if not contact:
            return jsonify(
                {
                    'message': f'El usuario solictado no existe. Intenta nuevamente.'
                }
            )

    except SQLAlchemyError as e:
        # Retornamos mensaje de error.
        return jsonify(
            {
                'message': f'Error al obtener contacto con id {id}. Mensaje: {str(e)}'
            }
        ), 500

    else:
        # Retornamos toda la infromación del contacto solicitado.
        return jsonify(contact.serialize()), 200


# @audit Route /contact get_contact
@app.route('/contact', methods=['GET'])
def get_contact():
    """
    Function que recibe metodo GET,
    para mostrar todos los contactos registrados.

    Returns:
        jsonify: Retorna mensajes en caso de error 
        o en caso de success la información de todos
        los contactos registrados, en formato JSON.
    """
    try:
        # Consulta para traer todos los contactos registrados.
        contacts = Contact.query.all()

        # Validamos que exista al menos un registro a mostrar.
        if contacts is None:
            return jsonify(
                {
                    'message': 'Actualmente no hay contactos registrados.'
                }
            ), 100

    except SQLAlchemyError as e:
        # Retorna mensaje de error.
        return jsonify(
            {
                'message': f'Error al obtener los contactos registrados. Mensaje: {str(e)}'
            }
        )

    else:
        list_contacts = []

        # Recorremos los datos obtenidos.
        for contact in contacts:
            contact.serialize()
            list_contacts.append(contact.serialize())

    return jsonify(
        {
            'contacts': list_contacts
        }
    )


# @audit Route /contact edit
@app.route('/contact/<int:id>', methods=['PUT', 'PATCH'])
def edit_contact(id):
    """
    Function que recibe metodo PUT y PATCH,
    edita la información de un contacto.

    Args:
        id (int): id del contacto a editar.

    Returns:
        jsonify: Retorna mensajes en caso de error 
        o en caso de success del contacto a editar.
    """
    try:
        # Consulta para obtener infromación del contacto.
        contact = Contact.query.get(id)

        # Validamos que el usuario a editar sea existente.
        if not contact:
            return jsonify(
                {
                    'message': f'El usuario solictado a editar no existe. Intenta nuevamente.'
                }
            ), 404

        # Recuperamos datos para editar el contacto.
        data = request.get_json()

        # Validamos que los datos existan en "data".
        if 'name' in data or 'email' in data or 'phone' in data:
            contact.name = data['name']
            contact.email = data['email']
            contact.phone = data['phone']

        # Confirmamos los cambios en la base de datos.
        db.session.commit()

    except SQLAlchemyError as e:
        # Deshacer cambios en caso de error.
        db.session.rollback()

        # Retorna mensaje de error.
        return jsonify(
            {
                'message': f'Error al editar el contacto, {contact.name}. Intenta nuevamente. Mensaje: {str(e)}'
            }
        ), 500

    else:
        # Retorna mensaje de exito. Mostrando los cambios nuevos.
        return jsonify(
            {
                'message': f'Se edito correctamente el contacto, {contact.name}.'
            }
        ), 201


# @audit Route /contact delete
@app.route('/contact/<int:id>', methods=['DELETE'])
def delete_contact(id):
    """
    Function que recibe metodo DELETE,
    que elimina un contacto.

    Args:
        id (int): id del contacto a eliminar.

    Returns:
        jsonify: Retorna mensajes en caso de error 
        o en caso de success del contacto a eliminar.
    """
    try:
        # Consulta para traer el contacto.
        contact = Contact.query.get(id)

        # Validamos que exista el contacto a eliminar.
        if not contact:
            # Retorna mensaje de error.
            return jsonify(
                {
                    'message': 'Contacto no encontrado.'
                }
            ), 404

        # Eliminamos el contacto.
        db.session.delete(contact)
        # Confirmamos los cambios en la base de datos.
        db.session.commit()

    except SQLAlchemyError as e:
        # Deshacemos los cambios en caso de error.
        db.session.rollback()

        # Retorna mensaje de error.
        return jsonify(
            {
                'message': f'Error al eliminar el contacto, {contact.name}. Intenta nuevamente. Mensaje: {str(e)}'
            }
        ), 500

    else:
        # Retorna mensaje de exito.
        return jsonify(
            {
                'message': f'Contacto, {contact.name} eliminado con existo.'
            }
        ), 200
