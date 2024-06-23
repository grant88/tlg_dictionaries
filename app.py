import os
import logging
from db import DB
from typing import Dict
import polars as pl

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram.constants import ParseMode

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

DICT_CHOICES_STAGE, BANK_STAGE, MCC_STAGE, READ_STAGE, END_STAGE = range(5)
(
    DICT_CHOICES,
    BANK_CHOICES,
    MCC_CHOICES,
    BANK_BY_BIK,
    BANK_BY_NAME,
    MCC_BY_CODE,
    MCC_BY_DESCR,
    END,
) = range(8)

TOKEN = os.environ.get("BANKS_LIST_TOKEN", "TOKEN Not Set")

db = DB()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("Инфо по банкам", callback_data=str(BANK_CHOICES)),
            InlineKeyboardButton("MCC", callback_data=str(MCC_CHOICES)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """
        Сервис, который позволяет получать информацию по разным справочникам.
        Выбери справочник, который нужен
    """
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return DICT_CHOICES_STAGE


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Инфо по банкам", callback_data=str(BANK_CHOICES)),
            InlineKeyboardButton("MCC", callback_data=str(MCC_CHOICES)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """
        Сервис, который позволяет получать информацию по разным справочникам.
        Выбери справочник, который нужен
    """
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return DICT_CHOICES_STAGE


async def dict_choices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"{update=}\n{context=}")
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Инфо по банкам", callback_data=str(BANK_CHOICES)),
            InlineKeyboardButton("MCC", callback_data=str(MCC_CHOICES)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Выбери, по какому справочнику искать"
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return DICT_CHOICES_STAGE


async def bank_choices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Поиск банка по БИКу", callback_data=str(BANK_BY_BIK)),
            InlineKeyboardButton(
                "Поиск банка по наименованию", callback_data=str(BANK_BY_NAME)
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Выбери критерий, по которому будешь искать банк"
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return BANK_STAGE


async def mcc_choices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Поиск по MCC", callback_data=str(MCC_BY_CODE)),
            InlineKeyboardButton(
                "Поиск по наименованию MCC", callback_data=str(MCC_BY_DESCR)
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Выбери критерий, по которому будешь искать MCC"
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return MCC_STAGE


async def bank_by_bik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["previous_step"] = "bank_by_bik"
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(
                "Искать банки по другому критерию", callback_data=str(BANK_CHOICES)
            ),
        ],
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Вводи БИК банка",
        reply_markup=reply_markup,
    )
    return READ_STAGE


async def mcc_by_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["previous_step"] = "mcc_by_code"
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(
                "Искать MCC по другому критерию", callback_data=str(MCC_CHOICES)
            ),
        ],
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Вводи MCC", reply_markup=reply_markup)
    return READ_STAGE


async def bank_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["previous_step"] = "bank_by_name"
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(
                "Искать банки по другому критерию", callback_data=str(BANK_CHOICES)
            ),
        ],
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Вводи наименование банка"
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return READ_STAGE


async def mcc_by_descr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["previous_step"] = "mcc_by_descr"
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(
                "Искать MCC по другому критерию", callback_data=str(MCC_CHOICES)
            ),
        ],
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Вводи наименование кода ТСП"
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return READ_STAGE


def reformat(data: pl.DataFrame) -> str:
    if data.is_empty():
        return "Ничего нашлось ("

    line_len = 30
    reformatted = "#" * line_len + "\n"

    for row in data.iter_rows():
        row_dict = dict(zip(data.columns, row))
        row_line = (
            "\n".join(
                [f"<b>{k.upper()}</b>: <i>{v}</i>\n" for k, v in row_dict.items()]
            )
            + "\n"
            + "#" * line_len
            + "\n"
        )
        reformatted += row_line
    logger.info(f"{reformatted=}")
    return reformatted


async def read_user_input_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    previous_step = context.user_data["previous_step"]
    user_input_text = update.message.text
    keyboard = [
        [
            InlineKeyboardButton("Главное меню", callback_data=str(DICT_CHOICES)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sqls = {
        "bank_by_bik": f"select short_name, bik, date_started from public.banks where bik = {user_input_text}",
        "mcc_by_code": f"select code, descr from public.mcc where code = {user_input_text}",
        "bank_by_name": f"select short_name, bik, date_started from public.banks where short_name ilike '%{user_input_text}%'",
        "mcc_by_descr": f"select code, descr from public.mcc where descr ilike '%{user_input_text}%'",
    }
    data = db.select(sqls[previous_step])
    reformatted_data = reformat(data)
    await update.message.reply_text(
        text=reformatted_data,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )
    return END_STAGE


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DICT_CHOICES_STAGE: [
                CallbackQueryHandler(
                    bank_choices, pattern="^" + str(BANK_CHOICES) + "$"
                ),
                CallbackQueryHandler(mcc_choices, pattern="^" + str(MCC_CHOICES) + "$"),
            ],
            BANK_STAGE: [
                CallbackQueryHandler(bank_by_bik, pattern="^" + str(BANK_BY_BIK) + "$"),
                CallbackQueryHandler(
                    bank_by_name, pattern="^" + str(BANK_BY_NAME) + "$"
                ),
            ],
            MCC_STAGE: [
                CallbackQueryHandler(mcc_by_code, pattern="^" + str(MCC_BY_CODE) + "$"),
                CallbackQueryHandler(
                    mcc_by_descr, pattern="^" + str(MCC_BY_DESCR) + "$"
                ),
            ],
            READ_STAGE: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=read_user_input_text,
                ),
            ],
            END_STAGE: [
                CallbackQueryHandler(start_over, pattern="^" + str(DICT_CHOICES) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
