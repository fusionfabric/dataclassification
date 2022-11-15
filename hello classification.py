from dataclassification.run import RunClassificationEngine

productDirectory = "./samples/productdirectory"
config_folder = "./samples/config_folder"
app_name = "Sample Application"
ce = RunClassificationEngine(productDirectory, config_folder, app_name)
