from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, flash, session
from flask_login import current_user

from app import app, db
from models import (User, LessonCategory, Vocabulary, Verb, UserProgress, 
                   ScheduledLesson, ChatSession, ChatMessage, VocabularyReview)
from replit_auth import require_login, make_replit_blueprint
from seed_data import seed_lesson_content
import calendar_service
import gemini_service

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

seed_lesson_content()


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.onboarding_complete:
            return redirect(url_for('onboarding'))
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/onboarding', methods=['GET', 'POST'])
@require_login
def onboarding():
    if current_user.onboarding_complete:
        return redirect(url_for('dashboard'))
    
    step = request.args.get('step', '1')
    
    if request.method == 'POST':
        if step == '1':
            current_user.experience_years = int(request.form.get('experience_years', 0))
            current_user.lesson_duration = int(request.form.get('lesson_duration', 30))
            db.session.commit()
            return redirect(url_for('onboarding', step='2'))
        
        elif step == '2':
            schedule_type = request.form.get('schedule_type')
            
            if schedule_type == 'manual':
                preferred_time = request.form.get('preferred_time')
                current_user.preferred_time = preferred_time
                current_user.calendar_connected = False
            else:
                current_user.calendar_connected = calendar_service.is_calendar_connected()
            
            current_user.onboarding_complete = True
            db.session.commit()
            
            first_category = LessonCategory.query.order_by(LessonCategory.order).first()
            if first_category and current_user.calendar_connected:
                slot = calendar_service.find_available_slot(current_user.lesson_duration)
                if slot:
                    event_id = calendar_service.create_calendar_event(
                        f"Lango Spanish Lesson: {first_category.name}",
                        slot,
                        current_user.lesson_duration,
                        f"Time to learn Spanish! Category: {first_category.name}"
                    )
                    if event_id:
                        lesson = ScheduledLesson(
                            user_id=current_user.id,
                            category_id=first_category.id,
                            scheduled_time=slot,
                            duration_minutes=current_user.lesson_duration,
                            calendar_event_id=event_id
                        )
                        db.session.add(lesson)
                        db.session.commit()
            
            return redirect(url_for('dashboard'))
    
    calendar_connected = calendar_service.is_calendar_connected()
    return render_template('onboarding.html', step=step, calendar_connected=calendar_connected)


@app.route('/dashboard')
@require_login
def dashboard():
    if not current_user.onboarding_complete:
        return redirect(url_for('onboarding'))
    
    categories = LessonCategory.query.order_by(LessonCategory.order).all()
    
    progress_dict = {}
    for p in current_user.progress:
        progress_dict[p.category_id] = p
    
    upcoming_lessons = ScheduledLesson.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).filter(
        ScheduledLesson.scheduled_time >= datetime.now()
    ).order_by(ScheduledLesson.scheduled_time).limit(3).all()
    
    total_vocab = 0
    completed_lessons = 0
    for p in current_user.progress:
        if p.vocabulary_completed:
            total_vocab += Vocabulary.query.filter_by(category_id=p.category_id).count()
        if p.conversation_completed:
            completed_lessons += 1
    
    streak = calculate_streak(current_user.id)
    
    return render_template('dashboard.html',
                          categories=categories,
                          progress_dict=progress_dict,
                          upcoming_lessons=upcoming_lessons,
                          total_vocab=total_vocab,
                          completed_lessons=completed_lessons,
                          streak=streak)


def calculate_streak(user_id):
    sessions = ChatSession.query.filter_by(user_id=user_id).filter(
        ChatSession.ended_at != None
    ).order_by(ChatSession.ended_at.desc()).all()
    
    if not sessions:
        return 0
    
    streak = 0
    current_date = datetime.now().date()
    
    dates_with_activity = set()
    for s in sessions:
        if s.ended_at:
            dates_with_activity.add(s.ended_at.date())
    
    for i in range(30):
        check_date = current_date - timedelta(days=i)
        if check_date in dates_with_activity:
            if i == 0 or (current_date - timedelta(days=i-1)) in dates_with_activity or i == 0:
                streak += 1
            else:
                break
        elif i == 0:
            continue
        else:
            break
    
    return streak


@app.route('/lesson/<int:category_id>')
@require_login
def lesson(category_id):
    category = LessonCategory.query.get_or_404(category_id)
    vocabulary = Vocabulary.query.filter_by(category_id=category_id).all()
    verbs = Verb.query.filter_by(category_id=category_id).all()
    
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        category_id=category_id
    ).first()
    
    return render_template('lesson.html',
                          category=category,
                          vocabulary=vocabulary,
                          verbs=verbs,
                          progress=progress)


