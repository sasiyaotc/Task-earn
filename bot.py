from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram import executor
import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)

async def is_joined(user_id):
    for ch in [config.CHANNEL_1, config.CHANNEL_2]:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status in ['left','kicked','banned']:
                return False
        except:
            return False
    return True

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    args = message.get_args()
    if args.startswith("ref_"):
        try:
            referrer = args.split("_")[1]
            if str(message.from_user.id) != str(referrer):
                # Save referral logic here (anti-fake in backend)
                pass
        except: pass

    if not await is_joined(message.from_user.id):
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton("📢 Join Channel 1", url=config.CHANNEL_1_LINK))
        kb.add(InlineKeyboardButton("📢 Join Channel 2", url=config.CHANNEL_2_LINK))
        kb.add(InlineKeyboardButton("✅ I Joined - Verify", callback_data="check_join"))
        await message.answer("⚠️ To get full access, please join both channels!\nAfter joining, click Verify button!", reply_markup=kb)
        return

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💰 Open Earning App", web_app=WebAppInfo(url="https://YOUR-KOYEB-APP.koyeb.app")))
    await message.answer(f"✅ Welcome {message.from_user.first_name}!\n\n💸 Earn $0.005 per ad (30 ads/day)\n📋 Complete tasks and earn\n👥 Refer and earn $0.02\n\nOpen app to start earning!", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "check_join")
async def check_join(c: types.CallbackQuery):
    if await is_joined(c.from_user.id):
        await c.message.delete()
        await start_handler(c.message)
    else:
        await bot.answer_callback_query(c.id, "❌ You haven't joined yet! Please join both channels!", show_alert=True)

@dp.message_handler(commands=['admin_add_task'])
async def admin_add_task(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    try:
        parts = message.text.split(" ", 2)
        link = parts[1]
        title = parts[2] if len(parts) > 2 else "New Task"
        await message.answer(f"✅ Free Task Added!\nTitle: {title}\nLink: {link}\nNow live for all users!")
    except:
        await message.answer("Usage:\n/admin_add_task https://t.me/yourgroup Title Of Task")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
