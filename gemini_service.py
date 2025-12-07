import os
import logging
from google import genai
from google.genai import types

client = None

def get_client():
    global client
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and client is None:
        try:
            client = genai.Client(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {e}")
            client = None
    return client


def get_difficulty_guidelines(difficulty_level):
    if difficulty_level == 1:
        return {
            'level_name': 'Beginner',
            'spanish_ratio': '30%',
            'sentence_complexity': 'simple, short sentences',
            'vocabulary_scope': 'basic vocabulary only',
            'grammar_focus': 'present tense, simple questions',
            'correction_style': 'always translate and explain in English',
            'response_length': 'short responses (1-2 sentences)'
        }
    elif difficulty_level == 2:
        return {
            'level_name': 'Intermediate',
            'spanish_ratio': '60%',
            'sentence_complexity': 'compound sentences with connectors',
            'vocabulary_scope': 'expand beyond lesson vocabulary',
            'grammar_focus': 'past tense, future tense, subjunctive basics',
            'correction_style': 'correct in Spanish with brief English explanation',
            'response_length': 'medium responses (2-3 sentences)'
        }
    else:
        return {
            'level_name': 'Advanced',
            'spanish_ratio': '85%',
            'sentence_complexity': 'complex sentences, idiomatic expressions',
            'vocabulary_scope': 'advanced vocabulary, slang, regional variations',
            'grammar_focus': 'all tenses, subjunctive, conditional',
            'correction_style': 'correct entirely in Spanish',
            'response_length': 'longer, more elaborate responses'
        }


def get_conversation_prompt(category_name, vocabulary_words, verbs, difficulty_level=1):
    vocab_list = ", ".join([f"{v['spanish']} ({v['english']})" for v in vocabulary_words[:10]])
    verb_list = ", ".join([v['infinitive'] for v in verbs[:5]])
    
    difficulty = get_difficulty_guidelines(difficulty_level)
    
    prompts_by_category = {
        "Greetings": [
            "Ask the student to introduce themselves in Spanish",
            "Ask how they are doing today",
            "Ask where they are from"
        ],
        "Food": [
            "Ask about their favorite food",
            "Ask what they ate for breakfast",
            "Ask them to describe a typical meal in their country"
        ],
        "Clothing": [
            "Ask what they are wearing today",
            "Ask about their favorite piece of clothing",
            "Ask what they wear in different seasons"
        ],
        "Family": [
            "Ask about their family members",
            "Ask them to describe a family member",
            "Ask about family traditions"
        ],
        "Sports": [
            "Ask about their favorite sport",
            "Ask them to write about their favorite soccer player and why they like them",
            "Ask if they play any sports"
        ],
        "Travel": [
            "Ask about a place they want to visit",
            "Ask about their last vacation",
            "Ask them to describe their hometown"
        ]
    }
    
    category_prompts = prompts_by_category.get(category_name, [
        "Ask the student a question related to the topic",
        "Have a friendly conversation about daily life"
    ])
    
    return f"""You are a friendly Spanish language tutor helping a student practice conversational Spanish.
The current lesson category is: {category_name}
Vocabulary words for this lesson include: {vocab_list}
Verbs for this lesson include: {verb_list}

STUDENT DIFFICULTY LEVEL: {difficulty['level_name']}
- Use approximately {difficulty['spanish_ratio']} Spanish in your responses
- Use {difficulty['sentence_complexity']}
- Vocabulary scope: {difficulty['vocabulary_scope']}
- Grammar focus: {difficulty['grammar_focus']}
- When correcting mistakes: {difficulty['correction_style']}
- Response length: {difficulty['response_length']}

Guidelines:
1. Start by greeting the student in Spanish and asking a question appropriate for their level
2. Encourage them to respond in Spanish
3. If they make mistakes, gently correct them according to their level
4. Use vocabulary and verbs from the lesson when possible
5. Keep responses conversational and encouraging
6. Adjust your Spanish complexity based on the student's level
7. Suggested conversation topics: {', '.join(category_prompts)}

IMPORTANT: When the student makes a grammar or vocabulary error, include "[CORRECTION]" at the start of your correction. This helps track their progress.
When the student responds correctly with good Spanish, include "[GOOD]" to acknowledge their success.

Be patient, supportive, and make learning fun!"""


def chat_with_ai(messages, category_name, vocabulary_words, verbs, difficulty_level=1):
    try:
        gemini_client = get_client()
        if not gemini_client:
            return "The AI tutor is not available right now. Please make sure the Gemini API key is configured."
        
        system_prompt = get_conversation_prompt(category_name, vocabulary_words, verbs, difficulty_level)
        
        contents = []
        for msg in messages:
            role = "user" if msg['role'] == 'user' else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg['content'])]))
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=500,
            ),
        )
        
        return response.text if response.text else "Lo siento, I couldn't generate a response. Please try again."
    
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return f"Sorry, there was an error connecting to the AI tutor. Please try again later."


