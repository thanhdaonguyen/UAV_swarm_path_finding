import torch
from torch import nn
import numpy
from .utils import *

import torch.nn.functional as F

class DoubleConv(nn.Module):
    """Two convolutional layers followed by ReLU (without changing size)"""
    def __init__(self, in_channels, out_channels):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)


class Model(nn.Module):
    def __init__(self, in_channels=1, out_channels=1, metadata_dim=18):
        super(Model, self).__init__()

        # Encoder (Downsampling path)
        self.down1 = DoubleConv(in_channels, 64)
        self.pool1 = nn.MaxPool2d(2)

        self.down2 = DoubleConv(64, 128)
        self.pool2 = nn.MaxPool2d(2)

        self.down3 = DoubleConv(128, 256)
        self.pool3 = nn.MaxPool2d(2)

        # self.down4 = DoubleConv(256, 512)
        # self.pool4 = nn.MaxPool2d(2)

        # Bottleneck
        self.bottleneck = DoubleConv(256, 512)

        # Metadata Fully Connected Layer
        self.metadata_fc = nn.Sequential(
            nn.Linear(metadata_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512)  # Same size as bottleneck features
        )

        # # Decoder (Upsampling path)
        # self.up4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        # self.dec4 = DoubleConv(1024, 512)

        self.up3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = DoubleConv(512, 256)

        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = DoubleConv(256, 128)

        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = DoubleConv(128, 64)

        # Final output layer
        self.out_conv = nn.Conv2d(64, out_channels, kernel_size=1)  # 1x1 Conv to match output channels

    def forward(self, image_input, metadata_input):
        # Encoder
        image_input = image_input.unsqueeze(1)
        #print(image_input.size(), metadata_input.size())
        image_input = image_input
        metadata_input = metadata_input
        d1 = self.down1(image_input)
        p1 = self.pool1(d1)

        d2 = self.down2(p1)
        p2 = self.pool2(d2)

        d3 = self.down3(p2)
        p3 = self.pool3(d3)

        # d4 = self.down4(p3)
        # p4 = self.pool4(d4)

        # Bottleneck
        bottleneck = self.bottleneck(p3)  # Shape: (batch, 1024, H/16, W/16)

        # Process metadata
        metadata_features = self.metadata_fc(metadata_input)  # Shape: (batch, 1024)
        metadata_features = metadata_features.view(metadata_features.shape[0], 512, 1, 1)  # Reshape to match bottleneck
        #print(bottleneck.size(), metadata_features.size())
        # Combine metadata with bottleneck features
        bottleneck = bottleneck + metadata_features  # Element-wise addition

        #print(bottleneck.size())

        # Decoder
        # u4 = self.up4(bottleneck)

        # #print(u4.size(), d4.size())
        # u4 = F.interpolate(u4, size=d4.shape[2:], mode="bilinear", align_corners=True)
        # u4 = torch.cat([u4, d4], dim=1)
        # d4 = self.dec4(u4)

        # u3 = self.up3(d4)
        u3 = self.up3(bottleneck)
        u3 = F.interpolate(u3, size=d3.shape[2:], mode="bilinear", align_corners=True)
        u3 = torch.cat([u3, d3], dim=1)
        d3 = self.dec3(u3)

        u2 = self.up2(d3)
        u2 = F.interpolate(u2, size=d2.shape[2:], mode="bilinear", align_corners=True)
        u2 = torch.cat([u2, d2], dim=1)
        d2 = self.dec2(u2)

        u1 = self.up1(d2)
        u1 = F.interpolate(u1, size=d1.shape[2:], mode="bilinear", align_corners=True)
        u1 = torch.cat([u1, d1], dim=1)
        d1 = self.dec1(u1)

        # Output Layer
        out = self.out_conv(d1)
        out = out[:, 0, :, :]
        #print(out.size())
        return out