@app.route('/lesson/<int:category_id>/vocabulary')
@require_login
def vocabulary_lesson(category_id):
    category = LessonCategory.query.get_or_404(category_id)
    vocabulary = Vocabulary.query.filter_by(category_id=category_id).all()
    
    return render_template('vocabulary.html',
                          category=category,
                          vocabulary=vocabulary)


@app.route('/lesson/<int:category_id>/vocabulary/complete', methods=['POST'])
@require_login
def complete_vocabulary(category_id):
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        category_id=category_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            category_id=category_id
        )
        db.session.add(progress)
    
    progress.vocabulary_completed = True
    
    vocab_items = Vocabulary.query.filter_by(category_id=category_id).all()
    for vocab in vocab_items:
        existing = VocabularyReview.query.filter_by(
            user_id=current_user.id,
            vocabulary_id=vocab.id
        ).first()
        if not existing:
            new_review = VocabularyReview(
                user_id=current_user.id,
                vocabulary_id=vocab.id,
                next_review_date=datetime.now()
            )
            db.session.add(new_review)
    
    db.session.commit()
    
    return redirect(url_for('lesson', category_id=category_id))


@app.route('/lesson/<int:category_id>/verbs')
@require_login
def verbs_lesson(category_id):
    category = LessonCategory.query.get_or_404(category_id)
    verbs = Verb.query.filter_by(category_id=category_id).all()
    
    return render_template('verbs.html',
                          category=category,
                          verbs=verbs)


@app.route('/lesson/<int:category_id>/verbs/complete', methods=['POST'])
@require_login
def complete_verbs(category_id):
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        category_id=category_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            category_id=category_id
        )
        db.session.add(progress)
    
    progress.verbs_completed = True
    db.session.commit()
    
    return redirect(url_for('lesson', category_id=category_id))


@app.route('/lesson/<int:category_id>/conversation')
@require_login
def conversation(category_id):
    category = LessonCategory.query.get_or_404(category_id)
    
    user_difficulty = current_user.difficulty_level or 1
    
    chat_session = ChatSession.query.filter_by(
        user_id=current_user.id,
        category_id=category_id,
        ended_at=None
    ).first()
    
    if not chat_session:
        chat_session = ChatSession(
            user_id=current_user.id,
            category_id=category_id,
            difficulty_level=user_difficulty
        )
        db.session.add(chat_session)
        db.session.commit()
        
        initial_greeting = gemini_service.get_initial_greeting(category.name, user_difficulty)
        initial_message = ChatMessage(
            session_id=chat_session.id,
            role='assistant',
            content=initial_greeting
        )
        db.session.add(initial_message)
        db.session.commit()
    
    messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.created_at).all()
    
    difficulty_names = {1: 'Beginner', 2: 'Intermediate', 3: 'Advanced'}
    
    return render_template('conversation.html',
                          category=category,
                          session=chat_session,
                          messages=messages,
                          difficulty_level=chat_session.difficulty_level,
                          difficulty_name=difficulty_names.get(chat_session.difficulty_level, 'Beginner'))


@app.route('/lesson/<int:category_id>/conversation/send', methods=['POST'])
@require_login
def send_message(category_id):
    category = LessonCategory.query.get_or_404(category_id)
    user_message = request.form.get('message', '').strip()
    
    if not user_message:
        return redirect(url_for('conversation', category_id=category_id))
    
    chat_session = ChatSession.query.filter_by(
        user_id=current_user.id,
        category_id=category_id,
        ended_at=None
    ).first()
    
    if not chat_session:
        return redirect(url_for('conversation', category_id=category_id))
    
    user_msg = ChatMessage(
        session_id=chat_session.id,
        role='user',
        content=user_message
    )
    db.session.add(user_msg)
    db.session.commit()
    
    messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.created_at).all()
    
    vocabulary = Vocabulary.query.filter_by(category_id=category_id).all()
    verbs = Verb.query.filter_by(category_id=category_id).all()
    
    vocab_list = [{'spanish': v.spanish_word, 'english': v.english_word} for v in vocabulary]
    verb_list = [{'infinitive': v.infinitive, 'english': v.english_meaning} for v in verbs]
    
    message_history = [{'role': m.role, 'content': m.content} for m in messages]
    
    session_difficulty = chat_session.difficulty_level or 1
    ai_response = gemini_service.chat_with_ai(message_history, category.name, vocab_list, verb_list, session_difficulty)
    
    performance = gemini_service.analyze_ai_response(ai_response)
    if performance['has_correction']:
        chat_session.corrections_count = (chat_session.corrections_count or 0) + 1
    if performance['has_good']:
        chat_session.successful_responses = (chat_session.successful_responses or 0) + 1
    
    total = (chat_session.corrections_count or 0) + (chat_session.successful_responses or 0)
    if total > 0:
        chat_session.performance_score = (chat_session.successful_responses or 0) / total * 100
    
    db.session.commit()
    
    ai_msg = ChatMessage(
        session_id=chat_session.id,
        role='assistant',
        content=ai_response
    )
    db.session.add(ai_msg)
    db.session.commit()
    
    return redirect(url_for('conversation', category_id=category_id))


