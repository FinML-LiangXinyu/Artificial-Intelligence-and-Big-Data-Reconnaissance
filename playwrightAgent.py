import os
from agentscope.agent import Agent
from agentscope.credential import DeepSeekCredential
from agentscope.model import DeepSeekChatModel
from agentscope.console import ConsoleRenderer
from agentscope.message import UserMsg, TextBlock, HintBlock
from agentscope.tool import Toolkit, Bash
from agentscope.permission import PermissionMode
import asyncio

# LLM 使用 DeepSeek 开发的 deepseek-v4-flash 
playwrightAgent = Agent(
    name = "Playwright Agent",
    system_prompt = "You are a browser-auto agent,"
    "You can use playwright-cli to control browser.",
    model = DeepSeekChatModel(
        credential = DeepSeekCredential(api_key = os.environ.get("DEEPSEEK_API_KEY")),
        model = "deepseek-v4-flash"
    ),

    # 给 Agent 注册 Bash 工具，允许 Agent 执行 cli 命令
    # 给 Agent 指定 Skill 文件地址
    toolkit = Toolkit(tools = [Bash()], skills_or_loaders = [".agents/skills/playwright-cli"]),
)

# 启动 LLM 的思考模式
playwrightAgent.model.parameters.thinking_enable = True
# 这里只是演示，所以将 Agent 的权限许可模式设置为了全部放行，注意这在生产环境中是危险的，可能造成破坏性的结果。
playwrightAgent.state.permission_context.mode = PermissionMode.BYPASS

# 利用 consolerender 在终端渲染事件流
consolerender = ConsoleRenderer()

async def conversion_with_agent():
    """构造一个和智能体沟通的异步函数"""
    # 构造一个系统暗示，在智能体每次响应前注入，要求智能体使用有头浏览器
    hint = HintBlock(hint = [TextBlock(text = "All browser-auto motion should use headed browser.")])
    while True:
        user_input: str = input("User:")
        if "exit" in user_input:
            break
        user_msg = UserMsg(name = "user", content = [TextBlock(text = user_input)])
        # Agent 每次回复时注入系统提示。
        playwrightAgent.state.append_context(name = "system", blocks = [hint])
        reponses = playwrightAgent.reply_stream(user_msg)
        async for event in reponses:
            # 将智能体的流式响应传入终端渲染工具
            consolerender.render(event)

    return

if __name__ == "__main__":
    asyncio.run(conversion_with_agent())