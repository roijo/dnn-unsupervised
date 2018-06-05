import torch
import torch.nn as nn

from dnn_pytorch.util.layer import Flatten, PrintLayer
from dnn_pytorch.base.constants.config import Config
from dnn_pytorch.base.utils.log_error import initialize_logger


class ConvNet(nn.Module):
    imsize = None
    n_colors = None
    num_classes = None

    def __init__(self, num_classes, imsize, n_colors, config=None):
        super(ConvNet, self).__init__()

        self.config = config or Config()
        self.logger = initialize_logger(
            self.__class__.__name__,
            self.config.out.FOLDER_LOGS)

        self.num_classes = num_classes
        self.n_colors = n_colors
        self.imsize = imsize

        # initialize a dropout layer
        self.dropout = nn.Dropout(p=0.5)

    def buildcnn(self):
        # VGG params
        n_layers = (4, 2, 1)
        poolsize = 2
        n_filters = 32
        filter_size = 3
        cnn = self._buildvgg(n_layers, poolsize, n_filters, filter_size)
        return cnn

    def buildoutput(self):
        n_size = self._get_conv_output(
            (self.n_colors, self.imsize, self.imsize))
        # create the output linear classification layers
        self.out = nn.Sequential()
        fc = nn.Linear(n_size, 512)
        self.out.add_module('fc', fc)
        self.out.add_module('dropout', self.dropout)
        fc2 = nn.Linear(512, self.num_classes)
        self.out.add_module('fc2', fc2)
        self.out.add_module('dropout', self.dropout)

    # generate input sample and forward to get shape
    def _get_conv_output(self, shape):
        bs = 1
        input = torch.autograd.Variable(torch.rand(bs, *shape))
        output_feat = self._forward_features(input)
        n_size = output_feat.data.view(bs, -1).size(1)
        return n_size

    def _buildvgg(self, n_layers=(4, 2, 1), poolsize=2,
                  n_filters=32, filter_size=3):
        '''
        Model function for building up the VGG style CNN.

        To Do:
        - Consider switching code layout to:

            layers = []
            layers.append(nn.Linear(3, 4))
            layers.append(nn.Sigmoid())
            layers.append(nn.Linear(4, 1))
            layers.append(nn.Sigmoid())

            net = nn.Sequential(*layers)

        '''
        self.net = nn.Sequential()

        # create the vgg-style convolutional layers w/ batch norm followed with
        # max-pooling
        for idx, n_layer in enumerate(n_layers):
            for ilay in range(n_layer):
                if idx == 0 and ilay == 0:
                    indim = self.n_colors
                else:
                    indim = prevfilter
                # keep track of the previous size filter
                prevfilter = n_filters * (2**idx)
                conv = nn.Conv2d(in_channels=indim,                         # input height
                                 out_channels=n_filters * \
                                 (2**idx),        # n_filters to use
                                 kernel_size=filter_size,                # filter size
                                 stride=1, padding=2)                    # filter step, padding
                # apply Glorot/xavier uniform init
                torch.nn.init.xavier_uniform_(conv.weight)
                self.net.add_module('conv{}_{}'.format(idx, ilay), conv)
                self.net.add_module(
                    'norm{}_{}'.format(
                        idx, ilay), nn.BatchNorm2d(
                        num_features=prevfilter))   # apply batch normalization
                # apply relu activation
                self.net.add_module(
                    'activate{}_{}'.format(
                        idx, ilay), nn.ReLU())
            self.net.add_module(
                'pool{}'.format(idx),
                nn.MaxPool2d(
                    kernel_size=poolsize,
                    stride=poolsize))  # choose max value in poolsize area
        return self.net

    def _forward_features(self, x):
        x = self.net(x)
        x = x.view(x.size(0), -1)  # to get the intermediate output
        return x

    def forward(self, x):
        output = None
        x = self._forward_features(x)
        output = self.out(x)
        return output, x


if __name__ == '__main__':
    from torchsummary import summary
    # Device configuration
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    cnn = ConvNet()

    # SUMMARIZE WEIGHTS IN EACH LAYER
    # for i, weights in enumerate(list(cnn.parameters())):
    #     print('i:',i,'weights:',weights.size())

    # PRINT FINAL OUTPUT USING A VARIABLE RUN THROUGH THE NETWORK
    expected_image_shape = (4, 64, 64)
    input_tensor = torch.autograd.Variable(
        torch.rand(1, *expected_image_shape))
    # this call will invoke all registered forward hooks
    output_tensor, x = cnn(input_tensor)
    print("X shape: ", x.shape)
    # print(output_tensor.shape)
    print(cnn)

    # SUMMARIZE NETWORK USING KERAS STYLE SUMMARY
    summary(cnn, (4, 28, 28))
