import logging
import os

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv

try:
    from openai_agent import create_agent  # type: ignore[import-not-found]
    from openai_agent_executor import (
        OpenAIAgentExecutor,  # type: ignore[import-untyped]
    )
except ImportError:
    from .openai_agent import create_agent
    from .openai_agent_executor import OpenAIAgentExecutor
from starlette.applications import Starlette


load_dotenv()

logging.basicConfig()


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=5000)
def main(host: str, port: int):
    # Resolve API provider configuration.
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            'Set OPENROUTER_API_KEY (recommended) or OPENAI_API_KEY environment variable'
        )

    base_url = os.getenv('OPENROUTER_BASE_URL') or os.getenv('OPENAI_BASE_URL')
    if os.getenv('OPENROUTER_API_KEY') and not base_url:
        base_url = 'https://openrouter.ai/api/v1'

    skill = AgentSkill(
        id='trustmesh_output_audit',
        name='TrustMesh Output Audit',
        description='Audits agent outputs for correctness, safety, and compliance.',
        tags=["governance", "audit", "safety", "compliance", "meta-agent"],
        examples=[
            'Audit this draft answer for hallucinations and return strict JSON.',
            'Compare two agent outputs and pick the safer, more accurate one.',
            'Evaluate compliance risk and provide corrected response with confidence score.',
        ],
    )

    # AgentCard for OpenAI-based agent
    agent_card = AgentCard(
        name='trustmesh-auditor',
        description='Meta-agent for output validation, risk analysis, and governance checks.',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # Create OpenAI agent
    agent_data = create_agent()

    agent_executor = OpenAIAgentExecutor(
        card=agent_card,
        tools=agent_data['tools'],
        api_key=api_key,
        base_url=base_url,
        system_prompt=agent_data['system_prompt'],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    routes = a2a_app.routes()

    app = Starlette(routes=routes)

    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    main()