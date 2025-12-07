from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    
    experience_years = db.Column(db.Integer, default=0)
    lesson_duration = db.Column(db.Integer, default=30)
    preferred_time = db.Column(db.String, nullable=True)
    calendar_connected = db.Column(db.Boolean, default=False)
    onboarding_complete = db.Column(db.Boolean, default=False)
    difficulty_level = db.Column(db.Integer, default=1)  # 1=Beginner, 2=Intermediate, 3=Advanced
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    scheduled_lessons = db.relationship('ScheduledLesson', backref='user', lazy=True)
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True)


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)


class LessonCategory(db.Model):
    __tablename__ = 'lesson_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    
    vocabulary = db.relationship('Vocabulary', backref='category', lazy=True)
    verbs = db.relationship('Verb', backref='category', lazy=True)


class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'
    id = db.Column(db.Integer, primary_key=True)
    spanish_word = db.Column(db.String(100), nullable=False)
    english_word = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(100))
    example_sentence = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('lesson_categories.id'), nullable=False)


class Verb(db.Model):
    __tablename__ = 'verbs'
    id = db.Column(db.Integer, primary_key=True)
    infinitive = db.Column(db.String(100), nullable=False)
    english_meaning = db.Column(db.String(100), nullable=False)
    yo = db.Column(db.String(100))
    tu = db.Column(db.String(100))
    el_ella = db.Column(db.String(100))
    nosotros = db.Column(db.String(100))
    vosotros = db.Column(db.String(100))
    ellos = db.Column(db.String(100))
    example_sentence = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('lesson_categories.id'), nullable=False)


class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('lesson_categories.id'), nullable=False)
    vocabulary_completed = db.Column(db.Boolean, default=False)
    verbs_completed = db.Column(db.Boolean, default=False)
    conversation_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    category = db.relationship('LessonCategory')


class ScheduledLesson(db.Model):
    __tablename__ = 'scheduled_lessons'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('lesson_categories.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    calendar_event_id = db.Column(db.String)
    completed = db.Column(db.Boolean, default=False)
    
    category = db.relationship('LessonCategory')


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('lesson_categories.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.now)
    ended_at = db.Column(db.DateTime)
    difficulty_level = db.Column(db.Integer, default=1)
    performance_score = db.Column(db.Float, default=0.0)
    corrections_count = db.Column(db.Integer, default=0)
    successful_responses = db.Column(db.Integer, default=0)
    
    messages = db.relationship('ChatMessage', backref='session', lazy=True)
    category = db.relationship('LessonCategory')


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class VocabularyReview(db.Model):
    __tablename__ = 'vocabulary_reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    vocabulary_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id'), nullable=False)
    ease_factor = db.Column(db.Float, default=2.5)
    interval_days = db.Column(db.Integer, default=1)
    repetitions = db.Column(db.Integer, default=0)
    next_review_date = db.Column(db.DateTime, default=datetime.now)
    last_reviewed = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='vocabulary_reviews')
    vocabulary = db.relationship('Vocabulary', backref='reviews')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'vocabulary_id', name='uq_user_vocabulary_review'),
    )
