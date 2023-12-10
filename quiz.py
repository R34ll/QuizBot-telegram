from dataclasses import dataclass,fields
import requests
from base64 import b64decode
import random

s = requests.Session()
url = "https://opentdb.com/api.php?"




@dataclass
class QuizCategory:
    general_knowledge: int = 9
    books: int = 10
    film: int = 11
    music: int = 12
    musicals_theatres: int = 13
    television: int = 14
    video_games: int = 15
    board_games: int = 16
    science_nature: int = 17
    science_computers: int = 18
    science_mathematics: int = 19
    mythology: int = 20
    sports: int = 21
    geography: int = 22
    history: int = 23
    politics: int = 24
    art: int = 25
    celebrities: int = 26
    animals: int = 27
    vehicles: int = 28
    comics: int = 29
    science_gadgets: int = 30
    anime_manga: int = 31
    cartoon_animations: int = 32

    def list_fields()->list:
        fields_list= [field.name for field in fields(QuizCategory)]
        return fields_list
    

    def get_value(category):
        c =  category.lower()
        if c in QuizCategory.__annotations__:
            return getattr(QuizCategory, c)



@dataclass
class QuizDifficulty:
    easy:str = "easy"
    medium:str = "medium"
    hard:str = "hard"

    def list_fields() -> list:

        fields_list = [field.name for field in fields(QuizDifficulty)]
        return fields_list





class QuizBot:
    def __init__(self):

        self.user_score = 0
        self.quiz_list:list =[]
        self.quiz_list_hist = []

        self.category:QuizCategory = QuizCategory.art
        self.difficulty:QuizDifficulty = QuizDifficulty.easy
        self.n_quiz  = 3
         


    def generate_quiz(self, encode:str="base64", _type:str="multiple") -> list:

        
        r = s.post(
                f"{url}amount={self.n_quiz}&category={self.category}&difficulty={self.difficulty}&encode={encode}&type={_type}"
            )

        q_l = []

        for question in r.json()['results']:
            # type_q = b64decode(question['type']).decode('utf-8')
            difficulty_q = b64decode(question['difficulty']).decode('utf-8')
            category_q = b64decode(question['category']).decode('utf-8')


            self.category = category_q
            self.difficulty = difficulty_q
            
            question_q:str = b64decode(question['question']).decode('utf-8')
            question_correct_q:str = b64decode(question['correct_answer']).decode('utf-8')
            question_incorrect_q:str = [b64decode(q_ic).decode('utf-8') for q_ic in question['incorrect_answers']]

            res:dict = self.format_quiz(
                question_q,
                question_correct_q, 
                question_incorrect_q)

            q_l.append(res)

        
        self.quiz_list = q_l
        return q_l

    def format_quiz(self,quiz,answer,incorrect) -> dict:

        q_l = incorrect
        q_l.append(answer)
        random.shuffle(q_l)

        q = {"quiz":"",
            "questions":{},
            "answer":"",}
        
        q['quiz'] = quiz

        q['questions']['a'] = q_l[0]
        q['questions']['b'] = q_l[1]
        q['questions']['c'] = q_l[2]
        q['questions']['d'] = q_l[3]

        q['answer'] = next(key for key, val in q['questions'].items() if val == answer)

        return q


    def start_quiz(self,update,ctx, list_quiz:list):
        user_id = update.message.from_user.id
        self.user_score = 0


        self.quiz_list = list_quiz


    def end_quiz(self):
        print("Congratulatinos. You answer {self.user_score} corrects answer")


    def get_new_quiz(self):
        if len(self.quiz_list) == 0:
            return None

        return self.quiz_list.pop(0)


    def handle_answer(self,answer):

        q = self.quiz_list[0]
        
        correct_answer = q['answer']

        if answer == correct_answer:
            self.user_score+=1
            self.quiz_list_hist.append({
                "quiz": q['quiz'],
                "user_answer": q['questions'][answer],
                "correct_answer": q['questions'][correct_answer],
                "emoji": '✅'
            })


            return True

        else:
            self.quiz_list_hist.append({
                "quiz": q['quiz'],
                "user_answer": q['questions'][answer],
                "correct_answer": q['questions'][correct_answer],
                "emoji": '❌'
            })            
            return False


        # handle user answer
        # compare user answer with correct answer
        # update score








