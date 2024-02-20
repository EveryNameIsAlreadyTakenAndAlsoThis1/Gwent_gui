import copy
import os
import random
import time

import cv2
import gym
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as init
import torch.optim as optim


class AgentPPO:
    def __init__(self, gamma, actions_count, model, lr=0.0003, beta_entropy=0.001, value_loss_coef=0.5, id=1,
                 name='ppo', epsilon=0.2, lr_decay=1e-6):
        self.gamma = gamma
        self.actions_count = actions_count
        self.model = model

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print('device: ', self.device)
        self.model.to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

        self.beta_entropy = beta_entropy
        self.value_loss_coef = value_loss_coef

        self.average_score = []
        self.episodes = 0
        self.upper_bound = 1 + epsilon
        self.lower_bound = 1 - epsilon

        self.id = id
        self.name = name

        self.lr = lr
        self.lr_decay = lr_decay

        self.model_directory_name = ''
        self.log_directory_name = ''

    def choose_action(self, state, mask):
        state = state.unsqueeze(0).to(self.device).float()
        with torch.no_grad():
            logits, _ = self.model(state)

        logits = torch.where(mask, logits, torch.tensor(-1e+8).to(self.device))

        probs = F.softmax(logits, dim=-1)
        probs = probs.cpu()
        action = probs.multinomial(num_samples=1).detach()

        while mask[action[0].item()] == False:
            action = probs.multinomial(num_samples=1).detach()
            print('Tunak sa to vykonalo')
        return action[0].item()

    def fix(self, mask):
        print("vsetci robime chyby, ale pytorch vedie")
        indexes = []
        i = 0
        for index in mask:
            if index == True:
                indexes.append(i)
            i += 1
        return random.choice(indexes)

    def write_to_file(self, log, filename):
        with open(filename, 'a') as file:
            file.write(log + '\n')

    def learn(self, workers, max_steps, max_iterations, best_score, write=True, start_iteration=0, max_epochs=4,
              batches_per_epoch=4):
        len_workers = len(workers)
        observations = []
        masks = []
        for worker in workers:
            obs, mask = worker.reset()
            observations.append(torch.from_numpy(obs).float())
            masks.append(mask)

        observations = torch.stack(observations)
        masks = torch.stack(masks)

        self.average_score = []
        self.episodes = 0
        best_avg = best_score

        max_steps_epochs = max_steps * batches_per_epoch

        text = 'iteration,episode,score,step'
        iter_step = max_steps_epochs * len_workers
        index_range = torch.arange(0, max_steps_epochs).long()

        for iteration in range(start_iteration, max_iterations):
            mem_values = torch.zeros([max_steps_epochs, len_workers, 1])
            mem_log_probs = torch.zeros([max_steps_epochs, len_workers, 1])
            mem_rewards = torch.zeros([max_steps_epochs, len_workers, 1])
            mem_non_terminals = torch.ones([max_steps_epochs, len_workers, 1])
            mem_actions = torch.zeros(max_steps_epochs, len_workers, 1).long()
            mem_observations = []
            mem_masks = []

            for step in range(max_steps_epochs):
                with torch.no_grad():
                    logits, values = self.model(observations.to(self.device))
                mem_observations.append(observations)
                mem_masks.append(masks)

                logits = torch.where(mem_masks[step], logits, torch.tensor(-1e+8).to(self.device))

                logits, values = logits.cpu(), values.cpu()
                probs = F.softmax(logits, dim=-1)
                log_probs = F.log_softmax(logits, dim=-1)

                actions = None

                while True:
                    actions = probs.multinomial(num_samples=1).detach()
                    everythingOk = True
                    for i in range(len(probs)):
                        if probs[i][actions[i][0].item()] == 0:
                            everythingOk = False

                    if everythingOk:
                        break
                    print("Všetci robíme chyby, ale pytorch vedie znova")

                log_policy = log_probs.gather(1, actions)

                rewards = torch.zeros([len_workers, 1])
                non_terminals = torch.ones([len_workers, 1])
                observations = []
                masks = []

                for i in range(len_workers):
                    o, rewards[i, 0], t, mask = workers[i].step(actions[i].item())

                    if t == True:
                        non_terminals[i, 0] = 0
                        o, mask = workers[i].reset()

                    observations.append(torch.from_numpy(o).float())
                    masks.append(mask)

                observations = torch.stack(observations)
                masks = torch.stack(masks)

                mem_values[step] = values
                mem_log_probs[step] = log_policy
                mem_rewards[step] = rewards
                mem_non_terminals[step] = non_terminals
                mem_actions[step] = actions

            with torch.no_grad():
                _, R = self.model(observations.to(self.device))
                R = R.detach().cpu()
                # mem_values[max_steps_epochs] = R

            avg = np.average(self.average_score[-100:])
            if avg > best_avg:
                best_avg = avg
                # print('saving model, best score is ', best_avg)
                torch.save(self.model.state_dict(),
                           self.model_directory_name + self.name + '_' + str(self.id) + '_ppo.pt')

            if iteration % 25 == 0 and iteration > 0:
                # print(iteration, '\tepisodes: ', self.episodes, '\taverage score: ', avg)
                if write:
                    text += '\n' + str(iteration) + ',' + str(self.episodes) + ',' + str(avg) + ',' + str(
                        iter_step * iteration)

                    if iteration % 100 == 0:
                        self.average_score = self.average_score[-100:]
                        write_to_file(text, self.log_directory_name + self.name + '_' + str(self.id) + '_' + str(
                            iteration) + '_ppo.txt')
                        torch.save(self.model.state_dict(),
                                   self.model_directory_name + self.name + '_' + str(self.id) + '_' + str(
                                       iteration) + '_ppo.pt')

            '''
            mem_R = torch.zeros([max_steps_epochs, len_workers, 1])
            advantages = torch.zeros([max_steps_epochs, len_workers, 1])
            #returns = torch.zeros([max_steps_epochs, len_workers, 1])
            #gae = torch.zeros(len_workers, 1)
            for step in reversed(range(max_steps_epochs)):
                R = mem_rewards[step] + self.gamma * R * mem_non_terminals[step]
                #delta = mem_rewards[step] + self.gamma * mem_values[step+1] * mem_non_terminals[step] - mem_values[
                step]
                #gae = gae * self.gamma * 0.95 + delta
                advantage[step] = R - mem_values[step]
            '''
            mem_R = torch.zeros([max_steps_epochs, len_workers, 1])
            advantages = torch.zeros([max_steps_epochs, len_workers, 1])

            for step in reversed(range(max_steps_epochs)):
                R = mem_rewards[step] + self.gamma * R * mem_non_terminals[step]
                mem_R[step] = R
                advantages[step] = R - mem_values[step]

            # mem_R = mem_rewards + self.gamma * mem_values[1:max_steps_epochs+1]
            # advantages = mem_R - mem_values[0:max_steps_epochs]

            # advantages = returns - mem_values[0:max_steps_epochs, :]
            # advantages = (advantages - torch.mean(advantages)) / (torch.std(advantages) + 1e-5)

            mem_observations = torch.stack(mem_observations)
            mem_masks = torch.stack(mem_masks)

            for epoch in range(max_epochs):
                index = index_range[torch.randperm(max_steps_epochs)].view(-1, max_steps)
                for batch in range(batches_per_epoch):
                    epoch_index = index[epoch]
                    states = mem_observations[epoch_index]
                    logits, values = self.model(states.to(self.device))
                    logits = torch.where(mem_masks[epoch_index], logits, torch.tensor(-1e+8).to(self.device))

                    logits = logits.flatten(0, 1)
                    values = values.flatten(0, 1)

                    logits, values = logits.cpu(), values.cpu()
                    probs = F.softmax(logits, dim=-1)
                    log_probs = F.log_softmax(logits, dim=-1)

                    log_new_policy = log_probs.gather(1, mem_actions[epoch_index].flatten(0, 1))
                    entropies = (log_probs * probs).sum(1, keepdim=True)

                    advantage = mem_R[epoch_index].view(-1, 1) - values
                    value_loss = (advantage ** 2).mean()

                    ratio = torch.exp(log_new_policy - mem_log_probs[epoch_index].view(-1, 1))

                    epoch_advangate = copy.deepcopy(advantages[epoch_index].view(-1, 1))

                    surr_policy = ratio * epoch_advangate
                    surr_clip = torch.clamp(ratio, self.lower_bound, self.upper_bound) * epoch_advangate
                    policy_loss = - torch.min(surr_policy, surr_clip).mean()
                    entropy_loss = entropies.mean()

                    self.optimizer.zero_grad()
                    loss = policy_loss + self.value_loss_coef * value_loss + self.beta_entropy * entropy_loss
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 0.1)
                    self.optimizer.step()

            if iteration % 25 == 0 and iteration > 0:
                self.lr = max(self.lr - self.lr_decay, 1e-7)
                self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        # print(f'Best score was: {best_avg}')

    def load_model(self):
        self.model.load_state_dict(torch.load(self.model_directory_name + self.name))
        self.old_model = copy.deepcopy(self.model)

    def save_model(self):
        torch.save(self.model.state_dict(), self.model_directory_name + self.name + '_' + str(self.id) + '_ppo.pt')


