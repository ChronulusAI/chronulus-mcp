from typing import Annotated
import json
from chronulus import Session
from mcp.server.fastmcp import Context
from pydantic import Field, AnyUrl


async def create_chronulus_session(
        name: Annotated[str, Field(description="A short descriptive name for the use case defined in the session.")],
        situation: Annotated[str, Field(description="The broader context for the use case")],
        task: Annotated[str, Field(description="Specific details on the forecasting or prediction task.")],
        ctx: Context
) -> str:
    """Creates a new Chronulus Session

    A Chronulus Session allows you to use Chronulus Agents. To create a session, you need to provide a situation
    and task. Once created, this will generate a unique session id that can be used to when calling the agents.

    Args:
        name (str): A short descriptive name for the use case defined in the session.
        situation (str): The broader context for the use case.
        task (str): The specific prediction task.


    Returns:
        str: The session ID.
    """

    try:
        chronulus_session = Session(
            name=name,
            situation=situation,
            task=task,
            verbose=False,
        )

    except Exception as e:
        error_message = f"Failed to create chronulus session with the following error: \n\n{e}"
        _ = await ctx.error(message=error_message)
        return error_message

    return chronulus_session.session_id


async def get_risk_assessment_scorecard(
        session_id: Annotated[str, Field(description="The session_id for the forecasting or prediction use case")],
        as_json:  Annotated[bool, Field(description="If true, returns the scorecard in JSON format, otherwise returns a markdown formatted scorecard")]
) -> str:
    """Get the risk assessment scorecard for the Session

    Args:
        session_id (str): The session_id for the forecasting or prediction use case.
        as_json (bool): If true, returns the scorecard in JSON format, otherwise returns a markdown formatted scorecard

    Returns:
        str: a risk assessment scorecard in the specified format.
    """

    chronulus_session = Session.load_from_saved_session(session_id=session_id, verbose=False)
    scorecard_md = chronulus_session.risk_scorecard(width='100%')
    if as_json:
        content = json.dumps(chronulus_session.scorecard.model_dump())
    else:
        content = scorecard_md
    return content


