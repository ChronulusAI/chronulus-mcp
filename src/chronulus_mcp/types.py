from typing import Literal

from pydantic import Field, BaseModel


class InputField(BaseModel):
    name: str = Field(description="Field name. Should be a valid python variable name.")
    description: str = Field(description="A description of the value you will pass in the field.")
    type: Literal[
        'str', 'Text', 'List[Text]', 'TextFromFile', 'List[TextFromFile]', 'PdfFromFile', 'List[PdfFromFile]', 'ImageFromFile', 'List[ImageFromFile]'
    ] = Field(
        default='str',
        description="""The type of the field. 
        ImageFromFile takes a single named-argument, 'file_path' as input which should be absolute path to the image to be included. So you should provide this input as json, eg. {'file_path': '/path/to/image'}.
        """
    )


class DataRow(BaseModel):
    dt: str = Field(description="The value of the date or datetime field")
    y_hat: float = Field(description="The value of the y_hat field")
