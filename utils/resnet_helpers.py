from keras.layers import *
from keras.regularizers import l2

# The original help functions from keras does not have weight regularizers, so I modified them.
# Also, I changed these two functions into functional style
def identity_block(kernel_size, filters, stage, block, weight_decay=0.):
    '''The identity_block is the block that has no conv layer at shortcut
    # Arguments
        kernel_size: defualt 3, the kernel size of middle conv layer at main path
        filters: list of integers, the nb_filters of 3 conv layer at main path
        stage: integer, current stage label, used for generating layer names
        block: 'a','b'..., current block label, used for generating layer names
    '''
    def f(input_tensor):
        nb_filter1, nb_filter2, nb_filter3 = filters
        if K.image_dim_ordering() == 'tf':
            bn_axis = 3
        else:
            bn_axis = 1
        conv_name_base = 'res' + str(stage) + block + '_branch'
        bn_name_base = 'bn' + str(stage) + block + '_branch'

        x = Convolution2D(nb_filter1, 1, 1, name=conv_name_base + '2a', W_regularizer=l2(weight_decay))(input_tensor)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2a')(x)
        x = Activation('relu')(x)

        x = Convolution2D(nb_filter2, kernel_size, kernel_size,
                          border_mode='same', name=conv_name_base + '2b', W_regularizer=l2(weight_decay))(x)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2b')(x)
        x = Activation('relu')(x)

        x = Convolution2D(nb_filter3, 1, 1, name=conv_name_base + '2c', W_regularizer=l2(weight_decay))(x)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2c')(x)

        x = merge([x, input_tensor], mode='sum')
        x = Activation('relu')(x)
        return x
    return f

def conv_block(kernel_size, filters, stage, block, weight_decay=0., strides=(2, 2)):
    '''conv_block is the block that has a conv layer at shortcut
    # Arguments
        kernel_size: defualt 3, the kernel size of middle conv layer at main path
        filters: list of integers, the nb_filters of 3 conv layer at main path
        stage: integer, current stage label, used for generating layer names
        block: 'a','b'..., current block label, used for generating layer names
    Note that from stage 3, the first conv layer at main path is with subsample=(2,2)
    And the shortcut should have subsample=(2,2) as well
    '''
    def f(input_tensor):
        nb_filter1, nb_filter2, nb_filter3 = filters
        if K.image_dim_ordering() == 'tf':
            bn_axis = 3
        else:
            bn_axis = 1
        conv_name_base = 'res' + str(stage) + block + '_branch'
        bn_name_base = 'bn' + str(stage) + block + '_branch'

        x = Convolution2D(nb_filter1, 1, 1, subsample=strides,
                          name=conv_name_base + '2a', W_regularizer=l2(weight_decay))(input_tensor)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2a')(x)
        x = Activation('relu')(x)

        x = Convolution2D(nb_filter2, kernel_size, kernel_size, border_mode='same',
                          name=conv_name_base + '2b', W_regularizer=l2(weight_decay))(x)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2b')(x)
        x = Activation('relu')(x)

        x = Convolution2D(nb_filter3, 1, 1, name=conv_name_base + '2c', W_regularizer=l2(weight_decay))(x)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2c')(x)

        shortcut = Convolution2D(nb_filter3, 1, 1, subsample=strides,
                                 name=conv_name_base + '1', W_regularizer=l2(weight_decay))(input_tensor)
        shortcut = BatchNormalization(axis=bn_axis, name=bn_name_base + '1')(shortcut)

        x = merge([x, shortcut], mode='sum')
        x = Activation('relu')(x)
        return x
    return f

# Atrous-Convolution version of residual blocks
def atrous_identity_block(kernel_size, filters, stage, block, weight_decay=0.):
    '''The identity_block is the block that has no conv layer at shortcut
    # Arguments
        kernel_size: defualt 3, the kernel size of middle conv layer at main path
        filters: list of integers, the nb_filters of 3 conv layer at main path
        stage: integer, current stage label, used for generating layer names
        block: 'a','b'..., current block label, used for generating layer names
    '''
    def f(input_tensor):
        nb_filter1, nb_filter2, nb_filter3 = filters
        if K.image_dim_ordering() == 'tf':
            bn_axis = 3
        else:
            bn_axis = 1
        conv_name_base = 'res' + str(stage) + block + '_branch'
        bn_name_base = 'bn' + str(stage) + block + '_branch'

        x = Convolution2D(nb_filter1, 1, 1, name=conv_name_base + '2a', W_regularizer=l2(weight_decay))(input_tensor)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2a')(x)
        x = Activation('relu')(x)

        x = AtrousConvolution2D(nb_filter2, kernel_size, kernel_size, atrous_rate=(2, 2),
                          border_mode='same', name=conv_name_base + '2b', W_regularizer=l2(weight_decay))(x)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2b')(x)
        x = Activation('relu')(x)

        x = Convolution2D(nb_filter3, 1, 1, name=conv_name_base + '2c', W_regularizer=l2(weight_decay))(x)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2c')(x)

        x = merge([x, input_tensor], mode='sum')
        x = Activation('relu')(x)
        return x
    return f

def atrous_conv_block(kernel_size, filters, stage, block, weight_decay=0., strides=(1, 1)):
    '''conv_block is the block that has a conv layer at shortcut
    # Arguments
        kernel_size: defualt 3, the kernel size of middle conv layer at main path
        filters: list of integers, the nb_filters of 3 conv layer at main path
        stage: integer, current stage label, used for generating layer names
        block: 'a','b'..., current block label, used for generating layer names
    '''
    def f(input_tensor):
        nb_filter1, nb_filter2, nb_filter3 = filters
        if K.image_dim_ordering() == 'tf':
            bn_axis = 3
        else:
            bn_axis = 1
        conv_name_base = 'res' + str(stage) + block + '_branch'
        bn_name_base = 'bn' + str(stage) + block + '_branch'

        x = Convolution2D(nb_filter1, 1, 1, subsample=strides,
                          name=conv_name_base + '2a', W_regularizer=l2(weight_decay))(input_tensor)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2a')(x)
        x = Activation('relu')(x)

        x = AtrousConvolution2D(nb_filter2, kernel_size, kernel_size, border_mode='same', atrous_rate=(2, 2),
                          name=conv_name_base + '2b', W_regularizer=l2(weight_decay))(x)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2b')(x)
        x = Activation('relu')(x)

        x = Convolution2D(nb_filter3, 1, 1, name=conv_name_base + '2c', W_regularizer=l2(weight_decay))(x)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2c')(x)

        shortcut = Convolution2D(nb_filter3, 1, 1, subsample=strides,
                                 name=conv_name_base + '1', W_regularizer=l2(weight_decay))(input_tensor)
        shortcut = BatchNormalization(axis=bn_axis, name=bn_name_base + '1')(shortcut)

        x = merge([x, shortcut], mode='sum')
        x = Activation('relu')(x)
        return x
    return f
