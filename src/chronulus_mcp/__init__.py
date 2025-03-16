import argparse

from mcp.server.fastmcp import FastMCP

from .assets import get_react_component
from chronulus_mcp.agent.forecaster import create_forecasting_agent_and_get_forecast, reuse_forecasting_agent_and_get_forecast, rescale_forecast
from chronulus_mcp.agent.predictor import create_prediction_agent_and_get_predictions, reuse_prediction_agent_and_get_prediction
from .session import create_chronulus_session, get_risk_assessment_scorecard
from .io import save_forecast, save_prediction_analysis_html

SERVER_DESCRIPTION_V1 = "Chronulus MCP provides access to the Chronulus AI platform of forecasting and prediction agents."

SERVER_DESCRIPTION_V2 = """
choronulus-agents server provides access to the Chronulus AI platform of forecasting and prediction agents.

- Sessions capture an overall use case that is described by a situation and task.
- Agents created for a given session and are reusable across multiple different forecasting inputs.
- Input features can include text or files including images, text, or pdf (provide the path to the file)
- The total size of all inputs cannot exceed 10MB. So plan according when choosing inputs

For example, in a retail forecasting workflow, 
    - The situation might include information about the business, location, demographics of customers, and motivation for forecasting
    - The task would include specifics about what to forecast like the demand, share of foot traffic, probability of the item going out of stock, etc.
    - The agent could be used for multiple different types of items with a single data model.  For example a data model with brand and price feature could
    be used to predict over multiple items with their own values for brand and price.
"""

mcp = FastMCP("chronulus-agents", instructions=SERVER_DESCRIPTION_V2)


##############################################################################
#   SESSION
##############################################################################

CREATE_SESSION_DESCRIPTION = """
A tool that creates a new Chronulus Session and returns a session_id

When to use this tool:
- Use this tool when a user has requested a forecast or prediction for a new use case
- Before calling this tool make sure you have enough information to write a well-defined situation and task. You might
need to ask clarifying questions in order to get this from the user.
- The same session_id can be reused as long as the situation and task remain the same
- If user wants to forecast a different use case, create a new session and then use that

How to use this tool:
- To create a session, you need to provide a situation and task that describe the forecasting use case 
- If the user has not provided enough detail for you to decompose the use case into a 
    situation (broad or background context) and task (specific requirements for the forecast), 
    ask them to elaborate since more detail will result in a better / more accurate forecast.
- Once created, this will generate a unique session_id that can be used to when calling other tools about this use case.
"""

# session tools
mcp.add_tool(create_chronulus_session, description=CREATE_SESSION_DESCRIPTION)


FILE_TYPE_INSTRUCTIONS = """
- Remember to pass all relevant information to Chronulus including text and images provided by the user. 
- If a user gives you files about a thing you are forecasting or predicting, you should pass these as inputs to the 
agent using one of the following types: 
    - ImageFromFile
    - List[ImageFromFile]
    - TextFromFile
    - List[TextFromFile]
    - PdfFromFile
    - List[PdfFromFile]
- If you have a large amount of text (over 500 words) to pass to the agent, you should use the Text or List[Text] field types
""".strip()


##############################################################################
#   FORECASTING AGENT
##############################################################################

CREATE_AGENT_AND_GET_FORECAST_DESCRIPTION = f"""
This tool creates a NormalizedForecaster agent with your session and input data model and then provides a forecast input 
data to the agent and returns the prediction data and text explanation from the agent.

When to use this tool:
- Use this tool to request a forecast from Chronulus
- This tool is specifically made to forecast values between 0 and 1 and does not require historical data
- The prediction can be thought of as seasonal weights, probabilities, or shares of something as in the decimal representation of a percent

How to use this tool:
- First, make sure you have a session_id for the forecasting or prediction use case.
- Next, think about the features / characteristics most suitable for producing the requested forecast and then 
create an input_data_model that corresponds to the input_data you will provide for the thing being forecasted.
{FILE_TYPE_INSTRUCTIONS}
- Finally, add information about the forecasting horizon and time scale requested by the user
- Assume the dates and datetimes in the prediction results are already converted to the appropriate local timezone if location is a factor in the use case. So do not try to convert from UTC to local time when plotting.
- When plotting the predictions, use a Rechart time series with the appropriate axes labeled and with the prediction explanation displayed as a caption below the plot
"""

