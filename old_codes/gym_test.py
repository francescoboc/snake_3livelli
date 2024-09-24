import gymnasium as gym
import matplotlib.pyplot as plt
from custom_env import *

from stable_baselines3 import A2C
from stable_baselines3 import DQN

from stable_baselines3.common.env_checker import check_env

# in case we need to reload the library
from importlib import reload
reload(sys.modules['custom_env'])
from custom_env import *

# env = gym.make("CartPole-v1", render_mode="rgb_array")
env = SnakeEnv()

# check_env(env, warn=True)

# model = A2C("CnnPolicy", env, verbose=1)
model = A2C("MlpPolicy", env, verbose=1)
# model = DQN("CnnPolicy", env, verbose=1)
# model = DQN("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=500000)

vec_env = model.get_env()

print('done')

obs = vec_env.reset()
# obs = env.reset()
img = plt.imshow(obs[0][0])
for i in range(1000):
    action = vec_env.action_space.sample()
    obs, reward, done, info = vec_env.step([action])
    # frame = vec_env.render()
    img.set_data(obs[0][0])
    plt.pause(0.1)

    # action = env.action_space.sample()
    # observation, reward, terminated, truncated, info = env.step(action)
    # frame = env.render()

    # print(observation)
    # print(reward, terminated)
    # print()

    # plt.clf()
    # plt.imshow(frame)
    # plt.title(i)
    # plt.pause(0.001)

    if done:
        obs = vec_env.reset()

plt.show()
