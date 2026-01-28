from bot.services.vip_features.history import VipHistoryService


async def show_insights_ui(query, context):
    user_id = query.from_user.id
    insights = await VipHistoryService.get_full_insights(user_id)

    text = (
        "📊 *Connection Insights*\n\n"
        f"💬 Total chats: {insights['total_chats']}\n"
        f"⏱️ Avg chat time: {insights['time']['average_time']}\n"
        f"🏆 Long chats: {insights['quality']['long_chat_percent']:.1f}%\n\n"
        "🌍 Regions & languages available in detailed view."
    )

    await query.edit_message_text(text, parse_mode="Markdown")