REUSE_AGENT_AND_GET_FORECAST_DESCRIPTION = f"""
This tool provides a forecast input to a previous created Chronulus NormalizedForecaster agent and returns the
    prediction data and text explanation from the agent.

When to use this tool:
- Use this tool to request a forecast from a Chronulus agent that you have already created and when your input data model is unchanged
- This tool is specifically made to forecast values between 0 and 1 and does not require historical data
- The prediction can be thought of as seasonal weights, probabilities, or shares of something as in the decimal representation of a percent

How to use this tool:
- First, make sure you have an agent_id for the agent. The agent is already attached to the correct session. So you do not need to provide a session_id.
- Next, reference the input data model that you previously used with the agent and create new inputs for the item being forecast
    that align with the previously specified input data model
{FILE_TYPE_INSTRUCTIONS}
- Finally, add information about the forecasting horizon and time scale requested by the user
- Assume the dates and datetimes in the prediction results are already converted to the appropriate local timezone if location is a factor in the use case. So do not try to convert from UTC to local time when plotting.
- When plotting the predictions, use a Rechart time series with the appropriate axes labeled and with the prediction explanation displayed as a caption below the plot
"""

RESCALE_PREDICTIONS_DESCRIPTION = """
A tool that rescales the prediction data (values between 0 and 1) from the NormalizedForecaster agent to scale required for a use case

When to use this tool:
- Use this tool when there is enough information from the user or use cases to determine a reasonable min and max for the forecast predictions
- Do not attempt to rescale or denormalize the predictions on your own without using this tool.
- Also, if the best min and max for the use case is 0 and 1, then no rescaling is needed since that is already the scale of the predictions.
- If a user requests to convert from probabilities to a unit in levels, be sure to caveat your use of this tool by noting that
    probabilities do not always scale uniformly to levels. Rescaling can be used as a rough first-pass estimate. But for best results, 
    it would be better to start a new Chronulus forecasting use case predicting in levels from the start.
    
How to use this tool:
- To use this tool present prediction_id from the normalized prediction and the min and max as floats
- If the user is also changing units, consider if the units will be inverted and set the inverse scale to True if needed.
- When plotting the rescaled predictions, use a Rechart time series plot with the appropriate axes labeled and include the chronulus 
    prediction explanation as a caption below the plot. 
- If you would like to add additional notes about the scaled series, put these below the original prediction explanation. 
"""

SAVE_FORECAST_DESCRIPTION = """
A tool that saves a Chronulus forecast from NormalizedForecaster to separate CSV and TXT files

When to use this tool:
- Use this tool when you need to save both the forecast data and its explanation to files
- The forecast data will be saved as a CSV file for data analysis
- The forecast explanation will be saved as a TXT file for reference
- Both files will be saved in the same directory specified by output_path
- This tool can also be used to directly save rescaled predictions without first calling the rescaling tool

How to use this tool:
- Provide the prediction_id from a previous forecast
- Specify the output_path where both files should be saved
- Provide csv_name for the forecast data file (must end in .csv)
- Provide txt_name for the explanation file (must end in .txt)
- Optionally provide y_min and y_max to rescale the predictions (defaults to 0)
- Set invert_scale to True if the target units run in the opposite direction
- The tool will provide status updates through the MCP context
"""

# forecasting agent tools
mcp.add_tool(create_forecasting_agent_and_get_forecast, description=CREATE_AGENT_AND_GET_FORECAST_DESCRIPTION)
mcp.add_tool(reuse_forecasting_agent_and_get_forecast, description=CREATE_AGENT_AND_GET_FORECAST_DESCRIPTION)
mcp.add_tool(rescale_forecast, description=RESCALE_PREDICTIONS_DESCRIPTION)
mcp.add_tool(save_forecast, description=SAVE_FORECAST_DESCRIPTION)


##############################################################################
#   Prediction Agent
##############################################################################

CREATE_AGENT_AND_GET_PREDICTION_DESCRIPTION = f"""
This tool creates a BinaryPredictor agent with your session and input data model and then provides prediction input 
data to the agent and returns the consensus a prediction from a panel of experts along with their individual estimates
and text explanations. The agent also returns the alpha and beta parameters for a Beta distribution that allows you to
estimate the confidence interval of its consensus probability estimate.

When to use this tool:
- Use this tool to request a probability estimate from Chronulus in situation when there is a binary outcome
- This tool is specifically made to estimate the probability of an event occurring and not occurring and does not 
require historical data

How to use this tool:
- First, make sure you have a session_id for the prediction use case.
- Next, think about the features / characteristics most suitable for producing the requested prediction and then 
create an input_data_model that corresponds to the input_data you will provide for the thing or event being predicted.
{FILE_TYPE_INSTRUCTIONS}
- Finally, provide the number of experts to consult. The minimum and default number is 2, but users may request up to 30
30 opinions in situations where reproducibility and risk sensitively is of the utmost importance. In most cases, 2 to 5 
experts is sufficient. 
"""