@app.route('/lesson/<int:category_id>/conversation/complete', methods=['POST'])
@require_login
def complete_conversation(category_id):
    chat_session = ChatSession.query.filter_by(
        user_id=current_user.id,
        category_id=category_id,
        ended_at=None
    ).first()
    
    difficulty_change = None
    if chat_session:
        chat_session.ended_at = datetime.now()
        
        new_difficulty, change_type = gemini_service.calculate_difficulty_adjustment(
            chat_session.corrections_count or 0,
            chat_session.successful_responses or 0,
            current_user.difficulty_level or 1
        )
        
        if change_type:
            current_user.difficulty_level = new_difficulty
            difficulty_change = change_type
        
        db.session.commit()
    
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        category_id=category_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            category_id=category_id
        )
        db.session.add(progress)
    
    progress.conversation_completed = True
    progress.completed_at = datetime.now()
    db.session.commit()
    
    scheduled = ScheduledLesson.query.filter_by(
        user_id=current_user.id,
        category_id=category_id,
        completed=False
    ).first()
    if scheduled:
        scheduled.completed = True
        db.session.commit()
    
    if difficulty_change == "increase":
        difficulty_names = {1: 'Beginner', 2: 'Intermediate', 3: 'Advanced'}
        flash(f'Great job! Your difficulty level has been upgraded to {difficulty_names.get(current_user.difficulty_level, "Unknown")}!', 'success')
    elif difficulty_change == "decrease":
        difficulty_names = {1: 'Beginner', 2: 'Intermediate', 3: 'Advanced'}
        flash(f'Your difficulty level has been adjusted to {difficulty_names.get(current_user.difficulty_level, "Unknown")} to help you practice more.', 'info')
    
    return redirect(url_for('lesson', category_id=category_id))


@app.route('/schedule')
@require_login
def schedule():
    categories = LessonCategory.query.order_by(LessonCategory.order).all()
    scheduled_lessons = ScheduledLesson.query.filter_by(
        user_id=current_user.id
    ).order_by(ScheduledLesson.scheduled_time).all()
    
    calendar_connected = calendar_service.is_calendar_connected()
    
    return render_template('schedule.html',
                          categories=categories,
                          scheduled_lessons=scheduled_lessons,
                          calendar_connected=calendar_connected)


@app.route('/schedule/add', methods=['POST'])
@require_login
def add_schedule():
    category_id = int(request.form.get('category_id'))
    schedule_type = request.form.get('schedule_type')
    
    category = LessonCategory.query.get_or_404(category_id)
    
    if schedule_type == 'auto':
        slot = calendar_service.find_available_slot(current_user.lesson_duration)
        if not slot:
            flash('Could not find an available time slot. Please try manual scheduling.', 'error')
            return redirect(url_for('schedule'))
    else:
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        try:
            slot = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except:
            flash('Invalid date/time format.', 'error')
            return redirect(url_for('schedule'))
    
    event_id = None
    if calendar_service.is_calendar_connected():
        event_id = calendar_service.create_calendar_event(
            f"Lango Spanish Lesson: {category.name}",
            slot,
            current_user.lesson_duration,
            f"Time to learn Spanish! Category: {category.name}"
        )
    
    lesson = ScheduledLesson(
        user_id=current_user.id,
        category_id=category_id,
        scheduled_time=slot,
        duration_minutes=current_user.lesson_duration,
        calendar_event_id=event_id
    )
    db.session.add(lesson)
    db.session.commit()
    
    flash('Lesson scheduled successfully!', 'success')
    return redirect(url_for('schedule'))


