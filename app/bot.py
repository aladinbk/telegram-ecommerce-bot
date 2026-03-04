import telebot
from app.config import TOKEN
from app.handlers.products import register_product_handlers
from app.handlers.cart import register_cart_handlers
from app.handlers.admin import register_admin_handlers

bot = telebot.TeleBot(TOKEN)

user_cart = {}
user_state = {}

register_product_handlers(bot, user_cart, user_state)
register_cart_handlers(bot, user_cart)
register_admin_handlers(bot)

print("Bot lancé...")
bot.infinity_polling()