class Agent:
  def __init__(self, swarm):
    self.possible_move_map = None
    self.possible_move_map_tensor = None
    self.state = None
    self.trainModel = Model(metadata_dim=len(swarm.uavs) * 2 + 1).to(device)
    self.targetModel =  Model(metadata_dim=len(swarm.uavs) * 2 + 1).to(device)
    self.targetModel.load_state_dict(self.trainModel.state_dict())

    self.optimizer = torch.optim.Adam(self.trainModel.parameters(), lr=1e-4)
    self.loss = nn.MSELoss()
    self.gamma = 0.8
    self.relay_memory = ReplayMemory(64 * 64)
    self.batch_size = 16
    self.updateTargetThreshold = 5
    self.updateTargetCount = 0

  def check_terminal(self):
    return sum(sum(self.possible_move_map,[])) == 0
  
  def iter(self, previousState, action, reward, final_point):
    terminal = 0 if self.check_terminal() else 1
    state = previousState
    newState = self.state
    reward = reward + (1 - terminal) * final_point * 10
    #print(state[0], state[1])
    self.relay_memory.push(state[0], state[1], action, newState[0], newState[1], reward, terminal)
    #print(self.relay_memory.sample(self.batch_size))
    samples = self.relay_memory.sample(self.batch_size)
    samples = Transition(*zip(*samples))

    # Preprocessing input
    #print(samples[0], samples[1])
    state_map = torch.tensor(samples[0], dtype = torch.float32, device = device)
    state_pos = torch.tensor(samples[1], dtype = torch.float32, device = device)
    action = torch.tensor(samples[2], dtype = torch.long, device = device)
    newState_map = torch.tensor(samples[3], dtype = torch.float32, device = device)
    newState_pos = torch.tensor(samples[4], dtype = torch.float32, device = device)
    reward = torch.tensor(samples[5], dtype = torch.float32, device = device)
    terminal = torch.tensor(samples[6], dtype = torch.float32, device = device)
    #print(state_map.size(), state_pos.size(), torch.arange(0, action.size(0) - 1))
    
    # Update train model using target model
    Q_newState_best_value = torch.max(self.targetModel(newState_map, newState_pos))
    Q_target = reward + self.gamma * Q_newState_best_value * terminal
    Q_train = self.trainModel(state_map, state_pos)[(torch.arange(0, action.size(0)), action[:, 0], action[:, 1])]
    loss = self.loss(Q_target, Q_train)
    self.optimizer.zero_grad()
    loss.backward()
    self.optimizer.step()

    # Update target model after some batch
    self.updateTargetCount += 1
    if(self.updateTargetCount % self.updateTargetThreshold == 0):
      self.copy_model()
    return loss.item(), self.state
  
  def decide_action(self):
    # Predict action from recent state
    state_map = torch.tensor(self.state[0], dtype = torch.float32, device = device).unsqueeze(0)
    state_pos = torch.tensor(self.state[1], dtype = torch.float32, device = device).unsqueeze(0)
    
    q_value = self.targetModel(state_map, state_pos)[0]
    q_value = q_value * self.possible_move_map_tensor
    action = (q_value==torch.max(q_value)).nonzero()[0].squeeze()
    return (action[0].item(), action[1].item())
  
  def set_state(self, swarm, uav_index):
    self.state = get_state(swarm, uav_index, self.possible_move_map)
  def create_possible_map(self, map, radius):
    self.possible_move_map = create_possible_move_map(map, radius)
    self.possible_move_map_tensor = torch.tensor(self.possible_move_map,  dtype = torch.float32, device = device)
  def exploration(self, epsilon = 0.9):
    # This function try to decide whether using model to take action or just choose randomly
    # state: state_map, recent_cell_uav
    # reward: priority / time, the last = 1 / reward_point
    # action: state_map (valid move is checked in decideAction, algorithm: find circle of next point uav -> find the max distance from the circle) 
    def choice():
      possible_move = []
      for x in range(len(self.possible_move_map)):
        for y in range(len(self.possible_move_map[0])):
          if self.possible_move_map[x][y] == 1:
            possible_move.append((x, y))
      #print(self.possible_move_map_tensor[0][0])
      if len(possible_move) == 0:
        return 1
      return random.choice(possible_move)
      
    rand = random.random()
    if(rand < epsilon):     
      return choice()
    else:
      action = self.decide_action()
      if self.possible_move_map[action[0]][action[1]] == 0:
        return choice()
      else:
        return action

  # def printQvalue(self, state):
  #   # Print Q value of targetModel for testing stuffs
  #   if(len(state.shape) > 1):
  #     state = state.flatten()
  #   state = torch.tensor(state, dtype = torch.float32)
  #   print(self.targetModel(state))

  def copy_model(self):
    self.targetModel.load_state_dict(self.trainModel.state_dict())