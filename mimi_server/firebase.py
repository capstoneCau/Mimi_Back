import time
from datetime import timedelta
from uuid import uuid4

from firebase_admin import firestore, initialize_app, credentials, auth
from secret import GOOGLE_APPLICATION_CREDENTIALS

__all__ = ['makeChattingRoom']
initialize_app(credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS))


def makeChattingRoom(roomId, users):
    db = firestore.client()
    db.collection(u'CHATINGS').add({
        u'roomId': roomId,
        u'latestMessage': {
            u'text': u'Matching was successful.',
            u'createdAt': int(time.time() * 1000),
        },
        u'users': users
    })[1].collection(u'MESSAGES').add({
        u'text': u'Matching was successful.',
        u'createdAt': int(time.time() * 1000),
        u'system': True,
    })


def registerUser(kakao_auth_id, email):
    user = auth.create_user(
        email=email,
        email_verified=True,
        password=kakao_auth_id)
