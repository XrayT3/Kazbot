# -*- coding: utf-8 -*-?
import os
import sqlite3
import telebot
import time
import urllib.request as urllib
import logging


import requests.exceptions as r_exceptions
from requests import ConnectionError

import const, base, markups, files, temp, config

bot = telebot.TeleBot(const.token)
uploaded_items = {}

logger = logging.getLogger('bot.py')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.FileHandler('logs.log')
# create formatter
formatter = logging.Formatter('-----------------------------------------------------------\n'
                              '%(levelname)s %(asctime)s - %(name)s: %(message)s\n'
                              '%(funcName)s - %(lineno)d')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

#TODO


# Обработка /start команды - ветвление пользователей на покупателя и продавца
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, const.welcome_celler, reply_markup=markups.start(message.chat.id))


# Выдача меню с типами товаров
@bot.message_handler(regexp='Меню')
def client_panel(message):
    bot.send_message(message.chat.id, 'Выберите:', reply_markup=markups.start(message.chat.id))

@bot.callback_query_handler(func = lambda call: call.data == "menu")
def client_panel(call):
    bot.edit_message_text("Меню", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markups.start(call.message.chat.id))


@bot.callback_query_handler(func=lambda call: call.data == 'celler_panel')
def client_panel(call):
    if base.is_seller(call.message.chat.id):
        bot.edit_message_text(const.welcome_client, chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markups.show_types())
    else:
        sent = bot.send_message(call.message.chat.id, "Пожалуйста, введите свой номер телефона",
                                reply_markup=markups.return_to_menu(call.message.chat.id))
        bot.register_next_step_handler(sent, registracy_panel_seller)
        #base.add_client(call.message)


# Запуск обработчика продавцов
@bot.message_handler(regexp="Панель покупателя")
def celler_panel(message):
    if base.is_in_base(message.chat.id):
        bot.send_message(message.chat.id, "Раздел покупателей отходов", parse_mode='Markdown', reply_markup=markups.edit())
    else:

        registraciy_panel(message)


@bot.callback_query_handler(func=lambda call: call.data == "client_panel")
def celler_panel1(call):
    if base.is_in_base(call.message.chat.id):
        bot.send_message(call.message.chat.id, "Раздел покупателей отходов", parse_mode='Markdown', reply_markup=markups.edit())
    else:

        registraciy_panel(call.message)
@bot.callback_query_handler(func = lambda call: call.data == "admin_panel")
def admin(call):
    bot.edit_message_text("Админ-панель", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markups.admin())

@bot.message_handler(regexp="Админ-панель")
def admin(message):
    if not base.is_admin(message.chat.id):
        bot.send_message(message.chat.id, "Нет прав доступа")
    else:
        bot.send_message(message.chat.id, "Админ-панель",
                         reply_markup=markups.admin())

@bot.callback_query_handler(func = lambda call: call.data == "send")
def send(call):
    msg = bot.send_message(call.message.chat.id, "Введите текст")
    const.user_adding_item_step.update([(call.message.chat.id, "Send")])


@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "Send")
@bot.message_handler(content_types=['photo'])
def send_all(message):
    head = "!!! Рассылка для всех пользователей !!!\n"
    tail = "\n---------------------------------------"
    try:
        if base.get_user_step(message.chat.id) == "Send":
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("temp.jpg", 'wb+') as new_file:
                new_file.write(downloaded_file)
            for id in base.get_all_ids():
                bot.send_message(id, head)
                bot.send_photo(message.chat.id, photo=open("temp.jpg", 'rb'))

            bot.send_message(message.chat.id, "Ваша рассылка отправлена!", reply_markup=markups.admin())
    except:
        for id in base.get_all_ids():
            bot.send_message(id, head + message.text + tail)
        bot.send_message(message.chat.id, "Ваша рассылка отправлена!", reply_markup=markups.admin())


@bot.callback_query_handler(func = lambda call: call.data == "statistic")
def statistics(call):
    msg = "Всего продавцов: {clients}\nВсего покупателей: {users}".format(clients = base.count_clients(), users = base.count_users())
    bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markups.admin())

# Запуск реистрации покупателей.
#@bot.message_handler(regexp='Регистрация')
def registraciy_panel(message):
    sent = bot.send_message(message.chat.id, "Введите данные компании (Название, БИН)",
                            reply_markup=markups.return_to_menu(message.chat.id))
    bot.register_next_step_handler(sent, hello)

def registracy_panel_seller(message):
    base.add_client(message)
    bot.send_message(248835526, 'Новая заявка на регистрацию. {name} '.format(name=message.text) + ' id= ' + str(message.from_user.id))
    bot.send_message(message.chat.id, 'Выберите категорию:', reply_markup=markups.show_types())


