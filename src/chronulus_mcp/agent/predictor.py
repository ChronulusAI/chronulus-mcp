import json
from typing import Annotated, List, Dict, Union

from mcp.server.fastmcp import Context
from pydantic import Field

from ._types import InputField, generate_model_from_fields

from chronulus import Session
from chronulus.estimator import BinaryPredictor


async def create_prediction_agent_and_get_predictions(
        session_id: Annotated[str, Field(description="The session_id for the forecasting or prediction use case")],
        input_data_model: Annotated[List[InputField], Field(
            description="""Metadata on the fields you will include in the input_data."""
        )],
        input_data: Annotated[Dict[str, Union[str, dict, List[dict]]], Field(description="The forecast inputs that you will pass to the chronulus agent to make the prediction. The keys of the dict should correspond to the InputField name you provided in input_fields.")],
        ctx: Context,
        num_experts: Annotated[int, Field(description="The number of experts to consult when forming consensus")],
) -> Union[str, Dict[str, Union[dict, str]]]:
    """Queues and retrieves a binary event prediction from Chronulus with a predefined session_id

    This tool creates a BinaryPredictor agent and then provides a prediction input to the agent and returns the prediction data and
    text explanations from each of the experts consulted by the agent.

    Args:
        session_id (str): The session_id for the forecasting or prediction use case.
        input_data_model (List[InputField]): Metadata on the fields you will include in the input_data. Eg., for a field named "brand", add a description like "the brand of the product to forecast"
        input_data (Dict[str, Union[str, dict, List[dict]]]): The prediction inputs that you will pass to the chronulus agent to make the prediction. The keys of the dict should correspond to the InputField name you provided in input_fields.
        ctx (Context): Context object providing access to MCP capabilities.
        num_experts (int): The number of experts to consult when forming consensus.

    Returns:
        Union[str, Dict[str, Union[dict, str]]]: a dictionary with prediction data, a text explanation of the predictions, agent_id, and probability estimate.
    """


    try:
        chronulus_session = Session.load_from_saved_session(session_id=session_id, verbose=False)
    except Exception as e:
        error_message = f"Failed to retrieve session with session_id: {session_id}\n\n{e}"
        _ = await ctx.error( message=error_message)
        return error_message

    try:
        InputItem = generate_model_from_fields("InputItem", input_data_model)
    except Exception as e:
        error_message = f"Failed to create InputItem model with input data model: {json.dumps(input_data_model, indent=2)}\n\n{e}"
        _ = await ctx.error(message=error_message)
        return error_message

    try:
        item = InputItem(**input_data)
    except Exception as e:
        error_message = f"Failed to validate the input_data with the generated InputItem model. \n\n{e}"
        _ = await ctx.error(message=error_message)
        return error_message

    try:
        agent = BinaryPredictor(
            session=chronulus_session,
            input_type=InputItem,
            verbose=False,
        )
    except Exception as e:
        return f"""Error at nf_agent: {str(e)}
        
input_fields = {input_data_model}

input_data = {json.dumps(input_data, indent=2)}

input_type = {str(type(InputItem))}
"""

    try:

        req = agent.queue(item, num_experts=num_experts, note_length=(5,10))
    except Exception as e:
        return f"""Error at nf_agent: {str(e)}"""

    try:
        prediction_set = agent.get_request_predictions(req.request_id)
        return {
            "agent_id": agent.estimator_id,
            "request_id": req.request_id,
            "beta_params": prediction_set.beta_params,
            'expert_opinions': [p.text for p in prediction_set],
            'probability': prediction_set.prob_a}

    except Exception as e:
        return f"""Error on prediction: {str(e)}"""


async def reuse_prediction_agent_and_get_prediction(
        agent_id: Annotated[str, Field(description="The agent_id for the forecasting or prediction use case and previously defined input_data_model")],
        input_data: Annotated[Dict[str, Union[str, dict, List[dict]]], Field(
            description="The forecast inputs that you will pass to the chronulus agent to make the prediction. The keys of the dict should correspond to the InputField name you provided in input_fields.")],
        num_experts: Annotated[int, Field(description="The number of experts to consult when forming consensus")],

) -> Union[str, Dict[str, Union[dict, str]]]:
    """Queues and retrieves a binary event prediction from Chronulus with a previously created agent_id

    This tool provides a prediction input to a previous created Chronulus BinaryPredictor agent and returns the
    prediction data and text explanations from each of the experts consulted by the agent.

    Args:
        agent_id (str): The agent_id for the forecasting or prediction use case and previously defined input_data_model
        input_data (Dict[str, Union[str, dict, List[dict]]]): The forecast inputs that you will pass to the chronulus agent to make the prediction. The keys of the dict should correspond to the InputField name you provided in input_fields.
        num_experts (int): The number of experts to consult when forming consensus.

    Returns:
        Union[str, Dict[str, Union[dict, str]]]: a dictionary with prediction data, a text explanation of the predictions, agent_id, and probability estimate.
    """

    agent = BinaryPredictor.load_from_saved_estimator(estimator_id=agent_id, verbose=False)
    item = agent.input_type(**input_data)

    try:
        req = agent.queue(item, num_experts=num_experts, note_length=(5,10))
    except Exception as e:
        return f"""Error at nf_agent: {str(e)}"""

    try:
        prediction_set = agent.get_request_predictions(req.request_id)
        return {
            "agent_id": agent.estimator_id,
            "request_id": req.request_id,
            "beta_params": prediction_set.beta_params,
            'expert_opinions': [p.text for p in prediction_set],
            'probability': prediction_set.prob_a}

    except Exception as e:
        return f"""Error on prediction: {str(e)}"""




