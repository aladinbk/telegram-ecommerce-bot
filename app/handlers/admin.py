from telebot import types
from app.config import ADMIN_ID
from app.database import orders_collection

def register_admin_handlers(bot):

    @bot.message_handler(commands=['admin'])
    def admin_panel(message):

        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.chat.id, "Accès refusé ❌")
            return

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📦 Commandes", callback_data="admin_orders"))
        markup.add(types.InlineKeyboardButton("💰 Revenus", callback_data="admin_revenue"))

        bot.send_message(message.chat.id, "Dashboard Admin", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == "admin_orders")
    def view_orders(call):

        if call.from_user.id != ADMIN_ID:
            return

        orders = list(orders_collection.find())

        for order in orders:
            bot.send_message(
                call.message.chat.id,
                f"Commande {order['_id']}\nTotal: {order['total']} DT"
            )

    @bot.callback_query_handler(func=lambda call: call.data == "admin_revenue")
    def revenue(call):

        if call.from_user.id != ADMIN_ID:
            return

        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$total"}}}]
        result = list(orders_collection.aggregate(pipeline))
        total = result[0]["total"] if result else 0

        bot.send_message(call.message.chat.id, f"Chiffre d'affaires: {total} DT")