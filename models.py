import tensorflow as tf
from tensorflow.keras import layers

def FSRCNN(input_shape, upscale):
    '''FSRCNN model
    :param input_shape: 3-tuple representing the image shape
    :param upscale: upscale factor
    '''

    # Attributes
    d = 48 # LR feature dimension
    s = 16 # Number of shrinking filters
    m = 4 # Mapping depth

    # Create model
    model = tf.keras.models.Sequential()

    # Feature extraction
    model.add(layers.Conv2D(
        input_shape = input_shape,
        filters = d,
        kernel_size = 5,
        padding = "same",
        data_format = "channels_last",
        activation = None, # PReLU defined after
        use_bias = True,
        kernel_initializer = tf.keras.initializers.VarianceScaling(0.01),
    ))
    model.add(layers.PReLU(shared_axes=[1, 2]))

    # Shrinking
    model.add(layers.Conv2D(
        filters = s,
        kernel_size = 1,
        padding = "same",
        data_format = "channels_last",
        activation = None, # PReLU defined after
        use_bias = True,
        kernel_initializer = tf.keras.initializers.VarianceScaling(2),
    ))
    model.add(layers.PReLU(shared_axes=[1, 2]))

    # Mapping
    for _ in range(m):
        model.add(layers.Conv2D(
            filters = s,
            kernel_size = 3,
            padding = "same",
            data_format = "channels_last",
            activation = None, # PReLU defined after
            use_bias = True,
            kernel_initializer = tf.keras.initializers.VarianceScaling(2),
        ))
        model.add(layers.PReLU(shared_axes=[1, 2]))

    # Expanding
    model.add(layers.Conv2D(
        filters = d,
        kernel_size = 1,
        padding = "same",
        data_format = "channels_last",
        activation = None, # PReLU defined after
        use_bias = True,
        kernel_initializer = tf.keras.initializers.VarianceScaling(2),
    ))
    model.add(layers.PReLU(shared_axes=[1, 2]))

    # Deconvolution
    model.add(layers.Conv2DTranspose(
        filters = 1,
        kernel_size = 9,
        strides = upscale,
        padding = "same",
        data_format = "channels_last",
        activation = None,
        use_bias = True,
        kernel_initializer = tf.keras.initializers.RandomNormal(mean=0.0, stddev=0.001),
    ))

    return model


def IRCNN(input_shape):
    '''IRCNN model
    :param input_shape: 3-tuple representing the image shape
    '''
    # Attributes
    kernel_weight_decay = 1e-4
    dilation_rate = [1, 2, 3, 4, 3, 2, 1]

    # Create model
    model = tf.keras.models.Sequential()

    # First layer
    model.add(layers.Conv2D(
            input_shape=input_shape,
            filters=64,
            kernel_size=[3, 3], 
            strides = 1,
            padding = 'same',
            data_format = "channels_last",
            dilation_rate = dilation_rate[0],
            activation = tf.nn.relu,
            kernel_initializer = tf.keras.initializers.glorot_uniform(),
            kernel_regularizer = tf.keras.regularizers.l2(kernel_weight_decay)
    ))

    # Middle layers
    for i in range(2, 7):
        model.add(layers.Conv2D(
            filters=64,
            kernel_size=[3, 3],
            strides = 1,
            padding = 'same',
            data_format = "channels_last",
            dilation_rate = dilation_rate[i-1],
            activation = None,
            kernel_initializer = tf.keras.initializers.glorot_uniform(),
            kernel_regularizer = tf.keras.regularizers.l2(kernel_weight_decay)
        ))
        model.add(layers.BatchNormalization())
        model.add(layers.Activation(tf.nn.relu))


    # Last layer
    model.add(layers.Conv2D(
            filters=3,
            kernel_size=[3, 3],
            strides = 1,
            padding = 'same',
            data_format = "channels_last",
            dilation_rate = dilation_rate[-1],
            activation = None,
            kernel_initializer = tf.keras.initializers.glorot_uniform(),
            kernel_regularizer = tf.keras.regularizers.l2(kernel_weight_decay)
    ))

    return model
