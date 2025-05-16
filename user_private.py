from aiogram import F, types, Router

from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import (
    as_list,
    as_marked_section
)

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from filters.chat_types import ChatTypeFilter

from kbds.reply import get_keyboard

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

user_carts = {}
user_addresses = {}

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет, я виртуальный помощник",
        reply_markup=get_keyboard(
            "Меню",
            "Помощь",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Корзина",
            placeholder="Что вас интересует?",
            sizes=(2, 2)
        ),
    )


@user_private_router.message(F.text.lower() == "помощь")
@user_private_router.message(Command("help"))
async def menu_cmd(message: types.Message):
    await message.answer("Если у вас случилось ошибка,\n"
                         "то вот вам контакты поддержки:\n"
                         "Главные разработчики: @Putinman22 и @laryugkh")

@user_private_router.message(F.text.lower() == "о магазине")
@user_private_router.message(Command("about"))
async def about_cmd(message: types.Message):
    await message.answer("О нас: 🍕Pizza - это ваш персональный помощник для заказа вкуснейшей пиццы! Ознакомьтесь с разнообразным меню, выбирайте любимые начинки. Оформляйте заказ в пару кликов. Быстро, удобно и вкусно - всё для вашего комфорта!")

@user_private_router.message(F.text.lower() == "варианты оплаты")
@user_private_router.message(Command("payment"))
async def payment_cmd(message: types.Message):
    text = as_list(
        as_marked_section(
            "Варианты оплаты:",
            "Можно:",
            "Картой",
            "В заведении",
            marker="✅ ",
        ),
        as_marked_section(
            "Нельзя:",
            "Брад, можно за кошельком в машину?",
            marker="❌ "
        ),
        sep="\n----------------------\n",
    )
    await message.answer(text.as_html())

@user_private_router.message(F.text.lower() == "варианты доставки")
@user_private_router.message(Command("shipping"))
async def menu_cmd(message: types.Message):
    text = as_list(
        as_marked_section(
            "Варианты доставки/заказа:",
            "Можно:",
            "Курьер",
            "Самовынос",
            "Покушаю у вас",
            marker="✅ ",
        ),
        as_marked_section(
            "Нельзя:",
            "Почта России",
            marker="❌ "
        ),
        sep="\n----------------------\n",
    )
    await message.answer(text.as_html())

# @user_private_router.message(F.text.lower() == "меню")
@user_private_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message):
    button_peperoni = types.InlineKeyboardButton(text="Пицца пеперони", callback_data="In_peperoni_button")
    button_margarita = types.InlineKeyboardButton(text="Пицца маргарита", callback_data="In_margarita_button")
    button_4sura = types.InlineKeyboardButton(text="Пицца 4 сыра", callback_data="In_4sura_button")

    keyboard_inline = types.InlineKeyboardMarkup(inline_keyboard=[
        [button_peperoni],
        [button_margarita],
        [button_4sura]
    ])
    await message.reply("Выберете пиццу: ", reply_markup=keyboard_inline)

@user_private_router.callback_query(F.data == "In_peperoni_button")
async def send_random_value(callback: types.CallbackQuery):
    photo = "https://ibb.co/B5MtD0F4"
    caption = (
        'Пицца пеперони\n\n'
        'Ингредиенты: пряные колбаски пепперони с легкой перчинкой, сыр моцарелла со сливочным вкусом и нежный томатный соус')
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Добавить в корзину", callback_data="add_peperoni")]
    ])
    await callback.message.answer_photo(photo, caption=caption, reply_markup=keyboard)

@user_private_router.callback_query(F.data == "In_margarita_button")
async def send_random_value(callback: types.CallbackQuery):
    photo = "https://ibb.co/sdGLy2RJ"
    caption = (
        'Пицца маргарита\n\n'
        'Ингредиенты: измельчённые и очищенные помидоры, моцарелла, свежие листья базилика и оливковое масло')
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Добавить в корзину", callback_data="add_margarita")]
    ])
    await callback.message.answer_photo(photo, caption=caption, reply_markup=keyboard)

@user_private_router.callback_query(F.data == "In_4sura_button")
async def send_random_value(callback: types.CallbackQuery):
    photo = "https://ibb.co/dw1nTjH3"
    caption = (
        'Пицца 4 сыра\n\n'
        'Ингредиенты: моцарелла, тильзитер, пармезан, дор блю, сливочный соус')
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Добавить в корзину", callback_data="add_4sura")]
    ])
    await callback.message.answer_photo(photo, caption=caption, reply_markup=keyboard)

@user_private_router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    product_key = callback.data[4:]

    if user_id not in user_carts:
        user_carts[user_id] = {}

    cart = user_carts[user_id]

    if cart.get(product_key, 0) >= 1:
        await callback.answer("В корзине уже есть 1 такая пицца. Больше нельзя добавить", show_alert=True)
        return

    cart[product_key] = 1
    await callback.answer("Пицца добавлена в корзину!")

