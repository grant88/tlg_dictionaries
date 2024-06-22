import os
import logging
from db import DB

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

# Stages
DICT_CHOICES_STAGE, BANK_STAGE, MCC_STAGE, END_STAGE = range(4)
# Callback data
DICT_CHOICES, BANK_CHOICES, MCC_CHOICES, BY_BIK, BY_MCC, READ_BIC, READ_MCC, END = range(8)

TOKEN = os.environ.get('BANKS_LIST_TOKEN', 'Not Set')
print(TOKEN)

db = DB()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("Инфо по банкам", callback_data=str(BANK_CHOICES)),
            InlineKeyboardButton("MCC", callback_data=str(MCC_CHOICES)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Сервис, который позволяет получать информацию по разным справочникам. \nВыбери, что нужно", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return DICT_CHOICES_STAGE

async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Инфо по банкам", callback_data=str(BANK_CHOICES)),
            InlineKeyboardButton("MCC", callback_data=str(MCC_CHOICES)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    await query.edit_message_text(text="Сервис, который позволяет получать информацию по разным справочникам. \nВыбери, что нужно", reply_markup=reply_markup)
    return DICT_CHOICES_STAGE


async def dict_choices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Инфо по банкам", callback_data=str(BANK_CHOICES)),
            InlineKeyboardButton("MCC", callback_data=str(MCC_CHOICES)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выбери, по какому справочнику искать", reply_markup=reply_markup)
    return DICT_CHOICES_STAGE


async def bank_choices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Поиск по БИКу банка", callback_data=str(BY_BIK)),
            #InlineKeyboardButton("Поиск по наименованию банка", callback_data=str(BY_BANK_NAME)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Выбери критерий, по которому будешь искать банк", reply_markup=reply_markup
    )
    return BANK_STAGE


async def mcc_choices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Поиск по MCC", callback_data=str(BY_MCC)),
            #InlineKeyboardButton("Поиск по наименованию MCC", callback_data=str(BY_MCC_NAME)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Выбери критерий, по которому будешь искать MCC", reply_markup=reply_markup
    )
    return MCC_STAGE


async def by_bik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Хочу искать банки по другому критерию", callback_data=str(BANK_CHOICES)),
        ],
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
         ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Вводи БИК банка", reply_markup=reply_markup
    )
    return BANK_STAGE

async def read_bik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bik = update.message.text
    print(f"{bik=}")
    keyboard = [
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
         ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    #data = db.select(f"select * from public.banks where bic = {bik}")
    #await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    await update.message.reply_text(f"Данные по БИКу {bik}", reply_markup=reply_markup)
    # Transfer to conversation state `SECOND`
    return END_STAGE

async def by_mcc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Хочу искать MCC по другому критерию", callback_data=str(MCC_CHOICES)),
        ],
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
         ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Вводи MCC", reply_markup=reply_markup
    )
    return MCC_STAGE

async def read_mcc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    mcc = update.message.text
    print(f"{mcc=}")
    keyboard = [
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
         ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    #data = db.select(f"select * from public.banks where bic = {bik}")
    await update.message.reply_text(f"Данные по MCC {mcc}", reply_markup=reply_markup)
    return END_STAGE


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DICT_CHOICES_STAGE: [
                CallbackQueryHandler(bank_choices, pattern="^" + str(BANK_CHOICES) + "$"),
                CallbackQueryHandler(mcc_choices, pattern="^" + str(MCC_CHOICES) + "$"),
            ],
            BANK_STAGE: [
                CallbackQueryHandler(by_bik, pattern="^" + str(BY_BIK) + "$"),
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=read_bik),
            ],
            MCC_STAGE: [
                CallbackQueryHandler(by_mcc, pattern="^" + str(BY_MCC) + "$"),  
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=read_mcc),
            ],
            END_STAGE: [
                CallbackQueryHandler(start_over, pattern="^" + str(DICT_CHOICES) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)
#    application.add_handler(bik_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()