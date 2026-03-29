from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("groupid"))
async def cmd_group_id(message: Message):
    chat = message.chat
    if chat.type == "private":
        await message.answer(
            f"ℹ️ Bu shaxsiy chat.\n\n"
            f"🆔 Sizning ID: <code>{chat.id}</code>\n\n"
            f"Guruh ID olish uchun botni guruhga qo'shing va shu komandani yuboring.",
            parse_mode="HTML"
        )
    else:
        chat_type = {
            "group": "Guruh",
            "supergroup": "Supergroup",
            "channel": "Kanal"
        }.get(chat.type, chat.type)

        await message.answer(
            f"✅ <b>{chat_type} ma'lumotlari:</b>\n\n"
            f"📛 Nomi: <b>{chat.title}</b>\n"
            f"🆔 ID: <code>{chat.id}</code>\n\n"
            f"Shu ID ni <code>.env</code> faylidagi <b>GROUP_ID</b> ga yozing.",
            parse_mode="HTML"
        )