@app.route('/schedule/reschedule/<int:lesson_id>', methods=['GET', 'POST'])
@require_login
def reschedule_lesson(lesson_id):
    lesson = ScheduledLesson.query.filter_by(
        id=lesson_id,
        user_id=current_user.id
    ).first_or_404()
    
    if lesson.completed:
        flash('This lesson has already been completed.', 'error')
        return redirect(url_for('schedule'))
    
    if request.method == 'POST':
        schedule_type = request.form.get('schedule_type')
        
        if schedule_type == 'auto':
            new_slot = calendar_service.find_available_slot(lesson.duration_minutes)
            if not new_slot:
                flash('Could not find an available time slot. Please try manual scheduling.', 'error')
                return redirect(url_for('reschedule_lesson', lesson_id=lesson_id))
        else:
            date_str = request.form.get('date')
            time_str = request.form.get('time')
            try:
                new_slot = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except:
                flash('Invalid date/time format.', 'error')
                return redirect(url_for('reschedule_lesson', lesson_id=lesson_id))
        
        old_time = lesson.scheduled_time
        lesson.scheduled_time = new_slot
        
        if lesson.calendar_event_id and calendar_service.is_calendar_connected():
            calendar_service.update_calendar_event(
                lesson.calendar_event_id,
                start_time=new_slot,
                duration_minutes=lesson.duration_minutes
            )
        
        db.session.commit()
        flash(f'Lesson rescheduled from {old_time.strftime("%b %d, %I:%M %p")} to {new_slot.strftime("%b %d, %I:%M %p")}!', 'success')
        return redirect(url_for('schedule'))
    
    calendar_connected = calendar_service.is_calendar_connected()
    return render_template('reschedule.html',
                          lesson=lesson,
                          calendar_connected=calendar_connected)


@app.route('/schedule/cancel/<int:lesson_id>', methods=['POST'])
@require_login
def cancel_lesson(lesson_id):
    lesson = ScheduledLesson.query.filter_by(
        id=lesson_id,
        user_id=current_user.id
    ).first_or_404()
    
    if lesson.calendar_event_id and calendar_service.is_calendar_connected():
        calendar_service.delete_calendar_event(lesson.calendar_event_id)
    
    db.session.delete(lesson)
    db.session.commit()
    
    flash('Lesson cancelled successfully.', 'info')
    return redirect(url_for('schedule'))


@app.route('/progress')
@require_login
def progress():
    categories = LessonCategory.query.order_by(LessonCategory.order).all()
    user_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
    
    progress_dict = {}
    for p in user_progress:
        progress_dict[p.category_id] = p
    
    total_vocab = sum([Vocabulary.query.filter_by(category_id=c.id).count() for c in categories])
    learned_vocab = 0
    for p in user_progress:
        if p.vocabulary_completed:
            learned_vocab += Vocabulary.query.filter_by(category_id=p.category_id).count()
    
    completed_lessons = sum([1 for p in user_progress if p.conversation_completed])
    total_lessons = len(categories)
    
    streak = calculate_streak(current_user.id)
    
    chat_sessions = ChatSession.query.filter_by(user_id=current_user.id).all()
    conversation_count = len([s for s in chat_sessions if s.ended_at])
    
    all_reviews = VocabularyReview.query.filter_by(user_id=current_user.id).all()
    mastery_stats = {
        'new': 0,
        'learning': 0,
        'reviewing': 0,
        'mastered': 0
    }
    
    reviewed_vocab_ids = set()
    for review in all_reviews:
        reviewed_vocab_ids.add(review.vocabulary_id)
        if review.repetitions == 0:
            mastery_stats['new'] += 1
        elif review.repetitions < 3:
            mastery_stats['learning'] += 1
        elif review.repetitions < 5:
            mastery_stats['reviewing'] += 1
        else:
            mastery_stats['mastered'] += 1
    
    total_messages = 0
    user_messages = 0
    ai_messages = 0
    completed_sessions = [s for s in chat_sessions if s.ended_at is not None]
    
    for session in completed_sessions:
        messages = ChatMessage.query.filter_by(session_id=session.id).all()
        total_messages += len(messages)
        user_messages += len([m for m in messages if m.role == 'user'])
        ai_messages += len([m for m in messages if m.role == 'assistant'])
    
    if completed_sessions and total_messages > 0:
        avg_messages_per_session = round(total_messages / len(completed_sessions), 1)
    else:
        avg_messages_per_session = 0
    
    total_practice_minutes = 0
    for session in completed_sessions:
        if session.started_at is not None and session.ended_at is not None:
            try:
                duration = (session.ended_at - session.started_at).total_seconds() / 60
                if duration > 0:
                    total_practice_minutes += min(duration, 120)
            except (TypeError, AttributeError):
                pass
    total_practice_minutes = round(total_practice_minutes)
    
    activity_data = []
    for i in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        vocab_count = VocabularyReview.query.filter(
            VocabularyReview.user_id == current_user.id,
            VocabularyReview.last_reviewed != None,
            VocabularyReview.last_reviewed >= day_start,
            VocabularyReview.last_reviewed <= day_end
        ).count()
        
        session_count = ChatSession.query.filter(
            ChatSession.user_id == current_user.id,
            ChatSession.ended_at != None,
            ChatSession.ended_at >= day_start,
            ChatSession.ended_at <= day_end
        ).count()
        
        activity_data.append({
            'day': day.strftime('%a'),
            'date': day.strftime('%m/%d'),
            'reviews': vocab_count,
            'conversations': session_count
        })
    
    category_mastery = []
    all_vocab_ids = [v.id for v in Vocabulary.query.all()]
    user_reviews_dict = {r.vocabulary_id: r for r in all_reviews}
    
    for category in categories:
        category_vocab = Vocabulary.query.filter_by(category_id=category.id).all()
        mastered_in_category = 0
        total_in_category = len(category_vocab)
        
        for vocab in category_vocab:
            review = user_reviews_dict.get(vocab.id)
            if review and review.repetitions >= 5:
                mastered_in_category += 1
        
        if total_in_category > 0:
            mastery_percent = round((mastered_in_category / total_in_category) * 100)
        else:
            mastery_percent = 0
            
        category_mastery.append({
            'name': category.name,
            'mastered': mastered_in_category,
            'total': total_in_category,
            'percent': mastery_percent
        })
    
    has_review_data = sum(mastery_stats.values()) > 0
    
    return render_template('progress.html',
                          categories=categories,
                          progress_dict=progress_dict,
                          total_vocab=total_vocab,
                          learned_vocab=learned_vocab,
                          completed_lessons=completed_lessons,
                          total_lessons=total_lessons,
                          streak=streak,
                          conversation_count=conversation_count,
                          mastery_stats=mastery_stats,
                          has_review_data=has_review_data,
                          total_messages=total_messages,
                          user_messages=user_messages,
                          avg_messages_per_session=avg_messages_per_session,
                          total_practice_minutes=total_practice_minutes,
                          activity_data=activity_data,
                          category_mastery=category_mastery)


