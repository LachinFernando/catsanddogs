def handle_ops(path):
    name = path.split("/")[-1]
    image_name = name.split(".")[0]
    final_name = image_name + ".png"
    return final_name