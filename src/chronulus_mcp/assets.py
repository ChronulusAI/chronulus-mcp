from importlib import resources

#



def get_react_component(filename: str) -> str:
    """
    Get the code for a react template.

    Returns
    -------
    str
        React template source code
    """
    # Get the package directory
    for file in resources.files("chronulus_mcp._assets.react").iterdir():
        if file.is_file() and file.name == filename:
            contents = file.read_text()
            return contents

    raise FileNotFoundError(filename)



def get_html_template(filename: str) -> str:
    """
    Get the code for a html template.

    Returns
    -------
    str
        Html template source code
    """
    # Get the package directory
    for file in resources.files("chronulus_mcp._assets.html").iterdir():
        if file.is_file() and file.name == filename:
            contents = file.read_text()
            return contents

    raise FileNotFoundError(filename)





