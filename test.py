import argparse
import torch
import os
import cv2

from src.model import DeepQNet
from src.env import DinoGame


def get_args():
    parser = argparse.ArgumentParser("Use RL to play dinorun")
    parser.add_argument("--saved_folder", type=str, default="models")
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--output", type=str, default=os.path.join("output", "dino.mp4"))

    return parser.parse_args()


def test(opt):
    if torch.cuda.is_available():
        device = torch.device("cuda")
        torch.cuda.manual_seed(258)
    else:
        device = torch.device("cpu")
        torch.manual_seed(258)

    model = DeepQNet()
    checkpoint_path = os.path.join(opt.saved_folder, "dino.pth")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    env = DinoGame()
    state, raw_state, _, _ = env.step(0, True)
    state = torch.cat(tuple(state for _ in range(4)))[None, :, :, :]
    if torch.cuda.is_available():
        model.cuda()
        state = state.cuda()

    out = cv2.VideoWriter(opt.output, cv2.VideoWriter_fourcc(*"MJPG"), opt.fps, (600, 150))
    done = False
    while not done:
        prediction = model(state)[0]
        action = torch.argmax(prediction).item()
        next_state, raw_next_state, reward, done = env.step(action, True)
        out.write(raw_next_state)
        if torch.cuda.is_available():
            next_state = next_state.cuda()
        next_state = torch.cat((state[0, 1:, :, :], next_state))[None, :, :, :]
        state = next_state


if __name__ == "__main__":
    opt = get_args()
    test(opt)
