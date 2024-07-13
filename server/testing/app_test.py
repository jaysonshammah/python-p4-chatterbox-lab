import unittest
from datetime import datetime
from app import app
from models import db, Message

class TestApp(unittest.TestCase):
    '''Flask application in app.py'''

    @classmethod
    def setUpClass(cls):
        with app.app_context():
            db.create_all()

    def setUp(self):
        with app.app_context():
            # Clear and populate the database before each test
            db.session.query(Message).delete()
            db.session.commit()
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(hello_from_liza)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def test_has_correct_columns(self):
        with app.app_context():
            hello_from_liza = Message.query.filter(
                Message.body == "Hello 👋"
            ).filter(
                Message.username == "Liza"
            ).first()

            assert(hello_from_liza.body == "Hello 👋")
            assert(hello_from_liza.username == "Liza")
            assert(isinstance(hello_from_liza.created_at, datetime))

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        '''returns a list of JSON objects for all messages in the database.'''
        with app.app_context():
            response = app.test_client().get('/messages')
            records = Message.query.all()

            for message in response.json:
                assert(message['id'] in [record.id for record in records])
                assert(message['body'] in [record.body for record in records])

    def test_creates_new_message_in_the_database(self):
        '''creates a new message in the database.'''
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={
                    "body": "Hello 👋",
                    "username": "Liza",
                }
            )

            h = Message.query.filter_by(body="Hello 👋").first()
            assert(h)

    def test_returns_data_for_newly_created_message_as_json(self):
        '''returns data for the newly created message as JSON.'''
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={
                    "body": "Hello 👋",
                    "username": "Liza",
                }
            )

            assert(response.content_type == 'application/json')
            assert(response.json["body"] == "Hello 👋")
            assert(response.json["username"] == "Liza")

            h = Message.query.filter_by(body="Hello 👋").first()
            assert(h)

    def test_updates_body_of_message_in_database(self):
        '''updates the body of a message in the database.'''
        with app.app_context():
            m = Message.query.first()
            id = m.id
            body = m.body

            response = app.test_client().patch(
                f'/messages/{id}',
                json={
                    "body": "Goodbye 👋",
                }
            )

            g = Message.query.filter_by(body="Goodbye 👋").first()
            assert(g)

            g.body = body
            db.session.add(g)
            db.session.commit()

    def test_returns_data_for_updated_message_as_json(self):
        '''returns data for the updated message as JSON.'''
        with app.app_context():
            m = Message.query.first()
            id = m.id
            body = m.body

            response = app.test_client().patch(
                f'/messages/{id}',
                json={
                    "body": "Goodbye 👋",
                }
            )

            assert(response.content_type == 'application/json')
            assert(response.json["body"] == "Goodbye 👋")

            g = Message.query.filter_by(body="Goodbye 👋").first()
            g.body = body
            db.session.add(g)
            db.session.commit()

    def test_deletes_message_from_database(self):
       '''deletes the message from the database.'''
    with app.app_context():
        hello_from_liza = Message(
            body="Hello 👋",
            username="Liza"
        )

        db.session.add(hello_from_liza)
        db.session.commit()

        response = app.test_client().delete(
            f'/messages/{hello_from_liza.id}'
        )

        assert response.status_code in [200, 204]

        # Refresh the session
        db.session.expire_all()

        h = Message.query.filter_by(body="Hello 👋").first()
        assert not h

if __name__ == '__main__':
    unittest.main()