REUSE_AGENT_AND_GET_PREDICTION_DESCRIPTION = f"""
This tool provides prediction input data to a previously created Chronulus BinaryPredictor agent and returns the 
consensus a prediction from a panel of experts along with their individual estimates and text explanations. The agent 
also returns the alpha and beta parameters for a Beta distribution that allows you to estimate the confidence interval 
of its consensus probability estimate.

When to use this tool:
- Use this tool to request a prediction from a Chronulus prediction agent that you have already created and when your 
input data model is unchanged
- Use this tool to request a probability estimate from an existing prediction agent in a situation when there is a binary outcome
- This tool is specifically made to estimate the probability of an event occurring and not occurring and does not 
require historical data

How to use this tool:
- First, make sure you have a session_id for the prediction use case.
- Next, think about the features / characteristics most suitable for producing the requested prediction and then 
create an input_data_model that corresponds to the input_data you will provide for the thing or event being predicted.
{FILE_TYPE_INSTRUCTIONS}
- Finally, provide the number of experts to consult. The minimum and default number is 2, but users may request up to 30
30 opinions in situations where reproducibility and risk sensitively is of the utmost importance. In most cases, 2 to 5 
experts is sufficient. 

How to use this tool:
- First, make sure you have an agent_id for the prediction agent. The agent is already attached to the correct session. 
So you do not need to provide a session_id.
- Next, reference the input data model that you previously used with the agent and create new input data for the item 
being predicted that aligns with the previously specified input data model
{FILE_TYPE_INSTRUCTIONS}
- Finally, provide the number of experts to consult. The minimum and default number is 2, but users may request up to 30
30 opinions in situations where reproducibility and risk sensitively is of the utmost importance. In most cases, 2 to 5 
experts is sufficient. 
"""

SAVE_ANALYSIS_HTML_DESCRIPTION = """
A tool that saves an analysis of a BinaryPredictor prediction to HTML. 

The analysis includes a plot of the theoretical and empirical beta distribution estimated by Chronulus and also
list the opinions provided by each expert.

When to use this tool:
- Use this tool when you need to save the BinaryPredictor estimates to for the user

How to use this tool:
- Provide the request_id from a previous prediction response
- Specify the output_path where the html should be saved
- Provide html_name for the file (must end in .html)
- The tool will provide status updates through the MCP context
"""

# prediction agent
mcp.add_tool(create_prediction_agent_and_get_predictions, description=CREATE_AGENT_AND_GET_PREDICTION_DESCRIPTION)
mcp.add_tool(reuse_prediction_agent_and_get_prediction, description=REUSE_AGENT_AND_GET_PREDICTION_DESCRIPTION)
mcp.add_tool(save_prediction_analysis_html, description=SAVE_ANALYSIS_HTML_DESCRIPTION)

##############################################################################
#   Extras
##############################################################################

GET_RISK_ASSESSMENT_SCORECARD_DESCRIPTION = """
A tool that retrieves the risk assessment scorecard for the Chronulus Session in Markdown format

When to use this tool:
- Use this tool when the use asks about the risk level or safety concerns of a forecasting use case
- You may also use this tool to provide justification to a user if you would like to warn them of the implications of 
    what they are asking you to forecasting or predict.

How to use this tool:
- Make sure you have a session_id for the forecasting or prediction use case
- When displaying the scorecard markdown for the user, you should use an MDX-style React component
"""

RESOURCE_GET_RISK_ASSESSMENT_SCORECARD_DESCRIPTION = """
A resource that retrieves the risk assessment scorecard for the Chronulus Session in Markdown or JSON format

When to use this resource:
- Use this tool when the use asks about the risk level or safety concerns of a forecasting use case
- You may also use this tool to provide justification to a user if you would like to warn them of the implications of 
    what they are asking you to forecasting or predict.

How to use this resource:
- Make sure you have a session_id for the forecasting or prediction use case
- To display the scorecard use the provided react resource at 'chronulus-react://Scorecard.jsx'
"""

# extra
mcp.add_tool(get_risk_assessment_scorecard, description=GET_RISK_ASSESSMENT_SCORECARD_DESCRIPTION)


@mcp.resource(
    uri="chronulus-react://Scorecard.jsx",
    name="Scorecard React Template",
    mime_type="text/javascript",
)
def get_scorecard_react_template() -> str:
    """Get scorecard.tsx"""
    return get_react_component("Scorecard.jsx")


@mcp.resource(
    uri="chronulus-react://BetaPlot.jsx",
    name="Beta Plot",
    mime_type="text/javascript",
)
def get_scorecard_react_template() -> str:
    """Get BetaPlot.jsx"""
    return get_react_component("BetaPlot.jsx")




def main():
    """Chronulus AI: A platform for the forecasting and prediction. Predict anything."""
    parser = argparse.ArgumentParser(description=SERVER_DESCRIPTION_V1)
    parser.parse_args()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()