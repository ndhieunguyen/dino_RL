from src.model import DeepQNet
from src.env import DinoGame
import torch
from torch import nn
import os
import random
import pickle
import numpy as np
import argparse


def get_args():
    parser = argparse.ArgumentParser("Use RL to play dinorun")
    parser.add_argument("--batch_size", type=int, default=64, help="The number of frame per batch")
    parser.add_argument("--optimizer", type=str, choices=["adam", "adamw"], default="adamw")
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--initial_epsilon", type=float, default=0.1)
    parser.add_argument("--final_epsilon", type=float, default=1e-4)
    parser.add_argument("--num_decay_iters", type=float, default=2000000)
    parser.add_argument("--num_iters", type=int, default=2000000)
    parser.add_argument("--replay_memory_size", type=int, default=50000, help="Number of epoches between testing phases")
    parser.add_argument("--saved_folder", type=str, default="models")

    args = parser.parse_args()
    return args


def train(opt):
    model = DeepQNet()

    if torch.cuda.is_available():
        device = torch.device("cuda")
        torch.cuda.manual_seed(42)
        model.cuda()
    else:
        device = torch.device("cpu")
        torch.manual_seed(42)

    optimizer = torch.optim.AdamW(model.parameters(), lr=opt.lr)

    if not os.path.isdir(opt.saved_folder):
        os.makedirs(opt.saved_folder)
    checkpoint_path = os.path.join(opt.saved_folder, "dino.pth")
    memory_path = os.path.join(opt.saved_folder, "replay_memory.pkl")

    if os.path.isfile(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=device)
        iter = checkpoint["iter"] + 1
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        print("Load trained model from iteration {}".format(iter))
    else:
        iter = 0

    if os.path.isfile(memory_path):
        with open(memory_path, "rb") as f:
            replay_memory = pickle.load(f)
        print("Load replay memory")
    else:
        replay_memory = []

    criterion = nn.MSELoss()
    env = DinoGame()
    state, _, _ = env.step(0)
    state = torch.cat(tuple(state for _ in range(4)))[None, :, :, :]

    while iter < opt.num_iters:
        if torch.cuda.is_available():
            prediction = model(state.cuda())[0]
        else:
            prediction = model(state)[0]

        # Threshold for choosing exploration or exploitation
        epsilon = opt.final_epsilon + (
            max(opt.num_decay_iters - iter, 0) * (opt.initial_epsilon - opt.final_epsilon) / opt.num_decay_iters
        )
        u = random.random()
        random_action = u <= epsilon
        if random_action:
            action = random.randint(0, 2)  # Exploration
        else:
            action = torch.argmax(prediction).item()  # Exploitation

        next_state, reward, done = env.step(action)
        next_state = torch.cat((state[0, 1:, :, :], next_state))[None, :, :, :]
        replay_memory.append([state, action, reward, next_state, done])
        if len(replay_memory) > opt.replay_memory_size:
            del replay_memory[0]
        batch = random.sample(replay_memory, min(len(replay_memory), opt.batch_size))
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)

        state_batch = torch.cat(tuple(state for state in state_batch))
        action_batch = torch.from_numpy(
            np.array(
                [[1, 0, 0] if action == 0 else [0, 1, 0] if action == 1 else [0, 0, 1] for action in action_batch],
                dtype=np.float32,
            )
        )
        reward_batch = torch.from_numpy(np.array(reward_batch, dtype=np.float32)[:, None])
        next_state_batch = torch.cat(tuple(state for state in next_state_batch))

        if torch.cuda.is_available():
            state_batch = state_batch.cuda()
            action_batch = action_batch.cuda()
            reward_batch = reward_batch.cuda()
            next_state_batch = next_state_batch.cuda()
        current_prediction_batch = model(state_batch)
        next_prediction_batch = model(next_state_batch)

        y_batch = torch.cat(
            tuple(
                reward if done else reward + opt.gamma * torch.max(prediction)
                for reward, done, prediction in zip(reward_batch, done_batch, next_prediction_batch)
            )
        )

        q_value = torch.sum(current_prediction_batch * action_batch, dim=1)
        optimizer.zero_grad()
        loss = criterion(q_value, y_batch)
        loss.backward()
        optimizer.step()

        state = next_state
        iter += 1
        print(
            "Iteration: {}/{}, Loss: {:.5f}, Epsilon {:.5f}, Reward: {}".format(iter + 1, opt.num_iters, loss, epsilon, reward)
        )
        if (iter + 1) % 50000 == 0:
            checkpoint = {"iter": iter, "model_state_dict": model.state_dict(), "optimizer": optimizer.state_dict()}
            torch.save(checkpoint, checkpoint_path)
            with open(memory_path, "wb") as f:
                pickle.dump(replay_memory, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    opt = get_args()
    train(opt)
