from telebot import types
from bson.objectid import ObjectId
from app.database import products_collection

def register_product_handlers(bot, user_cart, user_state):

    def main_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🛍 Homme", "👗 Femme", "🧒 Enfant")
        markup.add("🛒 Voir Panier")
        return markup

    @bot.message_handler(commands=['start'])
    def start(message):
        user_cart.setdefault(message.chat.id, [])
        bot.send_message(
            message.chat.id,
            "Bienvenue dans notre boutique 🛍",
            reply_markup=main_menu()
        )

    @bot.message_handler(func=lambda m: m.text in ["🛍 Homme", "👗 Femme", "🧒 Enfant"])
    def show_products(message):

        category = message.text.split(" ")[1].lower()
        products = list(products_collection.find({"category": category}))

        if not products:
            bot.send_message(message.chat.id, "Aucun produit trouvé.")
            return

        for product in products:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    "🛒 Ajouter",
                    callback_data=f"add_{product['_id']}"
                )
            )

            caption = f"📦 {product['name']}\n💰 {product['price']} DT"

            image_url = product.get("image_url")

            if image_url and image_url.startswith("http"):
                try:
                    bot.send_photo(message.chat.id, image_url, caption=caption, reply_markup=markup)
                except:
                    bot.send_message(message.chat.id, caption, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, caption, reply_markup=markup)

    # ---- AJOUT PRODUIT ----

    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
    def add_product(call):

        product_id = call.data.split("_")[1]
        product = products_collection.find_one({"_id": ObjectId(product_id)})

        if not product:
            return

        user_state[call.from_user.id] = {
            "product": product,
            "step": "size"
        }

        markup = types.InlineKeyboardMarkup()
        for size in product.get("sizes", []):
            markup.add(types.InlineKeyboardButton(size, callback_data=f"size_{size}"))

        bot.send_message(call.message.chat.id, "Choisissez la taille :", reply_markup=markup)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("size_"))
    def select_color(call):

        size = call.data.split("_")[1]
        state = user_state.get(call.from_user.id)
        if not state:
            return

        state["size"] = size
        state["step"] = "color"

        markup = types.InlineKeyboardMarkup()
        for color in state["product"].get("colors", []):
            markup.add(types.InlineKeyboardButton(color, callback_data=f"color_{color}"))

        bot.send_message(call.message.chat.id, "Choisissez la couleur :", reply_markup=markup)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("color_"))
    def select_quantity(call):

        color = call.data.split("_")[1]
        state = user_state.get(call.from_user.id)
        if not state:
            return

        state["color"] = color
        state["step"] = "quantity"

        bot.send_message(call.message.chat.id, "Entrez la quantité :")
        bot.answer_callback_query(call.id)

    @bot.message_handler(func=lambda m: m.from_user.id in user_state and user_state[m.from_user.id]["step"] == "quantity")
    def save_quantity(message):

        try:
            quantity = int(message.text)
            if quantity <= 0:
                bot.send_message(message.chat.id, "Quantité invalide.")
                return
        except:
            bot.send_message(message.chat.id, "Entrez un nombre valide.")
            return

        state = user_state[message.from_user.id]
        product = state["product"]

        item = {
            "product_id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"],
            "size": state["size"],
            "color": state["color"],
            "quantity": quantity,
            "image_url": product.get("image_url")
        }

        user_cart.setdefault(message.from_user.id, []).append(item)
        del user_state[message.from_user.id]

        bot.send_message(message.chat.id, "Produit ajouté ✅")