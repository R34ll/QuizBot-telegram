import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from quiz import QuizBot, QuizCategory, QuizDifficulty



class MyQuizBot:
    def __init__(self,token):
        self.bot = telebot.TeleBot(token)
        self.btn_main_menu = [
            {'text':"Category", "callback_data":"cb_category"},
            {'text':"Difficult", "callback_data":"cb_difficulty"},
            {'text':"Amount of Questions: 5", "callback_data":"cb_quests_num"},
            {"text":"Done", 'callback_data':"cb_done"}
        ]

        self.btn_game_menu = [
                {'text':'A', 'callback_data': 'cb_option1'},
                {'text':"B", 'callback_data': 'cb_option2'},
                {'text':'C', 'callback_data': 'cb_option1'},
                {'text':'D', 'callback_data': 'cb_option1'},

            
            
            ]
        
        self.quiz = QuizBot()


    def gen_markup(self, buttons):
        markup = InlineKeyboardMarkup()

        markup.row_width = 4
        for button in buttons:
            markup.add(InlineKeyboardButton(button['text'], callback_data=button['callback_data']))

        return markup


    def callback_query_handler(self, call):


        if call.data == "cb_category":
            fields_list = QuizCategory.list_fields()
            buttons = [{"text": field.title().replace("_", " "), "callback_data": f"cb_category_{field}"} for field in fields_list]
            buttons.append({"text":"<< Back", "callback_data":"cb_back"})

            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="You cliked Yes! Choose an option:",
                reply_markup=self.gen_markup(buttons)
            )

        elif call.data == "cb_difficulty":
            fields_list = QuizDifficulty.list_fields()
            buttons = [{"text": field.title().replace("_", " "), "callback_data": f"cb_difficulty_{field}"} for field in fields_list]
            buttons.append({"text":"<< Back", "callback_data":"cb_back"})

            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="You cliked Yes! Choose an option:",
                reply_markup=self.gen_markup(buttons)
            )


        elif call.data == "cb_quests_num":
            btn = [
                {"text":"<< Back", "callback_data":"cb_back"}
            ]


            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Choose an option a number between 1 and 50:",
                reply_markup=self.gen_markup(btn)
            )

            self.quiz.n_quiz = None


        elif call.data == "cb_done":
            self.quiz.generate_quiz()
            quiz_list = self.quiz.get_new_quiz()
            quiz = quiz_list['quiz']


            buttons = []
            for key,value in quiz_list["questions"].items():
                buttons.append({"text":value, "callback_data":"cb_q_answer_"+key})

                        

            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=quiz,
                reply_markup=self.gen_markup(buttons)
            )
            

        elif call.data[:11] == "cb_q_answer": 
            a_s = self.quiz.handle_answer(call.data[12:])


            if a_s == True:
                self.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=quiz,
                    reply_markup=self.gen_markup([{"text":"New Game", "callback_data":"cb_back"}])
                )


            quiz_list = self.quiz.get_new_quiz()


            if quiz_list == None:
                
                res = ""
                for i,hist in enumerate(self.quiz.quiz_list_hist,start=1):
                    res+=f"\n{i}. {hist['quiz']}\n"
                    res+=f"You answer({hist['emoji']}): {hist['user_answer']}\n"
                    res+=f"Correct answer: {hist['correct_answer']}\n"

                self.bot.send_message(
                    call.message.chat.id, "Game finished!\n"
                        +f"Your score: {self.quiz.user_score}/{self.quiz.n_quiz}\n"+res
                    
                    )

                
            else:

                quiz = quiz_list['quiz']
                buttons = []
                for key,value in quiz_list["questions"].items():
                    buttons.append({"text":value, "callback_data":"cb_q_answer_"+key})

                            
                self.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=quiz,
                    reply_markup=self.gen_markup(buttons)
                )
        
        



        elif call.data == "cb_back":
            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="You cliked Yes! Choose an option:",
                reply_markup=self.gen_markup(self.btn_main_menu)
            )

        elif call.data[:11] == "cb_category":
            self.quiz.category = QuizCategory.get_value(call.data[12:])
            self.btn_main_menu[0]['text'] = "Category: "+call.data[12:].title()

            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="You cliked Yes! Choose an option:",
                reply_markup=self.gen_markup(self.btn_main_menu)
            )

        elif call.data[:13] == "cb_difficulty":
            self.quiz.difficulty = call.data[14:].lower()


            self.btn_main_menu[1]['text'] = "Difficulty: "+call.data[14:].title()

            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="You cliked Yes! Choose an option:",
                reply_markup=self.gen_markup(self.btn_main_menu)
            )




    def message_handler(self, msg):
        if self.quiz.n_quiz is None:
            if msg.text.isdigit() and int(msg.text) >= 1 and int(msg.text) <= 50:
                self.quiz.n_quiz = msg.text
                self.btn_main_menu[2]['text'] = "Amount of Questions: "+self.quiz.n_quiz

                self.bot.send_message(msg.chat.id, "You choose a valid number!", reply_markup=self.gen_markup(self.btn_main_menu))

            else:
                self.bot.send_message(msg.chat.id,"Please choose a valid number between 1 and 50.")

        else:
            self.bot.send_message(msg.chat.id, "Let play an game bro!", reply_markup=self.gen_markup(self.btn_main_menu))



    def start_polling(self):
        self.bot.infinity_polling()



if __name__ == "__main__":
    print("Initializing bot...")

    quiz_bot = MyQuizBot(config.TOKEN)



    @quiz_bot.bot.message_handler(commands=['start'])
    def on_ready(msg):
        quiz_bot.bot.reply_to(msg, "Hello!\n Let's play a game?")

    @quiz_bot.bot.callback_query_handler(func=lambda call:True)
    def callback_query(call):
        quiz_bot.callback_query_handler(call)

    @quiz_bot.bot.message_handler(func=lambda msg: True)
    def message_handler(msg):
        quiz_bot.message_handler(msg)




    quiz_bot.start_polling()
    s.close()




