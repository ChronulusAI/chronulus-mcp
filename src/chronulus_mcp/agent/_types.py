from typing import Type, Annotated, List, Dict, Literal, Optional, Union


from pydantic import Field, BaseModel, create_model
from chronulus_core.types.attribute import ImageFromFile, TextFromFile, Text, PdfFromFile

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



def generate_model_from_fields(model_name: str, fields: List[InputField]) -> Type[BaseModel]:
    """
    Generate a new Pydantic BaseModel from a list of InputField objects.

    Args:
        model_name: The name for the generated model class
        fields: List of InputField objects defining the model's fields

    Returns:
        A new Pydantic BaseModel class with the specified fields
    """
    literal_type_mapping = {
        'str': str,
        'ImageFromFile': ImageFromFile,
        'List[ImageFromFile]': List[ImageFromFile],
        'TextFromFile': TextFromFile,
        'List[TextFromFile]': List[TextFromFile],
        'PdfFromFile': PdfFromFile,
        'List[PdfFromFile]': List[PdfFromFile]
    }

    field_definitions = {
        field.name: (
            Optional[literal_type_mapping.get(field.type, str)],
            Field(description=field.description)
        )
        for field in fields
    }

    DynamicModel = create_model(
        model_name,
        __base__=BaseModel,  # Explicitly set BaseModel as the base class
        **field_definitions
    )

    DynamicModel.__annotations__ = {
        field.name: str for field in fields
    }

    return DynamicModel