def calculate_sm2(quality, repetitions, ease_factor, interval):
    ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        repetitions += 1
        if repetitions == 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval = max(1, round(interval * ease_factor))
    
    interval = max(1, interval)
    
    return repetitions, ease_factor, interval


@app.route('/review')
@require_login
def review():
    now = datetime.now()
    
    due_reviews = VocabularyReview.query.filter(
        VocabularyReview.user_id == current_user.id,
        VocabularyReview.next_review_date <= now
    ).order_by(VocabularyReview.next_review_date).all()
    
    categories = LessonCategory.query.order_by(LessonCategory.order).all()
    
    total_reviews = VocabularyReview.query.filter_by(user_id=current_user.id).count()
    mastered_count = VocabularyReview.query.filter(
        VocabularyReview.user_id == current_user.id,
        VocabularyReview.repetitions >= 5
    ).count()
    
    return render_template('review.html',
                          due_reviews=due_reviews,
                          categories=categories,
                          total_reviews=total_reviews,
                          mastered_count=mastered_count)


@app.route('/review/card/<int:review_id>')
@require_login
def review_card(review_id):
    review = VocabularyReview.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('review_card.html', review=review)


@app.route('/review/rate/<int:review_id>', methods=['POST'])
@require_login
def rate_review(review_id):
    review = VocabularyReview.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()
    
    quality = int(request.form.get('quality', 3))
    quality = max(0, min(5, quality))
    
    repetitions, ease_factor, interval = calculate_sm2(
        quality,
        review.repetitions,
        review.ease_factor,
        review.interval_days
    )
    
    review.repetitions = repetitions
    review.ease_factor = ease_factor
    review.interval_days = interval
    review.last_reviewed = datetime.now()
    review.next_review_date = datetime.now() + timedelta(days=interval)
    
    db.session.commit()
    
    next_review = VocabularyReview.query.filter(
        VocabularyReview.user_id == current_user.id,
        VocabularyReview.next_review_date <= datetime.now(),
        VocabularyReview.id != review_id
    ).order_by(VocabularyReview.next_review_date).first()
    
    if next_review:
        return redirect(url_for('review_card', review_id=next_review.id))
    
    flash('Great job! You completed all your reviews for now.', 'success')
    return redirect(url_for('review'))


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404
