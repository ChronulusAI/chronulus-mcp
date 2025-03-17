import os
from typing import Annotated, Optional
import math

from mcp.server.fastmcp import Context
from pydantic import Field
from datetime import datetime

from chronulus.estimator import NormalizedForecaster
from chronulus.estimator import BinaryPredictor
from chronulus.prediction import RescaledForecast

from chronulus_mcp.assets import get_html_template


async def save_forecast(
    prediction_id: Annotated[str, Field(description="The prediction_id from a prediction result")],
    output_path: Annotated[str, Field(description="The path where the CSV file should be saved. Should end in .csv")],
    csv_name: Annotated[str, Field(description="The path where the CSV file should be saved. Should end in .csv")],
    txt_name: Annotated[str, Field(description="The name of the TXT file to be saved. Should end in .txt")],
    ctx: Context,
    y_min: Annotated[float, Field(default=0.0, description="The expected smallest value for the use case. E.g., for product sales, 0 would be the least possible value for sales.")],
    y_max: Annotated[float, Field(default=1.0, description="The expected largest value for the use case. E.g., for product sales, 0 would be the largest possible value would be given by the user or determined from this history of sales for the product in question or a similar product.")],
    invert_scale: Annotated[bool, Field(default=False, description="Set this flag to true if the scale of the new units will run in the opposite direction from the inputs.")],
) -> str:
    """Saves the forecast from a NormalizedForecaster agent to CSV and the explanation to TXT

    Args:
        prediction_id (str): The prediction_id for the prediction you would like to rescale as returned by the forecasting agent
        output_path (str): The path where the CSV and TXT file should be saved.
        csv_name (str): The name of the CSV file to be saved. Should end in .csv
        txt_name (str): The name of the TXT file to be saved. Should end in .txt
        ctx (Context): Context object providing access to MCP capabilities.
        y_min (float): The expected smallest value for the use case. E.g., for product sales, 0 would be the least possible value for sales.
        y_max (float): The expected largest value for the use case. E.g., for product sales, 0 would be the largest possible value would be given by the user or determined from this history of sales for the product in question or a similar product.
        invert_scale (bool): Set this flag to true if the scale of the new units will run in the opposite direction from the inputs.


    Returns:
        str: A message confirming the file was saved and its location
    """
    # Get normalized forecast and rescale it
    _ = await ctx.info(f"Fetching prediction data for {prediction_id}")
    normalized_forecast = NormalizedForecaster.get_prediction_static(prediction_id, verbose=False)
    rescaled_forecast = RescaledForecast.from_forecast(
        forecast=normalized_forecast,
        y_min=y_min,
        y_max=y_max,
        invert_scale=invert_scale
    )

    # Convert to pandas using built-in method
    df = rescaled_forecast.to_pandas()

    # Save to CSV
    df.to_csv(os.path.join(output_path, csv_name), index_label="ds")

    with open(os.path.join(output_path, txt_name), "w") as f:
        f.write(normalized_forecast.text)

    return f"Forecast saved successfully to {output_path}"



async def save_prediction_analysis_html(
    request_id: Annotated[str, Field(description="The request_id from the BinaryPredictor result")],
    output_path: Annotated[str, Field(description="The path where the HTML file should be saved.")],
    html_name: Annotated[str, Field(description="The path where the HTML file should be saved.")],
    title: Annotated[str, Field(description="Title of analysis")],
    plot_label: Annotated[str, Field(description="Label for the Beta plot")],
    chronulus_prediction_summary: Annotated[str, Field(description="A summary paragraph distilling prediction results and expert opinions provided by Chronulus")],
    dist_shape: Annotated[str, Field(description="A one line description of the shape of the distribution of predictions")],
    dist_shape_interpretation: Annotated[str, Field(description="2-3 sentences interpreting the shape of the distribution of predictions in layman's terms")],
    #ctx: Context,
) -> str:
    """Saves the analysis from a BinaryPredictor prediction to an HTML file

    Args:
        request_id (str): The request_id from the BinaryPredictor result
        output_path (str): The path where the CSV and TXT file should be saved.
        html_name (str): The name of the HTML file to be saved. Should end in .html
        title (str): Title of analysis
        plot_label (str): Label for the Beta plot
        chronulus_prediction_summary (str) : A summary paragraph distilling prediction results and expert opinions provided by Chronulus
        dist_shape (str) : A one line description of the shape of the distribution of predictions
        dist_shape_interpretation (str) : A 2-3 sentences interpreting the shape of the distribution of predictions in layman's terms

    Returns:
        str: A message confirming the file was saved and its location
    """
    # Get normalized forecast and rescale it
    #_ = await ctx.info(f"Fetching prediction data for request_id: {request_id}")

    html = get_html_template("binary_predictor_analysis.html")

    prediction_set = BinaryPredictor.get_request_predictions_static(request_id, verbose=False)

    mean = prediction_set.prob_a
    a, b = prediction_set.beta_params.alpha, prediction_set.beta_params.beta
    variance = (a*b) / (((a+b)**2)*(a+b+1))
    stdev = math.sqrt(variance)
    divergent = a <= 1 or b <= 1
    mode = (a - 1) / (a + b - 2)
    mode_txt = f"{mode: 16.4f}" if not divergent else 'Diverges'

    html = html.replace("[TITLE_OF_ANALYSIS]", title)
    html = html.replace("[PLOT_LABEL]", plot_label)
    html = html.replace("[CHRONULUS_PREDICTION_SUMMARY]", chronulus_prediction_summary)
    html = html.replace("[DIST_SHAPE_DESCRIPTION]", dist_shape)
    html = html.replace("[DIST_SHAPE_INTERPRETATION]", dist_shape_interpretation)
    html = html.replace("[ALPHA]", f"{a: 16.16f}")
    html = html.replace("[BETA]", f"{b: 16.16f}")
    html = html.replace("[MEAN]", f"{mean: 16.4f}")
    html = html.replace("[VARIANCE]", f"{variance: 16.4f}")
    html = html.replace("[STDEV]", f"{stdev: 16.4f}")
    html = html.replace("[MODE]", mode_txt)

    date = datetime.today().strftime("%B %d, %Y")
    html = html.replace("[DATE]", date)

    expert_opinion_list = []
    for i, p in enumerate(prediction_set):
        pos_text = p.opinion_set.positive.text
        neg_text = p.opinion_set.negative.text
        pos = f"""
        <div class="expert-opinion positive-case">
            <h3>Expert {i+1} - Positive Case</h3>
                <pre>{pos_text}</pre>
        </div>
        """
        neg = f"""
        <div class="expert-opinion negative-case">
            <h3>Expert {i+1} - Negative Case</h3>
                <pre>{neg_text}</pre>
        </div>
        """
        expert_opinion_list.append(pos)
        expert_opinion_list.append(neg)

    expert_opinions = "\n\n".join(expert_opinion_list)

    html = html.replace("[EXPERT_OPINIONS]", expert_opinions)


    with open(os.path.join(output_path, html_name), "w") as f:
        f.write(html)

    return f"BinaryPredictor analysis saved successfully to {output_path}"