class Worker:
    def __init__(self, id, env, agent, print_score=False):
        self.id = id
        self.env = env

        self.print_score = print_score
        self.episode = 1
        self.state = None
        self.score = 0
        self.agent = agent

    def reset(self):
        if self.print_score and self.episode % 10 == 0:
            print('worker: ', self.id, '\tepisode: ', self.episode, '\tscore: ', self.score)
        self.agent.average_score.append(self.score)
        self.agent.episodes += 1
        self.state, _ = self.env.reset()
        self.mask = self.env.valid_action_mask()
        self.episode += 1
        self.score = 0
        return self.state, self.mask

    def step(self, action):
        self.state, r, t, _, _ = self.env.step(action)
        self.mask = self.env.valid_action_mask()
        self.score += r
        if r > 1.0:
            r = 1.0
        elif r < -1.0:
            r = -1.0
        return self.state, r, t, self.mask


class SkipEnv(gym.Wrapper):
    def __init__(self, env=None, skip=4):
        super(SkipEnv, self).__init__(env)
        self._skip = skip

    def step(self, action):
        t_reward = 0.0
        done = False

        for _ in range(self._skip):
            obs, reward, done, truncated, info = self.env.step(action)
            t_reward += reward
            if done:
                break
        return obs, t_reward, done, truncated, info