@user_private_router.callback_query(F.data.startswith("inc_"))
async def increase_quantity(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    product_key = callback.data[4:]  # Например, "peperoni"
    cart = user_carts.setdefault(user_id, {})
    cart[product_key] = cart.get(product_key, 0) + 1
    await callback.answer("Количество увеличено!")
    await show_cart_update(callback, user_id)

@user_private_router.callback_query(F.data.startswith("dec_"))
async def decrease_quantity(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    product_key = callback.data[4:]
    cart = user_carts.setdefault(user_id, {})
    if cart.get(product_key, 0) > 1:
        cart[product_key] -= 1
        await callback.answer("Количество уменьшено!")
    else:
        cart.pop(product_key, None)
        await callback.answer("Товар удалён из корзины!")
    await show_cart_update(callback, user_id)

@user_private_router.callback_query(F.data.startswith("del_"))
async def delete_product(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    product_key = callback.data[4:]
    cart = user_carts.setdefault(user_id, {})
    if product_key in cart:
        cart.pop(product_key)
        await callback.answer("Товар удалён из корзины!")
    else:
        await callback.answer("Товар уже удалён.")
    await show_cart_update(callback, user_id)

@user_private_router.message(F.text.lower() == "корзина")
@user_private_router.message(Command("cart"))
async def show_cart_update(message: types.Message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, {})

    if not cart:
        await message.answer("Ваша корзина пуста")
        return

    for product_key, qty in cart.items():
        if product_key == "peperoni":
            name = "Пицца пепперони"
            desc = "Ингредиенты: пряные колбаски пепперони с легкой перчинкой, сыр моцарелла со сливочным вкусом и нежный томатный соус"
        elif product_key == "margarita":
            name = "Пицца маргарита"
            desc = "Ингредиенты: измельчённые и очищенные помидоры, моцарелла, свежие листья базилика и оливковое масло"
        elif product_key == "4sura":
            name = "Пицца 4 сыра"
            desc = "Ингредиенты: моцарелла, тильзитер, пармезан, дор блю, сливочный соус"

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="➖", callback_data=f"dec_{product_key}"),
                types.InlineKeyboardButton(text=f"Количество: {qty}", callback_data="count"),
                types.InlineKeyboardButton(text="➕", callback_data=f"inc_{product_key}")
            ],
            [
                types.InlineKeyboardButton(text="Удалить", callback_data=f"del_{product_key}")
            ]
        ])

        await message.answer(f"{name}\n{desc}\n\nКоличество: {qty}", reply_markup=keyboard)

    keyboard_checkout = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")]
    ])
    await message.answer("Когда будете готовы, нажмите кнопку ниже для оформления заказа:", reply_markup=keyboard_checkout)

class OrderStates(StatesGroup):
    waiting_for_phone = State()
    address_choice = State()
    waiting_for_address = State()
    waiting_for_payment = State()

@user_private_router.callback_query(F.data == "checkout")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, {})
    if not cart:
        await callback.answer("Ваша корзина пуста", show_alert=True)
        return

    await callback.message.answer(
        "Пожалуйста, отправьте ваш номер телефона.\n"
        "Можно нажать кнопку ниже, чтобы отправить контакт",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Отправить номер телефона", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(OrderStates.waiting_for_phone)
    await callback.answer()

@user_private_router.message(OrderStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = None
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(phone=phone)

    user_id = message.from_user.id
    stored_address = user_addresses.get(user_id)

    if stored_address:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Использовать сохраненный адрес")],
                [KeyboardButton(text="Ввести новый адрес")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(f"У вас сохранен адрес: {stored_address}\nИспользовать его или ввести новый?", reply_markup=keyboard)
        await state.set_state(OrderStates.address_choice)
    else:
        await message.answer("Теперь введите адрес доставки")
        await state.set_state(OrderStates.waiting_for_address)

@user_private_router.message(OrderStates.address_choice, F.text == "Использовать сохраненный адрес")
async def use_stored_address(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    stored_address = user_addresses.get(user_id)

    await state.update_data(address=stored_address)
    await state.set_state(OrderStates.address_choice)

@user_private_router.message(OrderStates.address_choice, F.text == "Ввести новый адрес")
async def request_new_address(message: types.Message, state: FSMContext):
    await message.answer("Теперь введите адрес доставки")
    await state.set_state(OrderStates.waiting_for_address)

@user_private_router.message(OrderStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    address = message.text
    user_id = message.from_user.id
    user_addresses[user_id] = address
    await state.update_data(address=address)
    await state.set_state(OrderStates.waiting_for_payment)

    await message.answer(
        "Сейчас вы будете перенаправлены к оплате заказа через Telegram.\n"
        "Нажмите кнопку ниже для выставления счёта",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Оплатить заказ")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


import os
from aiogram.types import LabeledPrice
from aiogram import Bot

PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

@user_private_router.message(OrderStates.waiting_for_payment, F.text == "Оплатить заказ")
async def process_payment(message: types.Message, state: FSMContext):
    await message.bot.send_invoice(
        message.chat.id,
        title='Покупка пиццы',
        description='Покупка пиццы',
        payload='invoice',
        provider_token=PAYMENT_TOKEN,
        currency='RUB',
        prices=[LabeledPrice(label='Покупка пиццы', amount=10000)]
    )

@user_private_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@user_private_router.message(F.content_type == "successful_payment")
async def process_successful_payment(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer("Спасибо за оплату! Ваш заказ принят в обработку. Ожидайте доставку 🍕")
    user_carts[user_id] = {}
    await state.clear()


