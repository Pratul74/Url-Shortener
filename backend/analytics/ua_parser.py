from user_agents import parse
import asyncio

class UserAgentService:

    async def parse(self, user_agent: str) -> dict:
        ua = await asyncio.to_thread(parse, user_agent)

        return {
            "browser": ua.browser.family,
            "browser_version": ua.browser.version_string,
            "os": ua.os.family,
            "os_version": ua.os.version_string,
            "device": ua.device.family,
            "device_brand": ua.device.brand,
            "device_model": ua.device.model,
            "is_mobile": ua.is_mobile,
            "is_tablet": ua.is_tablet,
            "is_pc": ua.is_pc,
            "is_bot": ua.is_bot,
        }