def hello(message):
    base.add_user(message)
    bot.send_message(248835526, 'Новая заявка на регистрацию. {name} '.format(name=message.text) + ' id= ' + str(message.from_user.id))
    bot.send_message(message.chat.id, "Qiwi +70000000000\n"\
                                    "Карта 0000 0000 0000 0000\n"\
                                    "Комментарий к платежу {id}".format(id = message.chat.id),
                                                          reply_markup=markups.pay_button())


@bot.callback_query_handler(func = lambda call: call.data == "paid")
def move_back(call):
    bot.edit_message_text("Раздел покупателей отходов", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.edit())

@bot.callback_query_handler(func=lambda call: call.data in base.give_menu())
def show_cities(call):
    const.users_choice[call.message.message_id] = call.data
    bot.edit_message_text("Выберите нужный город", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.show_cities())



# Отображение товаров и занесение их в кэш
@bot.callback_query_handler(func=lambda call: call.data in const.cities)
def show_items(call):
    for item in base.type_finder(const.users_choice[call.message.message_id], call.data):
        key = item.get_desc2()
        # callback_button = telebot.types.InlineKeyboardButton(text='Buy', callback_data=str(item.id))
        uploaded_items[str(item.id)] = 0
        print(uploaded_items)
        # key.row(callback_button)

        try:
            url = item.url
            photo = open("temp.jpg", 'w')  # Инициализация файла
            photo.close()
            photo = open("temp.jpg", 'rb')
            urllib.urlretrieve(url, "temp.jpg")
            bot.send_photo(chat_id=call.message.chat.id, photo=photo)
            photo.close()
            os.remove("temp.jpg")
        except Exception:
            bot.send_message(call.message.chat.id, item.description, reply_markup=key)
    bot.send_message(call.message.chat.id, "Удачных покупок!", reply_markup=markups.return_to_menu(call.message.chat.id))


# Отображение текущей корзины и вопрос о совершении транзакции
@bot.message_handler(regexp="Оформить заказ")
def transaction(message):
    print(uploaded_items)
    items = uploaded_items
    while items:
        print('processing names...')
        item = items.popitem()
        if item[1] > 0:
            it = base.item_finder(item[0])
            message1 = 'Заказ: ' + str(it.description) + ' Покупатель' + ' : ' + '@' + str(it.seller)
            bot.send_message(message.chat.id, message1)


# Запуск обработки транзакции


@bot.callback_query_handler(func=lambda call: call.data == '#Yes')
def transaction(call):
    message = "К ожалению, онлайн-системы оплаты пока что находятся в разработке.\n" \
              "Вместо этого, вы можете обсудить средства перевода денег с продавцом товаров\n"
    print(uploaded_items)
    items = uploaded_items
    while items:
        print('processing names...')
        item = items.popitem()
        if item[1] > 0:
            it = base.item_finder(item[0])
            message += str(it.company) + str(it.name) + ' : ' + '@' + str(it.seller)
            bot.send_invoice(call.message.chat.id, it.name, it.description)
            bot.send_invoice()
    bot.edit_message_text(message, call.message.chat.id, call.message.message_id)


# Обработка первой покупки товара
@bot.callback_query_handler(func=lambda call: call.data in uploaded_items)
def callback_handler(call):
    print('uploaded_items : ' + str(uploaded_items))
    print('callback_handler.call.data = ' + str(call.data))
    #markup = markups.add(call.data)
    #numb = telebot.types.InlineKeyboardButton(str(uploaded_items.get(call.data)), callback_data='.')
    #markup.add(numb)
    #bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    items = uploaded_items
    it = base.item_finder(call.data)
    message1 = 'Заказ: ' + str(it.description) + ' Покупатель' + ' : ' + '@' + str(it.seller)
    bot.send_message(call.message.chat.id, message1)


# Добавление ещё одной еденицы товара в корзину


@bot.callback_query_handler(func=lambda call: str(call.data[0]) == '+')
def handle_plus(call):
    try:
        uploaded_items[str(int(call.data[1:]))] += 1
    except KeyError as e:
        config.log(Error=e, text='WRONG_KEY')
    markup = markups.add(call.data[1:])
    numb = telebot.types.InlineKeyboardButton(str(uploaded_items.get(str(int(call.data[1:])))), callback_data='.')
    markup.row(numb)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    print('uploaded items = ' + str(uploaded_items))


# Удаление единицы товара из корзины


