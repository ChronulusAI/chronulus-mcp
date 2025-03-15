import json
from datetime import datetime
from typing import Annotated, List, Dict, Union

from mcp.server.fastmcp import Context
from pydantic import Field

from ._types import InputField, DataRow, generate_model_from_fields

from chronulus import Session
from chronulus.estimator import NormalizedForecaster
from chronulus.prediction import RescaledForecast



async def create_forecasting_agent_and_get_forecast(
        session_id: Annotated[str, Field(description="The session_id for the forecasting or prediction use case")],
        input_data_model: Annotated[List[InputField], Field(
            description="""Metadata on the fields you will include in the input_data."""
        )],
        input_data: Annotated[Dict[str, Union[str, dict, List[dict]]], Field(description="The forecast inputs that you will pass to the chronulus agent to make the prediction. The keys of the dict should correspond to the InputField name you provided in input_fields.")],
        forecast_start_dt_str: Annotated[str, Field(description="The datetime str in '%Y-%m-%d %H:%M:%S' format of the first value in the forecast horizon.")],
        ctx: Context,
        time_scale: Annotated[str, Field(description="The times scale of the forecast horizon. Valid time scales are 'hours', 'days', and 'weeks'.", default="days")],
        horizon_len: Annotated[int, Field(description="The integer length of the forecast horizon. Eg., 60 if a 60 day forecast was requested.", default=60)],
) -> Union[str, Dict[str, Union[dict, str]]]:
    """Queues and retrieves a forecast from Chronulus with a predefined session_id

    This tool creates a NormalizedForecaster agent and then provides a forecast input to the agent and returns the prediction data and
    text explanation from the agent.

    Args:
        session_id (str): The session_id for the forecasting or prediction use case.
        input_data_model (List[InputField]): Metadata on the fields you will include in the input_data. Eg., for a field named "brand", add a description like "the brand of the product to forecast"
        input_data (Dict[str, Union[str, dict, List[dict]]]): The forecast inputs that you will pass to the chronulus agent to make the prediction. The keys of the dict should correspond to the InputField name you provided in input_fields.
        forecast_start_dt_str (str): The datetime str in '%Y-%m-%d %H:%M:%S' format of the first value in the forecast horizon."
        ctx (Context): Context object providing access to MCP capabilities.
        time_scale (str): The times scale of the forecast horizon. Valid time scales are 'hours', 'days', and 'weeks'.
        horizon_len (int): The integer length of the forecast horizon. Eg., 60 if a 60 day forecast was requested.

    Returns:
        Union[str, Dict[str, Union[dict, str]]]: a dictionary with prediction data, a text explanation of the predictions, estimator_id, and the prediction id.
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
        nf_agent = NormalizedForecaster(
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
        forecast_start_dt = datetime.fromisoformat(forecast_start_dt_str)
        horizon_params = {
            'start_dt': forecast_start_dt,
            time_scale: horizon_len
        }
        req = nf_agent.queue(item, **horizon_params)
    except Exception as e:
        return f"""Error at nf_agent: {str(e)}"""

    try:
        predictions = nf_agent.get_predictions(req.request_id)
        prediction = predictions[0]
        return {
            "agent_id": nf_agent.estimator_id,
            "prediction_id": prediction.id,
            'data': prediction.to_json(orient='rows'),
            'explanation': prediction.text}

    except Exception as e:
        return f"""Error on prediction: {str(e)}"""


async def reuse_forecasting_agent_and_get_forecast(
        agent_id: Annotated[str, Field(description="The agent_id for the forecasting or prediction use case and previously defined input_data_model")],
        input_data: Annotated[Dict[str, Union[str, dict, List[dict]]], Field(
            description="The forecast inputs that you will pass to the chronulus agent to make the prediction. The keys of the dict should correspond to the InputField name you provided in input_fields.")],
        forecast_start_dt_str: Annotated[str, Field(
            description="The datetime str in '%Y-%m-%d %H:%M:%S' format of the first value in the forecast horizon.")],
        time_scale: Annotated[str, Field(
            description="The times scale of the forecast horizon. Valid time scales are 'hours', 'days', and 'weeks'.",
            default="days")],
        horizon_len: Annotated[int, Field(
            description="The integer length of the forecast horizon. Eg., 60 if a 60 day forecast was requested.",
            default=60)],
) -> Union[str, Dict[str, Union[dict, str]]]:
    """Queues and retrieves a forecast from Chronulus with a previously created agent_id

    This tool provides a forecast input to a previous created Chronulus NormalizedForecaster agent and returns the
    prediction data and text explanation from the agent.

    Args:
        agent_id (str): The agent_id for the forecasting or prediction use case and previously defined input_data_model
        input_data (Dict[str, Union[str, dict, List[dict]]]): The forecast inputs that you will pass to the chronulus agent to make the prediction. The keys of the dict should correspond to the InputField name you provided in input_fields.
        forecast_start_dt_str (str): The datetime str in '%Y-%m-%d %H:%M:%S' format of the first value in the forecast horizon."
        time_scale (str): The times scale of the forecast horizon. Valid time scales are 'hours', 'days', and 'weeks'.
        horizon_len (int): The integer length of the forecast horizon. Eg., 60 if a 60 day forecast was requested.

    Returns:
        Union[str, Dict[str, Union[dict, str]]]: a dictionary with prediction data, a text explanation of the predictions, agent_id, and the prediction id.
    """

    nf_agent = NormalizedForecaster.load_from_saved_estimator(estimator_id=agent_id, verbose=False)
    item = nf_agent.input_type(**input_data)

    try:
        forecast_start_dt = datetime.fromisoformat(forecast_start_dt_str)
        horizon_params = {
            'start_dt': forecast_start_dt,
            time_scale: horizon_len
        }
        req = nf_agent.queue(item, **horizon_params)
    except Exception as e:
        return f"""Error at nf_agent: {str(e)}"""

    try:
        predictions = nf_agent.get_predictions(req.request_id)
        prediction = predictions[0]
        return {
            "agent_id": nf_agent.estimator_id,
            "prediction_id": prediction.id,
            'data': prediction.to_json(orient='rows'),
            'explanation': prediction.text}

    except Exception as e:
        return f"""Error on prediction: {str(e)}"""


async def rescale_forecast(
    prediction_id: Annotated[str, Field(description="The prediction_id from a prediction result")],
    y_min: Annotated[float, Field(description="The expected smallest value for the use case. E.g., for product sales, 0 would be the least possible value for sales.")],
    y_max: Annotated[float, Field(description="The expected largest value for the use case. E.g., for product sales, 0 would be the largest possible value would be given by the user or determined from this history of sales for the product in question or a similar product.")],
    invert_scale: Annotated[bool, Field(description="Set this flag to true if the scale of the new units will run in the opposite direction from the inputs.", default=False)],
) -> List[dict]:
    """Rescales prediction data from the NormalizedForecaster agent

    Args:
        prediction_id (str) : The prediction_id for the prediction you would like to rescale as returned by the forecasting agent
        y_min (float) : The expected smallest value for the use case. E.g., for product sales, 0 would be the least possible value for sales.
        y_max (float) : The expected largest value for the use case. E.g., for product sales, 0 would be the largest possible value would be given by the user or determined from this history of sales for the product in question or a similar product.
        invert_scale (bool): Set this flag to true if the scale of the new units will run in the opposite direction from the inputs.

    Returns:
        List[dict] : The prediction data rescaled to suit the use case
    """

    normalized_forecast = NormalizedForecaster.get_prediction_static(prediction_id)
    rescaled_forecast = RescaledForecast.from_forecast(
        forecast=normalized_forecast,
        y_min=y_min,
        y_max=y_max,
        invert_scale=invert_scale
    )

    return [DataRow(dt=row.get('date',row.get('datetime')), y_hat=row.get('y_hat')).model_dump() for row in rescaled_forecast.to_json(orient='rows')]


