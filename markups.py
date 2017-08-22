# -*- coding: utf-8 -*-?
import telebot
import temp, base
from const import cities


def start(id):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_user = telebot.types.InlineKeyboardButton(text="Продавать!", callback_data='celler_panel')
    btn_celler = telebot.types.InlineKeyboardButton(text="Покупать!", callback_data='client_panel')
    markup.add(btn_celler, btn_user)
    if base.is_admin(id):
        btn_admin = telebot.types.InlineKeyboardButton(text="Админ-панель", callback_data="admin_panel")
        markup.add(btn_admin)
    return markup


def show_types():
    markup = telebot.types.InlineKeyboardMarkup()
    for key in base.give_menu():
        button = telebot.types.InlineKeyboardButton(text=key, callback_data=key)
        markup.add(button)
    #btn_registraciy = telebot.types.InlineKeyboardButton(text="Регистрация покупателей отходов",
         #                                                callback_data='registraciy_panel')
    #markup.add(btn_registraciy)
    return markup


def show_cities():
    markup = telebot.types.InlineKeyboardMarkup()
    for city in cities:
        button = telebot.types.InlineKeyboardButton(text=city, callback_data=city)
        markup.add(button)
    return markup


def make_bill(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    markup.row("Меню")
    markup.row("Регистрация")
    if base.is_seller(user_id):
        markup.row("Панель покупателя")
    return markup


def return_to_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    markup.row("Меню")
    #markup.row("Регистрация")
    if base.is_seller(user_id):
        markup.row("Панель покупателя")
    if base.is_admin(user_id):
        markup.row("Админ-панель")
    return markup


def is_seller():
    markup = telebot.types.InlineKeyboardMarkup()
    butquest = telebot.types.InlineKeyboardButton('Зайти как покупатель?', callback_data='.')
    btn_y = telebot.types.InlineKeyboardButton('Yes', callback_data='&Yes')
    btn_n = telebot.types.InlineKeyboardButton('No', callback_data='&No')
    markup.row(butquest)
    markup.row(btn_n, btn_y)
    return markup


def add(id):
    markup = base.item_finder(id).get_desc2()
    print('id : ' + str(id))
    #butp = telebot.types.InlineKeyboardButton('+', callback_data='+'+str(id))
    #butm = telebot.types.InlineKeyboardButton('-', callback_data='-'+str(id))
    #markup.row(butp, butm)
    #print('callback.data : \n' + str(butp.callback_data[0]) + '\n' + str(int(butp.callback_data[1:])))
    return markup


def concern():
    markup = telebot.types.InlineKeyboardMarkup()
    yesb = telebot.types.InlineKeyboardButton(text='Да', callback_data='#Yes')
    nob = telebot.types.InlineKeyboardButton(text='Нет', callback_data='#No')
    markup.add(yesb,nob)
    return markup


def add_paypal_id():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    tb = telebot.types.InlineKeyboardButton(text='Необходимо добавить ваш PayPal login', callback_data='.')
    tb2 = telebot.types.InlineKeyboardButton(text='Введите ваш логин, начиная сообщение с знака \'%\' ', callback_data='.')
    markup.add(tb,tb2)
    return markup


def edit():
    markup = telebot.types.InlineKeyboardMarkup()
    add_item = telebot.types.InlineKeyboardButton(text="Добавить заявку", callback_data='add_item')
    #delete_item = telebot.types.InlineKeyboardButton(text="Удалить заявку", callback_data='delete_item')
    add_kat = telebot.types.InlineKeyboardButton(text="Добавить категорию", callback_data='add_kat')
    #delete_kat = telebot.types.InlineKeyboardButton(text="Удалить категорию", callback_data='delete_kat')
    markup.row(add_kat, add_item)
    #markup.row(delete_kat, delete_item)

    return markup


def add_item():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for category in base.give_menu():
        markup.add(category)
    return markup


def add_city():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for city in cities:
        markup.add(city)
    return markup

def delete_item(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    for item in base.find_users_items(user_id):
        btn_item = telebot.types.InlineKeyboardButton(text=item[2], callback_data="^" + str(item[0]))
        markup.add(btn_item)
    btn_menu = telebot.types.InlineKeyboardButton(text="Вернуться в админ-панель", callback_data="celler_panel")
    markup.add(btn_menu)
    return markup

#
# def delete_kat():
#     markup = telebot.types.InlineKeyboardMarkup()
#     for key in base.give_menu():
#         button = telebot.types.InlineKeyboardButton(text=key, callback_data="?"+key)
#         markup.add(button)
#     btn_menu = telebot.types.InlineKeyboardButton(text="Вернуться в админ-панель", callback_data="celler_panel")
#     markup.add(btn_menu)
#     return markup




def remove_reply_keyboard():
    markup = telebot.types.ReplyKeyboardRemove()
    return markup

def pay_button():
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text="Оплатил", callback_data="paid")
    markup.row(btn)
    return markup

def admin():
    markup = telebot.types.InlineKeyboardMarkup()
    btn_send = telebot.types.InlineKeyboardButton(text="Рассылка", callback_data="send")
    btn_stat = telebot.types.InlineKeyboardButton(text="Статистика", callback_data="statistic")
    btn_back = telebot.types.InlineKeyboardButton(text="Меню", callback_data="menu")
    markup.add(btn_send)
    markup.add(btn_stat)
    markup.add(btn_back)
    return markup