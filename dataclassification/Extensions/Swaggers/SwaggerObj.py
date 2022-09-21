import logging


class SwaggerObj:
    def __init__(self, root_directory, path: str, obj: object):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            filename=root_directory + "/data-classification.log",
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        if path is None or obj is None:
            logging.error("Path and object cannot be empty")
            raise TypeError("Path and object cannot be empty")
        items = path.split("/")
        shortPath = "/" + items[-2] + "/" + items[-1]
        self.path = path
        if "dataset-schema-OAS" in shortPath:
            shortPath = shortPath.replace("dataset-schema-OAS", "schema")
        self.shortPath = shortPath
        self.obj = obj
