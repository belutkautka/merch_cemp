import asyncio
import logging
import json
import datetime
import time
from typing import Dict, List, Set


import aiohttp
import pytz

from config import PAYMENT_URL

# Константы и настройки
TASK_TIMEOUT = 16
CONNECT_TIMEOUT = 5
PAUSE = 60  # Опрашиваем сайт раз в минуту
MAX_PAYMENT_AGE_HOURS = 12  # Максимальный возраст платежа в часах

# Настройка логирования
log = logging.getLogger('tasks')
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
log.addHandler(console_handler)
file_handler = logging.FileHandler("log/tasks.log")
file_handler.setLevel(logging.INFO)
log.addHandler(file_handler)

# Хранилище для кэширования уже обработанных транзакций (работает в рамках сессии)
processed_transactions: Set[str] = set()


async def send_message_to_admins(bot, message: str):
    """Отправляет сообщение всем администраторам"""
    from badbadbar_merch_bot import ADMINS
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, text=message, parse_mode="HTML")
        except Exception as e:
            log.error(f"Не удалось отправить сообщение админу {admin_id}: {str(e)}")

async def send_message_to_user(bot, user_id: int, message: str, markup=None):
    """Отправляет сообщение пользователю"""
    try:
        await bot.send_message(user_id, text=message, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        log.error(f"Не удалось отправить сообщение пользователю {user_id}: {str(e)}")

async def approve(bot, orders):
    """Проверяет платежи и автоматически подтверждает их"""
    from badbadbar_merch_bot import calculate_order_price, format_order_details
    
    log.info("Начинаем проверку платежей")
    
    # Получаем всех пользователей с заказами в статусе ожидания подтверждения
    waiting_orders = list(orders.where(status="WAITING_APPROVE"))
    
    if not waiting_orders:
        log.info("Нет заказов, ожидающих подтверждения платежа")
        return
    
    try:
        # Получаем данные о платежах с сайта
        async with aiohttp.ClientSession() as session:
            async with session.get(PAYMENT_URL, timeout=CONNECT_TIMEOUT) as response:
                if response.status != 200:
                    log.error(f"Ошибка при получении данных с сайта: {response.status}")
                    return
                
                response_data = await response.json()
                
                if not response_data or "result" not in response_data or response_data["result"] != "OK":
                    log.error(f"Некорректный формат ответа API: {response_data}")
                    return
                
                payment_data = response_data.get("payload", [])
                
                if not payment_data:
                    log.info("Нет данных о платежах")
                    return
                
                # Логируем количество транзакций
                unprocessed_payments = [
                    p for p in payment_data if p.get("id") not in processed_transactions
                ]
                log.info(f"Получено {len(payment_data)} записей о платежах, из них {len(unprocessed_payments)} новых")
                
                # Обрабатываем каждый заказ, ожидающий подтверждения
                for order in waiting_orders:
                    order_id = order["id"]
                    user_id = order["user_id"]
                    username = order["user_nick"]
                    user_name = order["user_name"]
                    
                    # Рассчитываем стоимость заказа
                    order_price = calculate_order_price(order["order"])
                    
                    log.info(f"Проверяем платежи для {user_name} ({username}), ожидаемая сумма: {order_price}")
                    
                    # Проверяем все новые транзакции
                    for payment in payment_data:
                        payment_id = payment.get("id")
                        
                        # Пропускаем уже обработанные транзакции (из кэша)
                        if payment_id in processed_transactions:
                            continue
                        
                        # Пропускаем если у заказа уже есть ID транзакции
                        # Проверяем есть ли поле payment_transaction_id в заказе
                        if order.get("payment_transaction_id"):
                            processed_transactions.add(order["payment_transaction_id"])
                            continue
                        
                        payment_value = payment.get("value")
                        payment_message = payment.get("message", "")
                        payment_description = payment.get("description", "")
                        payment_timestamp = payment.get("timestamp")
                        
                        # Проверяем, что платеж не слишком старый
                        if payment_timestamp:
                            payment_datetime = datetime.datetime.fromtimestamp(payment_timestamp)
                            current_datetime = datetime.datetime.now()
                            time_diff = current_datetime - payment_datetime
                            
                            # Если платеж старше MAX_PAYMENT_AGE_HOURS часов - пропускаем
                            if time_diff.total_seconds() > MAX_PAYMENT_AGE_HOURS * 3600:
                                continue
                            
                            # Вычисляем, сколько минут назад был сделан платеж
                            minutes_ago = int(time_diff.total_seconds() / 60)
                        else:
                            # Если нет timestamp, предполагаем, что платеж текущий
                            payment_datetime = None
                            minutes_ago = 0
                        
                        if payment_value == order_price:
                            # Проверяем совпадение по тексту сообщения
                            payment_text = payment_message.lower()
                            matched = False
                            
                            # Проверяем совпадение только по никнейму телеграм
                            if username and username.lower() in payment_text:
                                log.info(f"Найдено совпадение по никнейму: {username}")
                                matched = True
                            
                            if matched:
                                log.info(f"Найден подтвержденный платеж ID {payment_id} для {user_name} ({username})")
                                
                                # Обновляем статус заказа и сохраняем ID транзакции
                                order = orders.update(order_id, status="PAID", payment_transaction_id=payment_id)
                                
                                # Отмечаем транзакцию как обработанную в кэше
                                processed_transactions.add(payment_id)
                                
                                # Уведомляем пользователя
                                user_message = f"Вы оплатили заказ #{order_id}. Мы вас оповестим когда он будет готов к выдаче 📦"
                                await send_message_to_user(bot, user_id, user_message)
                                
                                # Уведомляем администраторов
                                # Форматируем сообщение из платежа для вывода
                                payment_message_text = f"«{payment_message}»" if payment_message else "-"
                                payment_time_text = f"{minutes_ago} мин. назад" if payment_timestamp else "неизвестно"
                                
                                admin_message, admin_markup = format_order_details(order, include_timestamp=False, for_admins=True)
                                await send_message_to_admins(bot, admin_message)
                                
                                # Дополнительное сообщение с деталями платежа
                                payment_details = (
                                    f"🔄 <b>Автоматически подтвержден платеж</b>\n"
                                    f"Заказ: #{order_id}\n"
                                    f"Пользователь: {user_name} (@{username})\n"
                                    f"Стоимость: {order_price} руб.\n"
                                    f"Сообщение: {payment_message_text}\n"
                                    f"Описание: {payment_description}\n"
                                    f"Время платежа: {payment_time_text}\n"
                                    f"ID транзакции: {payment_id}"
                                )
                                await send_message_to_admins(bot, payment_details)
                                
                                log.info(f"Заказ #{order_id} пользователя {username} (ID: {user_id}) подтвержден")
                                break
                    
    except aiohttp.ClientError as e:
        log.error(f"Ошибка соединения с сайтом платежей: {str(e)}")
    except json.JSONDecodeError:
        log.error("Ошибка при разборе JSON с сайта платежей")
    except Exception as e:
        log.exception(f"Неожиданная ошибка при обработке платежей: {str(e)}")

async def load_processed_transactions(orders):
    """
    Загружает уже обработанные транзакции из базы данных заказов
    """
    log.info("Загрузка обработанных транзакций из базы данных")
    
    # Загружаем все заказы, у которых есть ID транзакции
    all_orders = list(orders.keys())
    transaction_ids = []
    
    for order_id in all_orders:
        order = orders.get(order_id)
        if order and order.get("payment_transaction_id"):
            transaction_ids.append(order["payment_transaction_id"])
    
    if transaction_ids:
        processed_transactions.update(transaction_ids)
        log.info(f"Загружено {len(transaction_ids)} транзакций из базы данных")
    else:
        log.info("Нет сохраненных транзакций в базе данных")

async def pay_approver(bot, orders):
    """
    Основная задача, которая периодически вызывает функцию проверки платежей
    """
    log.info("Запущено автоматическое подтверждение платежей")
    
    # Загружаем обработанные транзакции при старте
    await load_processed_transactions(orders)
    
    while True:
        try:
            # Проверяем платежи
            await asyncio.wait_for(approve(bot, orders), timeout=TASK_TIMEOUT)
        except asyncio.TimeoutError:
            log.error("Таймаут при выполнении проверки платежей")
        except Exception as e:
            log.exception(f"Ошибка в автоматическом подтверждении платежей: {str(e)}")
        finally:
            await asyncio.sleep(PAUSE)