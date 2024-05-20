def handle_ops(path):
    name = path.split("/")[-1]
    image_name = name.split(".")[0]
    final_name = image_name + ".png"
    return final_name

def change_ops(path):
    return path.replace(" ", "_")

def multi(n,n1):
    return n*n1