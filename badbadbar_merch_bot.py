import asyncio
import json
import os
import time
import datetime
import secrets
import csv
import io
import traceback

import pytz

import telegram
from telegram import Update, LabeledPrice, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, PreCheckoutQueryHandler, CallbackContext, CallbackQueryHandler, ContextTypes, TypeHandler

from config import TOKEN
import baydb
import tasks

# ORDER STATES: NEW->WAITING_PAYMENT->WAITING_APPROVE->PAID->READY->DONE
# ORDER STATES: CANCELED

RUB_IN_EUR = 100

PRICES = {
    "flyaga_bad_bar": 3000,
    "flyaga_horse": 3000,
    "flyaga_rectal": 3000,
    "rubashka_S": 8000,
    "rubashka_M": 8000,
    "rubashka_L": 8000,
    "rubashka_XL": 8000,
    "rubashka_2XL": 8000,
    "rubashka_3XL": 8000,
    "rubashka_4XL": 8000,
    "rubashka_5XL": 8000,
    "rain_M_L": 5000,
    "rain_XL_XXL": 5000,
}

NAMES = {
    "flyaga_bad_bar": "фляга с тегом bad bar",
    "flyaga_horse": "фляга с конём",
    "flyaga_rectal": "фляга rectal use only",
    "rubashka_S": "рубашка S",
    "rubashka_M": "рубашка M",
    "rubashka_L": "рубашка L",
    "rubashka_XL": "рубашка XL",
    "rubashka_2XL": "рубашка 2XL",
    "rubashka_3XL": "рубашка 3XL",
    "rubashka_4XL": "рубашка 4XL",
    "rubashka_5XL": "рубашка 5XL",
    "rain_M_L": "дождевик M-L",
    "rain_XL_XXL": "дождевик XL-XXL",
}

orders = baydb.BayDB("orders.json", indexes=["status", "user_id"])

application = None

ADMINS = [53684567]

#, 5068140821, 117711124, 1813518716, 1035477903, 321169743]

