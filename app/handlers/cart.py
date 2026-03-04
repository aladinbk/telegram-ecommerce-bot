from telebot import types
from datetime import datetime
from app.database import orders_collection

def register_cart_handlers(bot, user_cart):

    @bot.message_handler(func=lambda m: m.text == "🛒 Voir Panier")
    def view_cart(message):

        cart = user_cart.get(message.chat.id, [])
        if not cart:
            bot.send_message(message.chat.id, "🛒 Panier vide.")
            return

        total = 0

        for index, item in enumerate(cart):

            subtotal = item["price"] * item["quantity"]
            total += subtotal

            text = f"""
🛍 {item['name']}
💰 {item['price']} DT
📏 Taille: {item['size']}
🎨 Couleur: {item['color']}
🔢 Qté: {item['quantity']}
Sous-total: {subtotal} DT
"""

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("➕", callback_data=f"inc_{index}"),
                types.InlineKeyboardButton("➖", callback_data=f"dec_{index}")
            )
            markup.add(
                types.InlineKeyboardButton("🗑", callback_data=f"delete_{index}")
            )

            bot.send_message(message.chat.id, text, reply_markup=markup)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Confirmer", callback_data="confirm"))

        bot.send_message(message.chat.id, f"💳 Total: {total} DT", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("inc_"))
    def inc(call):
        index = int(call.data.split("_")[1])
        user_cart[call.from_user.id][index]["quantity"] += 1
        bot.answer_callback_query(call.id, "Augmenté")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("dec_"))
    def dec(call):
        index = int(call.data.split("_")[1])
        user_cart[call.from_user.id][index]["quantity"] -= 1
        if user_cart[call.from_user.id][index]["quantity"] <= 0:
            user_cart[call.from_user.id].pop(index)
        bot.answer_callback_query(call.id, "Diminué")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
    def delete(call):
        index = int(call.data.split("_")[1])
        user_cart[call.from_user.id].pop(index)
        bot.answer_callback_query(call.id, "Supprimé")

    @bot.callback_query_handler(func=lambda call: call.data == "confirm")
    def confirm(call):

        cart = user_cart.get(call.from_user.id, [])
        if not cart:
            return

        total = sum(item["price"] * item["quantity"] for item in cart)

        order = {
            "user_id": call.from_user.id,
            "items": cart,
            "total": total,
            "created_at": datetime.utcnow()
        }

        orders_collection.insert_one(order)
        user_cart[call.from_user.id] = []

        bot.send_message(call.message.chat.id, "Commande confirmée ✅")
        bot.answer_callback_query(call.id)