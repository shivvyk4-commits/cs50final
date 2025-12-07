from app import app, db
from models import LessonCategory, Vocabulary, Verb


def seed_lesson_content():
    with app.app_context():
        if LessonCategory.query.first() is not None:
            return
        
        categories_data = [
            {
                "name": "Greetings",
                "description": "Learn basic greetings and introductions",
                "icon": "hand-wave",
                "order": 1,
                "vocabulary": [
                    ("Hola", "Hello", "OH-lah"),
                    ("Buenos días", "Good morning", "BWEH-nohs DEE-ahs"),
                    ("Buenas tardes", "Good afternoon", "BWEH-nahs TAR-dehs"),
                    ("Buenas noches", "Good night", "BWEH-nahs NOH-chehs"),
                    ("¿Cómo estás?", "How are you?", "KOH-moh ehs-TAHS"),
                    ("Bien", "Good/Well", "byehn"),
                    ("Mal", "Bad", "mahl"),
                    ("¿Cómo te llamas?", "What is your name?", "KOH-moh teh YAH-mahs"),
                    ("Me llamo", "My name is", "meh YAH-moh"),
                    ("Mucho gusto", "Nice to meet you", "MOO-choh GOOS-toh"),
                    ("Adiós", "Goodbye", "ah-DYOHS"),
                    ("Hasta luego", "See you later", "AHS-tah LWEH-goh"),
                ],
                "verbs": [
                    ("ser", "to be (permanent)", "soy", "eres", "es", "somos", "sois", "son"),
                    ("estar", "to be (temporary)", "estoy", "estás", "está", "estamos", "estáis", "están"),
                    ("llamarse", "to be called", "me llamo", "te llamas", "se llama", "nos llamamos", "os llamáis", "se llaman"),
                ]
            },
            {
                "name": "Food",
                "description": "Learn vocabulary about food and meals",
                "icon": "utensils",
                "order": 2,
                "vocabulary": [
                    ("La comida", "Food", "lah koh-MEE-dah"),
                    ("El desayuno", "Breakfast", "ehl deh-sah-YOO-noh"),
                    ("El almuerzo", "Lunch", "ehl ahl-MWEHR-soh"),
                    ("La cena", "Dinner", "lah SEH-nah"),
                    ("El pan", "Bread", "ehl pahn"),
                    ("El arroz", "Rice", "ehl ah-ROHS"),
                    ("La carne", "Meat", "lah KAR-neh"),
                    ("El pollo", "Chicken", "ehl POH-yoh"),
                    ("El pescado", "Fish", "ehl pehs-KAH-doh"),
                    ("Las frutas", "Fruits", "lahs FROO-tahs"),
                    ("Las verduras", "Vegetables", "lahs behr-DOO-rahs"),
                    ("El agua", "Water", "ehl AH-gwah"),
                ],
                "verbs": [
                    ("comer", "to eat", "como", "comes", "come", "comemos", "coméis", "comen"),
                    ("beber", "to drink", "bebo", "bebes", "bebe", "bebemos", "bebéis", "beben"),
                    ("cocinar", "to cook", "cocino", "cocinas", "cocina", "cocinamos", "cocináis", "cocinan"),
                ]
            },
            {
                "name": "Clothing",
                "description": "Learn vocabulary about clothes and fashion",
                "icon": "shirt",
                "order": 3,
                "vocabulary": [
                    ("La ropa", "Clothes", "lah ROH-pah"),
                    ("La camisa", "Shirt", "lah kah-MEE-sah"),
                    ("Los pantalones", "Pants", "lohs pahn-tah-LOH-nehs"),
                    ("El vestido", "Dress", "ehl behs-TEE-doh"),
                    ("La falda", "Skirt", "lah FAHL-dah"),
                    ("Los zapatos", "Shoes", "lohs sah-PAH-tohs"),
                    ("El sombrero", "Hat", "ehl sohm-BREH-roh"),
                    ("La chaqueta", "Jacket", "lah chah-KEH-tah"),
                    ("Los calcetines", "Socks", "lohs kahl-seh-TEE-nehs"),
                    ("El abrigo", "Coat", "ehl ah-BREE-goh"),
                ],
                "verbs": [
                    ("llevar", "to wear", "llevo", "llevas", "lleva", "llevamos", "lleváis", "llevan"),
                    ("vestirse", "to get dressed", "me visto", "te vistes", "se viste", "nos vestimos", "os vestís", "se visten"),
                    ("comprar", "to buy", "compro", "compras", "compra", "compramos", "compráis", "compran"),
                ]
            },
            {
                "name": "Family",
                "description": "Learn vocabulary about family members",
                "icon": "users",
                "order": 4,
                "vocabulary": [
                    ("La familia", "Family", "lah fah-MEE-lyah"),
                    ("La madre", "Mother", "lah MAH-dreh"),
                    ("El padre", "Father", "ehl PAH-dreh"),
                    ("Los padres", "Parents", "lohs PAH-drehs"),
                    ("El hermano", "Brother", "ehl ehr-MAH-noh"),
                    ("La hermana", "Sister", "lah ehr-MAH-nah"),
                    ("El abuelo", "Grandfather", "ehl ah-BWEH-loh"),
                    ("La abuela", "Grandmother", "lah ah-BWEH-lah"),
                    ("El tío", "Uncle", "ehl TEE-oh"),
                    ("La tía", "Aunt", "lah TEE-ah"),
                    ("El primo", "Cousin (male)", "ehl PREE-moh"),
                    ("La prima", "Cousin (female)", "lah PREE-mah"),
                ],
                "verbs": [
                    ("tener", "to have", "tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen"),
                    ("querer", "to love/want", "quiero", "quieres", "quiere", "queremos", "queréis", "quieren"),
                    ("vivir", "to live", "vivo", "vives", "vive", "vivimos", "vivís", "viven"),
                ]
            },
            {
                "name": "Sports",
                "description": "Learn vocabulary about sports and activities",
                "icon": "futbol",
                "order": 5,
                "vocabulary": [
                    ("El deporte", "Sport", "ehl deh-POHR-teh"),
                    ("El fútbol", "Soccer", "ehl FOOT-bohl"),
                    ("El baloncesto", "Basketball", "ehl bah-lohn-SEHS-toh"),
                    ("El tenis", "Tennis", "ehl TEH-nees"),
                    ("La natación", "Swimming", "lah nah-tah-SYOHN"),
                    ("El equipo", "Team", "ehl eh-KEE-poh"),
                    ("El jugador", "Player", "ehl hoo-gah-DOHR"),
                    ("El partido", "Match/Game", "ehl pahr-TEE-doh"),
                    ("Ganar", "To win", "gah-NAHR"),
                    ("Perder", "To lose", "pehr-DEHR"),
                ],
                "verbs": [
                    ("jugar", "to play", "juego", "juegas", "juega", "jugamos", "jugáis", "juegan"),
                    ("correr", "to run", "corro", "corres", "corre", "corremos", "corréis", "corren"),
                    ("nadar", "to swim", "nado", "nadas", "nada", "nadamos", "nadáis", "nadan"),
                ]
            },
            {
                "name": "Travel",
                "description": "Learn vocabulary for traveling",
                "icon": "plane",
                "order": 6,
                "vocabulary": [
                    ("El viaje", "Trip/Travel", "ehl BYAH-heh"),
                    ("El aeropuerto", "Airport", "ehl ah-eh-roh-PWEHR-toh"),
                    ("El avión", "Airplane", "ehl ah-BYOHN"),
                    ("El hotel", "Hotel", "ehl oh-TEHL"),
                    ("La maleta", "Suitcase", "lah mah-LEH-tah"),
                    ("El pasaporte", "Passport", "ehl pah-sah-POHR-teh"),
                    ("El billete", "Ticket", "ehl bee-YEH-teh"),
                    ("La playa", "Beach", "lah PLAH-yah"),
                    ("La montaña", "Mountain", "lah mohn-TAH-nyah"),
                    ("El museo", "Museum", "ehl moo-SEH-oh"),
                ],
                "verbs": [
                    ("viajar", "to travel", "viajo", "viajas", "viaja", "viajamos", "viajáis", "viajan"),
                    ("ir", "to go", "voy", "vas", "va", "vamos", "vais", "van"),
                    ("visitar", "to visit", "visito", "visitas", "visita", "visitamos", "visitáis", "visitan"),
                ]
            }
        ]
        
        for cat_data in categories_data:
            category = LessonCategory(
                name=cat_data["name"],
                description=cat_data["description"],
                icon=cat_data["icon"],
                order=cat_data["order"]
            )
            db.session.add(category)
            db.session.flush()
            
            for vocab in cat_data["vocabulary"]:
                v = Vocabulary(
                    spanish_word=vocab[0],
                    english_word=vocab[1],
                    pronunciation=vocab[2],
                    category_id=category.id
                )
                db.session.add(v)
            
            for verb in cat_data["verbs"]:
                v = Verb(
                    infinitive=verb[0],
                    english_meaning=verb[1],
                    yo=verb[2],
                    tu=verb[3],
                    el_ella=verb[4],
                    nosotros=verb[5],
                    vosotros=verb[6],
                    ellos=verb[7],
                    category_id=category.id
                )
                db.session.add(v)
        
        db.session.commit()
        print("Lesson content seeded successfully!")


if __name__ == "__main__":
    seed_lesson_content()
