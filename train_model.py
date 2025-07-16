from human_mouse.human_mouse_stat_mj import train_mouse_model

def train_and_save_model():
    train_mouse_model("./csv_data", "mouse_model.pkl")

if __name__ == '__main__':
    train_and_save_model()