def analyze_ai_response(response_text):
    has_correction = "[CORRECTION]" in response_text
    has_good = "[GOOD]" in response_text
    
    return {
        'has_correction': has_correction,
        'has_good': has_good
    }


def calculate_difficulty_adjustment(session_corrections, session_successes, current_level):
    if session_corrections + session_successes < 3:
        return current_level, None
    
    total_responses = session_corrections + session_successes
    success_rate = session_successes / total_responses if total_responses > 0 else 0
    
    if success_rate >= 0.8 and total_responses >= 5 and current_level < 3:
        return current_level + 1, "increase"
    elif success_rate <= 0.3 and total_responses >= 5 and current_level > 1:
        return current_level - 1, "decrease"
    
    return current_level, None


def get_initial_greeting(category_name, difficulty_level=1):
    difficulty = get_difficulty_guidelines(difficulty_level)
    
    beginner_greetings = {
        "Greetings": "¡Hola! Bienvenido a la lección de saludos. I'm your Spanish tutor! Let's practice greetings. ¿Cómo te llamas? (What is your name?)",
        "Food": "¡Hola! Welcome to the food lesson! Let's talk about comida. ¿Cuál es tu comida favorita? (What is your favorite food?)",
        "Clothing": "¡Hola! Today we're learning about la ropa (clothing). ¿Qué llevas puesto hoy? (What are you wearing today?)",
        "Family": "¡Hola! Let's talk about la familia. ¿Cuántas personas hay en tu familia? (How many people are in your family?)",
        "Sports": "¡Hola! Today's topic is deportes (sports). ¿Te gustan los deportes? (Do you like sports?)",
        "Travel": "¡Hola! Let's discuss los viajes (travel). ¿A dónde te gustaría viajar? (Where would you like to travel?)"
    }
    
    intermediate_greetings = {
        "Greetings": "¡Hola! ¿Cómo estás hoy? Espero que estés bien. Cuéntame un poco sobre ti - ¿de dónde eres y qué te gusta hacer?",
        "Food": "¡Hola! Hoy vamos a hablar sobre la comida. ¿Qué comiste ayer para la cena? Cuéntame sobre tu plato favorito.",
        "Clothing": "¡Hola! ¿Cómo te vistes hoy? Describe lo que llevas puesto y cuál es tu estilo favorito.",
        "Family": "¡Hola! Vamos a hablar sobre la familia. ¿Podrías describir a un miembro de tu familia? ¿Cómo es?",
        "Sports": "¡Hola! Hablemos de deportes. ¿Practicas algún deporte? ¿Cuándo empezaste y por qué te gusta?",
        "Travel": "¡Hola! El tema de hoy es viajar. ¿Has viajado recientemente? Cuéntame sobre un lugar interesante que visitaste."
    }
    
    advanced_greetings = {
        "Greetings": "¡Buenas! ¿Qué tal te va? Me encantaría conocerte mejor. Cuéntame sobre tu vida cotidiana, tus pasatiempos y tus metas para aprender español.",
        "Food": "¡Hola! Hoy profundizaremos en el tema de la gastronomía. ¿Qué opinas de la cocina española o latinoamericana? ¿Has probado algún plato típico que te haya sorprendido?",
        "Clothing": "¡Hola! Vamos a explorar el mundo de la moda. ¿Cómo describirías tu estilo personal? ¿Crees que la ropa refleja la personalidad de una persona?",
        "Family": "¡Hola! Hoy conversaremos sobre las relaciones familiares. ¿Cómo son las tradiciones familiares en tu cultura? ¿Qué valores te han transmitido tus familiares?",
        "Sports": "¡Hola! Charlemos sobre el deporte a un nivel más profundo. ¿Qué papel juega el deporte en tu vida? ¿Crees que los deportes profesionales tienen demasiada influencia en la sociedad?",
        "Travel": "¡Hola! Exploremos el fascinante mundo de los viajes. ¿Qué experiencia de viaje te ha cambiado la perspectiva? ¿Prefieres el turismo de aventura o el cultural?"
    }
    
    if difficulty_level == 1:
        greetings = beginner_greetings
    elif difficulty_level == 2:
        greetings = intermediate_greetings
    else:
        greetings = advanced_greetings
    
    level_indicator = f"[Your level: {difficulty['level_name']}] "
    greeting = greetings.get(category_name, f"¡Hola! Welcome to the {category_name} lesson. Let's practice Spanish together!")
    
    return level_indicator + greeting