class PreProcessFrame(gym.ObservationWrapper):
    def __init__(self, env=None):
        super(PreProcessFrame, self).__init__(env)
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(96, 96, 1), dtype=np.uint8)

    def observation(self, obs):
        return PreProcessFrame.process(obs)

    @staticmethod
    def process(frame):
        new_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        new_frame = cv2.resize(new_frame[35:195, :], (96, 96), interpolation=cv2.INTER_AREA)
        new_frame = np.reshape(new_frame, (96, 96, 1))
        return new_frame.astype(np.uint8)


class MoveImgChannel(gym.ObservationWrapper):
    def __init__(self, env):
        super(MoveImgChannel, self).__init__(env)
        self.observation_space = gym.spaces.Box(low=0.0, high=1.0,
                                                shape=(self.observation_space.shape[-1],
                                                       self.observation_space.shape[0],
                                                       self.observation_space.shape[1]), dtype=np.float32)

    def observation(self, observation):
        return np.moveaxis(observation, 2, 0)


class ScaleFrame(gym.ObservationWrapper):
    def observation(self, obs):
        return np.array(obs).astype(np.float32) / 255.0


class BufferWrapper(gym.ObservationWrapper):
    def __init__(self, env, n_steps):
        super(BufferWrapper, self).__init__(env)
        self.observation_space = gym.spaces.Box(env.observation_space.low.repeat(n_steps, axis=0),
                                                env.observation_space.high.repeat(n_steps, axis=0),
                                                dtype=np.float32)

    def reset(self):
        self.buffer = np.zeros_like(self.observation_space.low, dtype=np.float32)
        obs, info = self.env.reset()

        return self.observation(obs), info

    def observation(self, observation):
        self.buffer[:-1] = self.buffer[1:]
        self.buffer[-1] = observation
        return self.buffer