async def logging_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        user_id = update.effective_user.id
        user_name = format_user_name(update.effective_user)
    else:
        user_id = "unknown"
        user_name = "Unknown User"

    log_entry = ""
    ekb_timezone = pytz.timezone('Asia/Yekaterinburg')
    timestamp = datetime.datetime.now(tz=ekb_timezone).strftime("%Y-%m-%d %H:%M:%S")

    if update.callback_query:
        callback_data = update.callback_query.data
        log_entry = f"[{timestamp}] {user_id} ({user_name}): {callback_data}\n"
    elif update.effective_message:
        message_text = update.effective_message.text or update.effective_message.caption or "No text"
        if update.effective_message.web_app_data:
            message_text = f"Web app data: {update.effective_message.web_app_data.data}"
        log_entry = f"[{timestamp}] {user_id} ({user_name}): {message_text}\n"
    else:
        log_entry = f"[{timestamp}] {user_id} ({user_name}): Unknown update type\n"

    with open("log/log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

    if user_id != "unknown":
        with open(f"log/log_{user_id}.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)


def calculate_order_price(order_items):
    try:
        order = order_items["order"]
        total_price = int(order_items["total_price"])

        ans = 0
        for item, num in order.items():
            num = int(num)
            if item not in PRICES or num < 0:
                return -1
            ans += PRICES[item] * num

        if total_price != ans:
            return -1

        return ans
    except (LookupError, ValueError):
        return -1


def format_user_name(user):
    try:
        user = user.to_dict()
    except AttributeError:
        pass

    ans = user["first_name"]
    if "last_name" in user:
        ans += " " + user["last_name"]
    if "username" in user:
        ans += " aka " + user["username"]
    return ans


def get_readable_order_details(order):
    order_details = []
    order_items = order.get("order", {})
    for item, num in order_items.get("order", {}).items():
        if num == 0:
            continue
        if num == 1:
            suffix = ""
        else:
            suffix = f" х {num}"

        order_details.append(NAMES.get(item, "неизвестно")+suffix)
    order_details = ", ".join(order_details)
    return order_details


def format_order_details(order, include_timestamp=True, for_admins=False):
    """Format order details for display in messages"""
    order_id = order["id"]
    status = order["status"]
    order_items = order["order"]
    order_user_nick = order["user_nick"]
    order_user_name = order["user_name"]

    order_details = get_readable_order_details(order)
    
    # Calculate total price
    total_price = calculate_order_price(order_items)
    
    if total_price == -1:
        total_price = "∞"

    message = f"<b>Заказ #{order_id}</b>\n"

    if not for_admins and status == "READY":
        message = "<b>Заказ готов к выдаче!</b>\n\n" + message
    
    if for_admins:
        ekb_tz = pytz.timezone('Asia/Yekaterinburg')
        create_datetime = datetime.datetime.fromtimestamp(order["create_time"], tz=pytz.UTC)
        create_time_ekb = create_datetime.astimezone(ekb_tz).strftime("%d-%m-%Y %H:%M:%S")
        message += f"Создан: {create_time_ekb}\n"
        message += f"Создатель: {order_user_name}\n"
        # if "code" in order:
            # message += f"Код получения: {order["code"]}\n"

    total_price_eur = total_price // RUB_IN_EUR

    # message += f"Статус: {status}\n"
    message += f"Детали: {order_details}\n"
    message += f"Сумма: {total_price} ₽ (или {total_price_eur} €).\n\n"

    keyboard = None

    if for_admins:
        if status == "WAITING_APPROVE":
            message += f"Пришёл ли платёж?"
            keyboard = [[
                InlineKeyboardButton("❌ Не оплачен", callback_data=f"admin_not_paid_{order_id}"),
                InlineKeyboardButton("✅ Оплачен", callback_data=f"admin_paid_{order_id}")
            ]]
        elif status == "PAID":
            keyboard = [[
                InlineKeyboardButton("🙈 Скрыть", callback_data=f"admin_hide_{order_id}"),
                InlineKeyboardButton("📦 Готов к выдаче", callback_data=f"admin_ready_{order_id}")
            ]]
        elif status == "READY":
            message += f"Заказ готов к выдаче, код получения <b>{order.get("code", "НЕТ")}</b>"
            keyboard = [[
                InlineKeyboardButton("🏁 Выдать", callback_data=f"admin_finish_{order_id}"),
            ]]
        elif status == "DONE":
            message += f"Заказ выдан"

    else:
        if status == "NEW":
            message += f"Ура, всё выбрано! Теперь осталось оплатить заказ.\n\nПеред оплатой, пожалуйста, проверь правильность своего заказа.\nЕсли всё верно — жми «Оплатить»."
            keyboard = [[
                InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_{order_id}"),
                InlineKeyboardButton("🎟 Оплатить", callback_data=f"pay_{order_id}")
            ]]
        elif status == "WAITING_PAYMENT":
            message += f"Совершая перевод, ты подтверждаешь, что ознакомлен(а) с описанием товаров и понимаешь: мерч нельзя вернуть или обменять, ведь мы делаем его специально под заказ 🎁\n\nhttps://www.tbank.ru/cf/2eOMJ7HDzYa\n\nВ описании платежа укажи «<b>{order_user_nick}</b>», чтобы мы знали от кого он."
            keyboard = [[
                InlineKeyboardButton("🔙 Назад", callback_data=f"back_to_new_{order_id}"),
                InlineKeyboardButton("💸 Оплатил", callback_data=f"paid_{order_id}")
            ]]
        elif status == "WAITING_APPROVE":
            message += f"Ожидаем поступления платежа, если не переводили деньги нажмите 'назад'"
            keyboard = [[
                InlineKeyboardButton("🔙 Назад", callback_data=f"not_paid_{order_id}")
            ]]
        elif status == "PAID":
            message += f"Заказ оплачен. Мы напишем, когда его можно будет забрать 📦."
        elif status == "READY":
            message += f"Код получения <b>{order.get("code", "НЕТ")}</b>.\n\nПишите <a href='https://t.me/IamALENO4KA'>Алёне</a>. С ней можно договориться о самовывозе, курьере за счёт получателя или другом способе"
        elif status == "DONE":
            message += f"Заказ выдан"

    markup = None
    if keyboard:
        markup = InlineKeyboardMarkup(keyboard)
    
    return message, markup


async def send_message_to_admins(text, markup=None, parse_mode="HTML"):
    for admin_id in ADMINS:
        try:
            await application.bot.send_message(admin_id, text=text, reply_markup=markup, parse_mode=parse_mode, disable_web_page_preview=True)
        except Exception as e:
            print(e)
            pass


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Notify admins about errors during message processing."""
    # Get error details
    error = context.error

    # Get user information
    if update and update.effective_user:
        user_id = update.effective_user.id
        user_name = format_user_name(update.effective_user)
    else:
        user_id = "unknown"
        user_name = "Unknown User"

    # Get the user's original input that triggered the error
    user_input = "Unknown input"
    if update:
        if update.message:
            user_input = update.message.text or update.message.caption or "No text"
        elif update.callback_query:
            user_input = f"Callback: {update.callback_query.data}"
        elif update.effective_message and update.effective_message.web_app_data:
            user_input = f"Web app data: {update.effective_message.web_app_data.data}"

    # Format error message
    error_message = f"❌ EXCEPTION: {str(error)}\nUser: {user_id} ({user_name})\nUser's message: {user_input}"


    # Log to file
    ekb_timezone = pytz.timezone('Asia/Yekaterinburg')
    timestamp = datetime.datetime.now(tz=ekb_timezone).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ERROR: {error_message}\n"

    try:
        with open("log/errors.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
            f.write("".join(traceback.format_exception(error)))
    except Exception as e:
        print(f"Failed to write to error log: {e}")

    # Notify admins
    await send_message_to_admins(error_message)



async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await update.message.reply_html(text="Слишком поздно, время приёма заказов подошло к концу")
    # return

    user_id = update.effective_user.id
    user_name = format_user_name(update.effective_user)

    data = json.loads(update.effective_message.web_app_data.data)

    data["orig_currency"] = data["currency"]

    if data.get("currency") == "EUR":
        data["currency"] = "RUB"
        data["total_price"] *= RUB_IN_EUR
    elif data.get("currency") == "RUB":
        pass
    else:
        await update.message.reply_html(text="Неизвестная валюта заказа")
        return

    if calculate_order_price(data) == 0:
        await update.message.reply_html(text="Оформить заказ на 0 рублей нельзя 🤭\n\nПроверь, добавил(а) ли ты что-то в корзину.\nЕсли нет — самое время это сделать!")
        return

    if calculate_order_price(data) == -1:
        await update.message.reply_html(text="Что-то не так с переданными данными")

        await send_message_to_admins(f"Плохие данные для заказа {user_id} {user_name}: {str(data)[:1000]}", parse_mode=None)
        return


    order = {}
    order["user_id"] = user_id
    order["user_nick"] = update.effective_user.username or "no_nick"
    order["user_name"] = user_name
    order["order"] = data
    order["status"] = "NEW"
    order["create_time"] = int(time.time())

    order = orders.append(order)
    
    message, markup = format_order_details(order)

    await update.message.reply_html(text=message, reply_markup=markup, disable_web_page_preview=True)


async def admin_get_paid_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_html(text="Доступ запрещён")
        return

    paid_orders = list(orders.where(status="PAID"))

    if not paid_orders:
        await update.message.reply_text("Пока нет заказов.")
        return

    for order in paid_orders:
        status = order["status"]
        order_id = order["id"]

        message, markup = format_order_details(order, for_admins=True)
        await update.message.reply_text(message, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


async def admin_get_wait_approval_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_html(text="Доступ запрещён")
        return

    paid_orders = list(orders.where(status="WAITING_APPROVE"))

    if not paid_orders:
        await update.message.reply_text("Пока нет заказов.")
        return

    for order in paid_orders:
        status = order["status"]
        order_id = order["id"]

        message, markup = format_order_details(order, for_admins=True)
        await update.message.reply_text(message, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


async def admin_get_ready_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_html(text="Доступ запрещён")
        return

    ready_orders = list(orders.where(status="READY"))

    if not ready_orders:
        await update.message.reply_text("Пока нет заказов.")
        return

    for order in ready_orders:
        status = order["status"]
        order_id = order["id"]

        message, markup = format_order_details(order, for_admins=True)
        await update.message.reply_text(message, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


async def admin_get_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_html(text="Доступ запрещён")
        return

    # Генерируем CSV-файл
    csv_data = generate_orders_csv()

    # Создаем имя файла с временной меткой
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"orders_{timestamp}.csv"

    # Отправляем файл прямо из памяти
    csv_bytes = csv_data.encode('utf-8')
    input_file = io.BytesIO(csv_bytes)
    input_file.name = filename

    await update.message.reply_document(
        document=input_file,
        filename=filename,
        caption="Экспорт всех заказов"
    )


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_orders = list(orders.where(user_id=user_id))
    
    user_orders = [order for order in user_orders if order["status"] != "CANCELED"]
    
    if not user_orders:
        await update.message.reply_text("У вас пока нет заказов.")
        return
    
    for order in user_orders:
        status = order["status"]
        order_id = order["id"]
        
        message, markup = format_order_details(order)
        await update.message.reply_text(message, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


async def admin_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    query = update.callback_query
    data = query.data

    try:
        action, order_id = data.rsplit("_", 1)
        order_id = int(order_id)
    except ValueError:
        await query.answer("Некорректный формат данных")
        return

    order = orders.get(order_id)

    if not order:
        await query.answer("Ошибка: заказ не найден")
        return

    status = order["status"]
    order_user_id = order["user_id"]

    if action in ["admin_paid", "admin_not_paid"]:
        if status in ["PAID"]:
            await query.answer(f"Заказ уже подтвердил кто-то другой")
            return

        if status not in ["NEW", "WAITING_PAYMENT", "WAITING_APPROVE"]:
            await query.answer(f"Плохое состояние заказа: {status}")
            return

        if action == "admin_paid":
            order = orders.update(order_id, status="PAID")
            await context.bot.send_message(order_user_id, f"Заказ {order_id} оплачен.\nМы напишем, когда его можно будет забрать 🙌", disable_web_page_preview=True)

            message, markup = format_order_details(order, include_timestamp=False, for_admins=True)
            await query.edit_message_text(message, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)

        elif action == "admin_not_paid":
            order = orders.update(order_id, status="WAITING_PAYMENT")
            await context.bot.send_message(order_user_id, f"Мы не нашли ваш платёж по заказу {order_id}. Если вы заплатили, напишите @IamALENO4KA или @bay3255", parse_mode="HTML", disable_web_page_preview=True)

            await query.edit_message_text(text=f"Заказ {order_id}: вы не нашли платёж пользователя. Ему выслано отовещение об этом", parse_mode="HTML", disable_web_page_preview=True)
    elif action in ["admin_ready", "admin_hide"]:
        if status not in ["PAID", "READY"]:
            await query.answer(f"Плохое состояние заказа: {status}")
            return

        if action == "admin_ready":
            code = f"{secrets.randbelow(10000):04}"
            order = orders.update(order_id, status="READY", code=code)

            user_message, user_markup = format_order_details(order, include_timestamp=False, for_admins=False)
            await context.bot.send_message(order_user_id, user_message, reply_markup=user_markup, parse_mode="HTML", disable_web_page_preview=True)

            admin_message, admin_markup = format_order_details(order, include_timestamp=False, for_admins=True)
            await query.edit_message_text(text=admin_message, reply_markup=admin_markup, parse_mode="HTML", disable_web_page_preview=True)

        elif action == "admin_hide":
            await query.message.delete()
    elif action in ["admin_finish"]:
        if status not in ["READY", "DONE"]:
            await query.answer(f"Плохое состояние заказа: {status}")
            return

        order = orders.update(order_id, status="DONE")

        user_message, user_markup = format_order_details(order, include_timestamp=False, for_admins=False)
        await context.bot.send_message(order_user_id, user_message, reply_markup=user_markup, parse_mode="HTML", disable_web_page_preview=True)

        message, markup = format_order_details(order, include_timestamp=False, for_admins=True)
        await query.edit_message_text(text=message, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    query = update.callback_query
    data = query.data

    action, order_id = data.rsplit("_", 1)
    order_id = int(order_id)
    order = orders.get(order_id)

    if action.startswith("admin_"):
        if user_id not in ADMINS:
            await query.answer("Ошибка: доступ запрещён")
            return

        await admin_button_callback(update, context)
        return


    action_to_cur_state = {
        "pay": "NEW",
        "cancel": "NEW",
        "back_to_new": "WAITING_PAYMENT",
        "paid": "WAITING_PAYMENT",
        "not_paid": "WAITING_APPROVE",
    }

    action_to_next_state = {
        "pay": "WAITING_PAYMENT",
        "cancel": "CANCELED",
        "back_to_new": "NEW",
        "paid": "WAITING_APPROVE",
        "not_paid": "WAITING_PAYMENT",
    }

    if not order:
        await query.answer("Ошибка: заказ не найден")
        return

    if order["user_id"] != user_id:
        await query.answer("Ошибка: вы можете управлять только своими заказами")
        return


    if order["status"] != action_to_cur_state[action]:
        await query.answer(f"Ошибка: действие недоступно для заказа в статусе {order['status']}")
        return

    # if action in ["pay", "paid"]:
    #     await query.answer(f"Ошибка: время приёма заказов подошло к концу")
    #     return

    next_state = action_to_next_state[action]

    order = orders.update(order_id, status=next_state)
    await query.answer()

    if action == "cancel":
        await query.edit_message_text(text=f"Заказ #{order_id} отменен.", parse_mode="HTML", disable_web_page_preview=True)
        return

    if action == "paid":
        message, markup = format_order_details(order, include_timestamp=False, for_admins=True)
        await send_message_to_admins(message, markup=markup)


    message, markup = format_order_details(order, include_timestamp=False)
    await query.edit_message_text(text=message, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


async def start_webserver(app):
    """Функция для возможной будущей интеграции с веб-сервером"""
    pass


def generate_orders_csv():
    """Генерирует CSV-файл со всеми заказами, сгруппированными по статусу"""
    # Создаем буфер для записи данных
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)

    # Заголовки столбцов
    headers = ["Номер", "Заказ", "Статус", "Пользователь", "Имя пользователя", "Стоимость", "Дата создания", "Код получения"]
    writer.writerow(headers)

    # Получаем все заказы
    all_orders = [orders.get(order_id) for order_id in orders.keys()]

    # Группируем заказы по статусу
    orders_by_status = {}
    for order in all_orders:
        status = order["status"]
        if status not in orders_by_status:
            orders_by_status[status] = []
        orders_by_status[status].append(order)

    # Сортировка статусов в логическом порядке
    status_order = ["NEW", "WAITING_PAYMENT", "WAITING_APPROVE", "PAID", "READY", "DONE", "CANCELED"]

    # Проходим по статусам в установленном порядке
    for status in status_order:
        if status not in orders_by_status:
            continue

        # Добавляем заголовок группы
        writer.writerow([])
        writer.writerow(["", f"===== СТАТУС: {status} ====="])
        writer.writerow([])

        # Сортируем заказы внутри группы по времени создания (от новых к старым)
        status_orders = orders_by_status[status]
        status_orders.sort(key=lambda x: x.get("create_time", 0), reverse=True)

        sum_of_orders = {}
        sum_price = 0

        # Добавляем данные в CSV
        for order in status_orders:
            order_id = order["id"]
            user_nick = order["user_nick"]
            user_name = order["user_name"]
            order_items = get_readable_order_details(order)
            total_price = calculate_order_price(order["order"])

            # Форматируем дату создания
            create_time = order.get("create_time", 0)
            if create_time:
                ekb_tz = pytz.timezone('Asia/Yekaterinburg')
                create_datetime = datetime.datetime.fromtimestamp(create_time, tz=pytz.UTC)
                create_time_ekb = create_datetime.astimezone(ekb_tz).strftime("%Y-%m-%d %H:%M:%S")
            else:
                create_time_ekb = "Неизвестно"

            code = order.get("code", "")

            # Записываем строку
            writer.writerow([order_id, order_items, status, user_nick, user_name, total_price, create_time_ekb, code])

            for item, count in order["order"]["order"].items():
                if item not in sum_of_orders:
                    sum_of_orders[item] = 0

                sum_of_orders[item] += count

            sum_price += total_price

        writer.writerow([
            "СУММА", get_readable_order_details({"order":{"order": sum_of_orders}}),
            "", "", "", sum_price
            ])



    # Получаем данные из буфера
    csv_buffer.seek(0)
    csv_data = csv_buffer.getvalue()

    return csv_data


async def admin_get_order_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для получения заказа по ID для администраторов"""
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_html(text="Доступ запрещён")
        return

    # Получаем текст сообщения и проверяем, является ли он числом
    message_text = update.message.text.strip()
    if not message_text.isdigit():
        return False  # Не обрабатываем не числовые сообщения

    order_id = int(message_text)
    order = orders.get(order_id)

    if not order:
        await update.message.reply_html(text=f"Заказ #{order_id} не найден")
        return True

    message, markup = format_order_details(order, for_admins=True)
    await update.message.reply_html(text=message, reply_markup=markup, disable_web_page_preview=True)
    return True


async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Если пользователь админ и сообщение - число, пробуем найти заказ
    if user_id in ADMINS:
        was_handled = await admin_get_order_by_id(update, context)
        if was_handled:
            return

    await update.message.reply_text(
        "Используйте кнопки для взаимодействия с ботом или введите /start для начала работы.",
        disable_web_page_preview=True)


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # if user_id in [1239687503]:
    #     keyboard_buttons = [[
    #         InlineKeyboardButton("В магазин 🛒", web_app=WebAppInfo(url="https://dmmbot.alexbers.com/webapp/merch/dist_personal")),
    #         InlineKeyboardButton("Мои заказы 🛍"),
    #     ], [InlineKeyboardButton("Приклеить ачивку ℹ️"),]
    #     ]
    # if user_id in [48276621, 462122850]:
    if user_id in []:
        pass
        # keyboard_buttons = [[
        #     InlineKeyboardButton("В магазин 🛒", web_app=WebAppInfo(url="https://dmmbot.alexbers.com/webapp/merch/dist_personal")),
        #     InlineKeyboardButton("Мои заказы 🛍"),
        # ], [
        #     InlineKeyboardButton("Приклеить ачивку ℹ️")
        # ]]
    else:
        keyboard_buttons = [[
            InlineKeyboardButton("В магазин 🛒", web_app=WebAppInfo(url="https://dmmbot.alexbers.com/webapp_bad/dist")),
            InlineKeyboardButton("Мои заказы 🛍"),
        ]]

    # Если пользователь - администратор, добавляем дополнительную кнопку
    if user_id in ADMINS:
        admin_buttons = [[
                        # InlineKeyboardButton("Неподтверждённые ⏳"),
                        InlineKeyboardButton("Оплаченные 💵"),
                        InlineKeyboardButton("Готовые к выдаче 📦"),
                        InlineKeyboardButton("Выгрузить заказы 📊")]]
        keyboard_buttons.extend(admin_buttons)

    await update.message.reply_text(
        "Сәлем! Здесь ты сможешь купить мерч Bad Bar.\n\n"
        "Прежде, чем ты заглянешь в бота, хотим напомнить, что, купив наш мерч, ты инвестируешь в сомнительные развлечения!\n\n"
        "Жми «В магазин» — и поехали.",
        parse_mode="html",
        reply_markup=ReplyKeyboardMarkup(keyboard_buttons, resize_keyboard=True),
        disable_web_page_preview=True
    )


async def start_approver(application):
    asyncio.create_task(tasks.pay_approver(bot=application.bot, orders=orders))


def main():
    os.makedirs("log", exist_ok=True)

    global application
    application = Application.builder().token(TOKEN).post_init(start_approver).build()

    # Add middleware for logging
    application.add_handler(TypeHandler(Update, logging_middleware), group=-1)

    # Add regular handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    application.add_handler(MessageHandler(filters.Regex("^Мои заказы 🛍$"), my_orders))
    application.add_handler(MessageHandler(filters.Regex("^Неподтверждённые ⏳$"), admin_get_wait_approval_orders))
    application.add_handler(MessageHandler(filters.Regex("^Оплаченные 💵$"), admin_get_paid_orders))
    application.add_handler(MessageHandler(filters.Regex("^Готовые к выдаче 📦$"), admin_get_ready_orders))
    application.add_handler(MessageHandler(filters.Regex("^Выгрузить заказы 📊$"), admin_get_orders))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT, handle_other_messages))

    # Add error handler to notify admins about exceptions
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
