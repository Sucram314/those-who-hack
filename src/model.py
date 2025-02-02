from collections.abc import Callable

import numpy as np

def ReLU(x : np.ndarray) -> np.ndarray:
    return np.maximum(0, x)

def dReLU(x : np.ndarray) -> np.ndarray:
    return (x > 0)

def normalize(x : np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x,axis=0)

def softmax(x : np.ndarray) -> np.ndarray:
    exp = np.exp(x)
    return exp / np.sum(exp, 0)

class Data:
    def __init__(self, input : np.ndarray = None, output : np.ndarray = None, labels : np.ndarray = None):
        self.input = input
        self.output = output
        self.labels = labels

    def add_example(self, input : np.ndarray, output : np.ndarray, label : np.ndarray):
        if self.input is None: 
            self.input = input
        else:
            self.input = np.append(self.input.T, input.T, axis=0).T
        
        if self.output is None:
            self.output = output
        else:
            self.output = np.append(self.output.T, output.T, axis=0).T

        if self.labels is None:
            self.labels = np.array([label])
        else:
            self.labels = np.append(self.labels,[label])

        if self.input.shape[1] % 10 == 0:
            print(self.input.shape[1], "examples")

class Model:
    def __init__(self, 
                 data : Data,
                 layers : np.ndarray, 
                 activation : Callable[[np.ndarray],np.ndarray] = ReLU, 
                 activation_derivative : Callable[[np.ndarray],np.ndarray] = dReLU, 
                 final_activation : Callable[[np.ndarray],np.ndarray] = softmax) -> None:

        self.data = data
        
        self.nlayers = layers.size
        self.layers = layers

        self.activation = activation
        self.activation_derivative = activation_derivative
        self.final_activation = final_activation

        self.weights : list[np.ndarray] = []
        self.biases : list[np.ndarray]  = []

        for i in range(1, self.nlayers):
            pre = self.layers[i-1]
            cur = self.layers[i]

            self.weights.append(np.random.randn(cur,pre))
            self.biases.append(np.random.randn(cur,1)) 

        self.iteration = 0           

    def forward_propagate(self, input_layer : np.ndarray) -> tuple[list[np.ndarray],list[np.ndarray]]:
        result : np.ndarray = input_layer

        layers = [input_layer]
        activated = [input_layer]

        for i in range(self.nlayers - 1):
            result = self.weights[i].dot(result) + self.biases[i]
            layers.append(result)

            if i == self.nlayers - 2:
                result = self.final_activation(result)
            else:
                result = self.activation(result)

            activated.append(result)

        return layers, activated
    
    def backward_propagate(self, layers : list[np.ndarray], activated : list[np.ndarray], target : np.ndarray) -> tuple[list[np.ndarray],list[np.ndarray]]:
        num_examples = target.shape[1]

        dweights = []
        dbiases = []

        dcurrent = activated[-1] - target
        dweights.append(1 / num_examples * dcurrent.dot(activated[-2].T))
        dbiases.append(1 / num_examples * np.sum(dcurrent,1,keepdims=1))

        for i in range(self.nlayers - 2, 0, -1):
            dcurrent = self.weights[i].T.dot(dcurrent) * self.activation_derivative(layers[i])
            dweights.append(1 / num_examples * dcurrent.dot(activated[i-1].T))
            dbiases.append(1 / num_examples * np.sum(dcurrent,1,keepdims=1))

        return dweights, dbiases

    def update_parameters(self, dweights, dbiases, alpha=0.1) -> None:
        for i in range(self.nlayers - 1):
            self.weights[i] -= dweights[-i-1] * alpha
            self.biases[i] -= dbiases[-i-1] * alpha

        self.iteration += 1

    def predict(self, input_layer : np.ndarray) -> np.ndarray:
        current : np.ndarray = input_layer

        for i in range(self.nlayers - 1):
            current =  self.weights[i].dot(current) + self.biases[i]

            if i == self.nlayers - 2:
                current = self.final_activation(current)
            else:
                current = self.activation(current)

        return np.argmax(current,0)
    
    def evaluate(self):
        print(f"Iteration {self.iteration}")

        predictions = self.predict(self.data.input)
        self.accuracy = np.sum(predictions == self.data.labels) / self.data.labels.size
        
        print(f"Accuracy: {self.accuracy:%}")

        print()

    def train(self, alpha=0.05):
        layers, activated = self.forward_propagate(self.data.input)
        dweights, dbiases = self.backward_propagate(layers, activated, self.data.output)
        self.update_parameters(dweights, dbiases, alpha)

        if self.iteration % 10 == 0:
            self.evaluate()
    
class Aimer(Model):
    def __init__(self,data,resolution):
        super().__init__(data,np.array([resolution**2, 32, 20, 16]))

class Selector(Model):
    def __init__(self,data,resolution):
        super().__init__(data,np.array([resolution**2, 16, 10, 2]))