def weights_init_xavier(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1 or classname.find('Linear') != -1:
        init.xavier_uniform_(m.weight)


def make_env(env_name):
    env = gym.make(env_name)
    env = SkipEnv(env)
    env = PreProcessFrame(env)
    env = MoveImgChannel(env)
    env = BufferWrapper(env, 4)
    return ScaleFrame(env)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()

        self.fc1 = nn.Linear(16 * 20 * 148, 64)
        self.fc2 = nn.Linear(64, 64)

        self.tanh1 = nn.Tanh()
        self.tanh2 = nn.Tanh()

        self.fc5 = nn.Linear(64, 463)
        self.fc6 = nn.Linear(64, 1)

        self.apply(weights_init_xavier)

    def forward(self, x):
        x = x.view(-1, 16 * 20 * 148)
        x = F.tanh(self.fc1(x))
        x = F.tanh(self.fc2(x))

        logit = self.fc5(x)
        value = self.fc6(x)
        return logit, value


def learning(num=1):
    actions = 6
    best_score = 0

    run_id = 1
    dir_path = f'/kaggle/working/{run_id}'

    os.makedirs(dir_path)

    agent = AgentPPO(0.99, actions, Net(), 0.001, beta_entropy=0.001, id=num, name=f'{dir_path}/pong.pt')
    # agent.model.load_state_dict(torch.load('/kaggle/input/projektovavyucba-pong/pong.pt_1_ppo.pt'))

    workers = []
    for id in range(16):
        env = make_env('PongNoFrameskip-v4')  # gym.make("ALE/Pong-v5", frameskip=1, full_action_space=False)
        env.seed(id)
        w = Worker(id, env, agent)
        workers.append(w)

    agent.learn(workers, 24, 2001, best_score)


def animation():
    actions = 4

    agent = AgentPPO(0.99, actions, Net(), lr=2.5e-4, beta_entropy=0.01, id=0, name='breakout/breakout_ppo.pt')
    # breakout/breakout_1_20000_a2c.pt'
    env = make_env('PongNoFrameskip-v4')
    agent.load_model()

    while True:
        terminal = False
        observation = env.reset()

        while not terminal:
            env.render()
            time.sleep(0.02)
            observation = torch.from_numpy(observation)
            action = agent.choose_action(observation)
            observation, _, terminal, _ = env.step(action)

    env.close()


def load_file(file_path):
    with open(file_path, 'r', encoding='unicode_escape') as f:
        data = f.read().splitlines()

    result = {}
    current_group = None

    for line in data:
        if line == '':
            continue

        if 'Northern Realms' in line or 'Scoiatael' in line or 'Neutral' in line or 'Nilfgaard' in line or 'Monsters' \
                in line:
            current_group = line.strip(',')
            result[current_group] = []
            continue

        name, _id, strength, ability, card_type, placement, count = line.split(',')

        if name == 'Name':
            continue

        result[current_group].append({
            'Name': name,
            'Id': int(_id),
            'Strength': int(strength),
            'Ability': ability,
            'Type': card_type,
            'Placement': int(placement),
            'Count': int(count),
            'Faction': current_group
        })

    return result


def mask_fn(env: gym.Env) -> np.ndarray:
    return env.valid_action_mask()


def load_file_game(file_path):
    """
    Load game data from a file and organizes it into a structured dictionary.

    Parameters:
    ----------
    file_path : str
        The path to the file containing the game data.

    Returns:
    -------
    dict
        A dictionary containing the organized game data, grouped by factions.

    Behavior:
    -----------
    - Opens the file located at `file_path` for reading.
    - Reads the data line-by-line, splitting it into different components, such as
      faction, name, id, strength, ability, card type, placement, and count.
    - Organizes the data into a dictionary, where each key represents a faction
      (e.g., Northern Realms, Scoiatael, Neutral, Nilfgaard, Monsters), and the
      corresponding value is a list of dictionaries containing the detailed information
      of each card associated with that faction.
    - Each card’s information dictionary includes keys like 'Name', 'Id', 'Strength',
      'Ability', 'Type', 'Placement', and 'Count', along with their respective values
      parsed from the file.
    - Empty lines and lines with column headers in the file are ignored.

    Example:
    -------
    The resulting dictionary might look something like this:
    {
        'Northern Realms': [
            {
                'Name': 'Card1',
                'Id': 1,
                'Strength': 5,
                'Ability': 'Some_Ability',
                'Type': 'Some_Type',
                'Placement': 1,
                'Count': 2,
                'Faction': 'Northern Realms'
            },
            ... (More cards)
        ],
        ... (More factions)
    }
    """

    with open(file_path, 'r') as f:
        data_read = f.read().splitlines()

    result = {}
    current_group = None

    for line in data_read:
        if line == '':
            continue

        if 'Northern Realms' in line or 'Scoiatael' in line or 'Neutral' in line or 'Nilfgaard' in line or 'Monsters' \
                in line:
            current_group = line.strip(',')
            result[current_group] = []
            continue

        name, _id, strength, ability, card_type, placement, count, image, empty = line.split(',')

        if name == 'Name':
            continue

        result[current_group].append({
            'Name': name,
            'Id': int(_id),
            'Strength': int(strength),
            'Ability': ability,
            'Type': card_type,
            'Placement': int(placement),
            'Count': int(count),
            'Faction': current_group
        })

    return result


class ActionChooser():
    def choose_action_AI(self, game, agent):
        bool_actions, actions = game.valid_actions()
        obs = torch.from_numpy(np.array(game.game_state(), dtype=np.int64))
        expanded_tensor = obs.unsqueeze(0)
        final_tensor = expanded_tensor.repeat(16, 1, 1)
        action = agent.choose_action(final_tensor, torch.BoolTensor(bool_actions))
        if action == 462:
            action = -1
        return action


def write_to_file(log, filename):
    f = open(filename, "w")
    f.write(log)
    f.close()