@bot.callback_query_handler(func=lambda call: str(call.data[0]) == '-')
def handle_minus(call):
    try:
        if uploaded_items[str(int(call.data[1:]))]:
            uploaded_items[str(int(call.data[1:]))] -= 1
    except KeyError as e:
        config.log(Error=e, text='WRONG_KEY')
    if uploaded_items[str(int(call.data[1:]))] == 0:
        key = (base.item_finder(call.data[1:])).get_desc2()

        key.row_width = 1
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=key)
        return
    markup = markups.add(call.data[1:])
    numb = telebot.types.InlineKeyboardButton(str(uploaded_items.get(str(int(call.data[1:])))), callback_data='.')
    markup.row(numb)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    print('uploaded items = ' + str(uploaded_items))
    return


# @bot.message_handler(content_types=['document'])
# def handle_xl(message):
#     files.get_xls_data(bot.get_file(message.document.file_id), message.from_user.id, message.from_user.username)


# Добавление категории
@bot.callback_query_handler(func=lambda call: call.data == 'add_kat')
def handle_add_kat(call):
    sent = bot.send_message(call.message.chat.id, "Введите название категории", reply_markup=markups.return_to_menu(call.message.chat.id))
    bot.register_next_step_handler(sent, base.add_kat)


# Удаление категории
@bot.callback_query_handler(func=lambda call: call.data == 'delete_kat')
def handle_delete_kat(call):
    bot.edit_message_text("Выберите категорию для удаления", call.message.chat.id,
                          call.message.message_id, reply_markup=markups.delete_kat())


@bot.callback_query_handler(func=lambda call: call.data[0] == '?')
def handle_delete_this_kat(call):
    db = sqlite3.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("DELETE FROM categories WHERE name = ?", (str(call.data[1:]),))
    db.commit()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_kat())

    print('deleted')


# дальше идет какое-то дерьмо


# Добавление товара.


# Выбор типа товара
@bot.callback_query_handler(func=lambda call: call.data == 'add_item')
def handle_add_item_type(call):
    new_item = temp.Item()
    const.new_items_user_adding.update([(call.message.chat.id, new_item)])
    sent = bot.send_message(call.message.chat.id, "Выберите тип товара:", reply_markup=markups.add_item())
    bot.register_next_step_handler(sent, base.add_item_kategory)
    const.user_adding_item_step.update([(call.message.chat.id, "City")])

@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "City")
def confirm_city(message):
    sent = bot.send_message(message.chat.id, "Выберите город", reply_markup=markups.add_city())
    bot.register_next_step_handler(sent, base.add_item_city)
    const.user_adding_item_step.update([(message.chat.id, "Enter name")])

# Ввод наименования товара
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "Enter name")
def handle_add_item_description(message):
    sent = bot.send_message(message.chat.id, "Введите описание")
    bot.register_next_step_handler(sent, base.add_item_description)
    const.user_adding_item_step[message.chat.id] = "End"


# Конец добавления товара
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "End")
def handle_add_item_end(message):
    bot.send_message(message.chat.id, "Добавлено!\n Меню:", reply_markup=markups.show_types())
    const.user_adding_item_step.pop(message.chat.id)


# Удаление товара
@bot.callback_query_handler(func=lambda call: call.data == 'delete_item')
def handle_delete_item(call):
    bot.edit_message_text("Выберите товар для удаления", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_item(call.message.chat.id))


@bot.callback_query_handler(func=lambda call: call.data[0] == '^')
def handle_delete_from_db(call):
    db = sqlite3.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (str(call.data[1:])))
    db.commit()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_item(call.message.chat.id))
    print('deleted')


# Сохранение PayPal логина продавца


# @bot.message_handler(content_types=['text'], func=lambda message: message.text[0] == '%' and config.goRegister == True)
# def handle_paypal_login(message):
#     if not base.is_seller(message.from_user.id):
#         base.add_client(message)


@bot.callback_query_handler(func=lambda call: call.data[0] == '$')
def give_desc(call):
    # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=item.swap_desc())
    bot.edit_message_text("Здесь текст", call.message.chat.id, call.message.message_id, )


# Запуск бота


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except ConnectionError as expt:
        config.log(Exception='HTTP_CONNECTION_ERROR', text=expt)
        logger.error("HTTP_CONNECTION_ERROR\n" + str(expt))
        print('Connection lost..')
        time.sleep(30)
        continue
    except r_exceptions.Timeout as exptn:
        config.log(Exception='HTTP_REQUEST_TIMEOUT_ERROR', text=exptn)
        time.sleep(5)
        continue
    except Exception as e:
        logger.error(str(e))
